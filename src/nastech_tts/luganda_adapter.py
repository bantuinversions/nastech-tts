"""Optional local adapter for the reviewed OpenBible Luganda VITS provider pack.

Nastech does not download, bundle, or automatically configure the large Luganda
model pack. An operator supplies a local wrapper that has already loaded a named
reviewed model and speaker. The adapter normalizes valid local WAV output to the
public Nastech mono PCM 44.1 kHz delivery contract.
"""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .audio_levels import analyze_wav_levels
from .supertonic import CompactAudio, CompactCompiledRequest

OPENBIBLE_LUGANDA_MODEL = "multilingual-tts/VITS-OpenBible-Luganda"


class LugandaAdapterError(ValueError):
    """Raised when the configured optional Luganda provider cannot render safely."""


@dataclass(frozen=True)
class LugandaCommandSettings:
    """Explicit operator configuration for the optional isolated Luganda runtime."""

    command: tuple[str, ...]
    model_id: str
    speaker: str
    ffmpeg_command: tuple[str, ...]
    timeout_seconds: int

    @classmethod
    def from_env(cls) -> LugandaCommandSettings | None:
        """Return disabled until all explicit Luganda settings are supplied."""
        enabled = os.getenv("NASTECH_ENABLE_LUGANDA_ADAPTER", "0").lower()
        if enabled not in {"1", "true", "yes"}:
            return None
        raw_command = os.getenv("NASTECH_LUGANDA_TTS_COMMAND", "").strip()
        model_id = os.getenv("NASTECH_LUGANDA_TTS_MODEL", "").strip()
        speaker = os.getenv("NASTECH_LUGANDA_TTS_SPEAKER", "").strip()
        if not raw_command or not model_id or not speaker:
            return None
        if model_id != OPENBIBLE_LUGANDA_MODEL:
            raise LugandaAdapterError(
                "NASTECH_LUGANDA_TTS_MODEL must identify the reviewed OpenBible Luganda model."
            )
        command = tuple(shlex.split(raw_command))
        ffmpeg_command = tuple(shlex.split(os.getenv("NASTECH_FFMPEG_COMMAND", "ffmpeg")))
        if not command or not ffmpeg_command:
            return None
        timeout = int(os.getenv("NASTECH_LUGANDA_TTS_TIMEOUT_SECONDS", "300"))
        if timeout < 1 or timeout > 900:
            raise LugandaAdapterError(
                "NASTECH_LUGANDA_TTS_TIMEOUT_SECONDS must be between 1 and 900."
            )
        return cls(command, model_id, speaker, ffmpeg_command, timeout)


@dataclass(frozen=True)
class LugandaCommandAdapter:
    """Fixed-argv wrapper for a locally installed reviewed Luganda VITS pack."""

    settings: LugandaCommandSettings

    @classmethod
    def from_env(cls) -> LugandaCommandAdapter | None:
        settings = LugandaCommandSettings.from_env()
        return cls(settings) if settings else None

    def preflight(self) -> dict[str, Any]:
        """Describe activation requirements without running the local provider."""
        command_path = shutil.which(self.settings.command[0])
        ffmpeg_path = shutil.which(self.settings.ffmpeg_command[0])
        return {
            "configured": True,
            "model_id": self.settings.model_id,
            "model_id_accepted": self.settings.model_id == OPENBIBLE_LUGANDA_MODEL,
            "speaker_configured": bool(self.settings.speaker),
            "command_executable": self.settings.command[0],
            "executable_exists": bool(command_path),
            "normalizer_executable": self.settings.ffmpeg_command[0],
            "normalizer_exists": bool(ffmpeg_path),
            "input_language": "lg",
            "provider_output_contract": (
                "provider-defined WAV, normalized to mono 16-bit PCM at 44100 Hz"
            ),
            "network_request_made": False,
        }

    def synthesize(self, compiled: CompactCompiledRequest) -> CompactAudio:
        """Render plain Luganda through an external local command and normalize the WAV."""
        if "<" in compiled.text or ">" in compiled.text:
            raise LugandaAdapterError(
                "The Luganda VITS adapter currently accepts plain spoken text only; "
                "emotion and sound tags require provider-specific validation."
            )
        with tempfile.TemporaryDirectory(prefix="nastech-luganda-") as directory:
            raw_output = Path(directory) / "provider.wav"
            normalized_output = Path(directory) / "nastech.wav"
            command = [
                *self.settings.command,
                "--text",
                compiled.text,
                "--out_path",
                str(raw_output),
                "--speaker",
                self.settings.speaker,
            ]
            try:
                completed = subprocess.run(
                    command,
                    check=False,
                    shell=False,
                    capture_output=True,
                    text=True,
                    timeout=self.settings.timeout_seconds,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise LugandaAdapterError(f"Luganda local command did not complete: {exc}") from exc
            if completed.returncode:
                message = (
                    completed.stderr.strip()
                    or completed.stdout.strip()
                    or "unknown command failure"
                )
                raise LugandaAdapterError(f"Luganda local command failed: {message[:500]}")
            if not raw_output.is_file():
                raise LugandaAdapterError(
                    "Luganda local command did not create the requested WAV file."
                )
            normalizer = [
                *self.settings.ffmpeg_command,
                "-nostdin",
                "-y",
                "-v",
                "error",
                "-i",
                str(raw_output),
                "-ac",
                "1",
                "-ar",
                "44100",
                "-c:a",
                "pcm_s16le",
                str(normalized_output),
            ]
            try:
                normalized = subprocess.run(
                    normalizer,
                    check=False,
                    shell=False,
                    capture_output=True,
                    text=True,
                    timeout=self.settings.timeout_seconds,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise LugandaAdapterError(
                    f"Luganda WAV normalizer did not complete: {exc}"
                ) from exc
            if normalized.returncode or not normalized_output.is_file():
                message = (
                    normalized.stderr.strip()
                    or normalized.stdout.strip()
                    or "unknown normalizer failure"
                )
                raise LugandaAdapterError(f"Luganda WAV normalizer failed: {message[:500]}")
            data = normalized_output.read_bytes()
        report = analyze_wav_levels(data)
        if report.sample_rate_hz != 44100 or report.channels != 1 or report.sample_width_bytes != 2:
            raise LugandaAdapterError(
                "Normalized Luganda output does not meet the Nastech PCM contract."
            )
        return CompactAudio(
            data=data,
            content_type="audio/wav",
            duration_seconds=report.duration_seconds,
            sample_rate=report.sample_rate_hz,
        )
