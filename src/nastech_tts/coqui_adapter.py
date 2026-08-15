"""Guarded adapter for an operator-provided Coqui-compatible local command.

Nastech does not bundle this runtime. The operator must install a compatible
Coqui environment, select a reviewed model, and explicitly enable the adapter.
The adapter uses a fixed argv list with ``shell=False`` and never downloads a
model or sends a network request itself.
"""

from __future__ import annotations

import os
import shlex
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .audio_levels import analyze_wav_levels
from .supertonic import CompactAudio, CompactCompiledRequest


class CoquiAdapterError(RuntimeError):
    """Raised when the externally managed Coqui-compatible adapter cannot render."""


@dataclass(frozen=True)
class CoquiCommandSettings:
    """Operator-controlled command settings for a local isolated environment."""

    command: tuple[str, ...]
    model_name: str | None = None
    speaker: str | None = None
    timeout_seconds: int = 180

    @classmethod
    def from_env(cls) -> CoquiCommandSettings | None:
        """Load explicit configuration; return ``None`` while the adapter is disabled."""
        enabled = os.getenv("NASTECH_ENABLE_COQUI_ADAPTER", "0").lower()
        if enabled not in {"1", "true", "yes"}:
            return None
        raw_command = os.getenv("NASTECH_COQUI_TTS_COMMAND", "").strip()
        if not raw_command:
            return None
        command = tuple(shlex.split(raw_command))
        if not command:
            return None
        timeout = int(os.getenv("NASTECH_COQUI_TTS_TIMEOUT_SECONDS", "180"))
        if timeout < 1 or timeout > 900:
            raise CoquiAdapterError("NASTECH_COQUI_TTS_TIMEOUT_SECONDS must be between 1 and 900.")
        return cls(
            command=command,
            model_name=os.getenv("NASTECH_COQUI_TTS_MODEL") or None,
            speaker=os.getenv("NASTECH_COQUI_TTS_SPEAKER") or None,
            timeout_seconds=timeout,
        )


@dataclass(frozen=True)
class CoquiCommandAdapter:
    """Local command adapter compatible with Coqui's documented ``tts`` CLI shape."""

    settings: CoquiCommandSettings

    @classmethod
    def from_env(cls) -> CoquiCommandAdapter | None:
        settings = CoquiCommandSettings.from_env()
        return cls(settings) if settings else None

    def preflight(self) -> dict[str, Any]:
        """Describe local activation without executing the configured command."""
        executable = Path(self.settings.command[0]).expanduser()
        return {
            "configured": True,
            "command_executable": str(executable),
            "executable_exists": executable.exists(),
            "model_name_configured": bool(self.settings.model_name),
            "speaker_configured": bool(self.settings.speaker),
            "network_request_made": False,
            "output_contract": "mono 16-bit PCM WAV at 44100 Hz",
        }

    def synthesize(self, compiled: CompactCompiledRequest) -> CompactAudio:
        """Render one request through a configured local command without a shell."""
        with tempfile.TemporaryDirectory(prefix="nastech-coqui-") as directory:
            output = Path(directory) / "speech.wav"
            command = [*self.settings.command, "--text", compiled.text, "--out_path", str(output)]
            if self.settings.model_name:
                command.extend(["--model_name", self.settings.model_name])
            if self.settings.speaker:
                command.extend(["--speaker_idx", self.settings.speaker])
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
                raise CoquiAdapterError(
                    f"Coqui-compatible command did not complete: {exc}"
                ) from exc
            if completed.returncode:
                message = (
                    completed.stderr.strip()
                    or completed.stdout.strip()
                    or "unknown command failure"
                )
                raise CoquiAdapterError(f"Coqui-compatible command failed: {message[:500]}")
            if not output.is_file():
                raise CoquiAdapterError(
                    "Coqui-compatible command did not create the requested WAV file."
                )
            data = output.read_bytes()
        report = analyze_wav_levels(data)
        if report.sample_rate_hz != 44100:
            raise CoquiAdapterError(
                "Coqui-compatible output must be 44100 Hz before Nastech can deliver it; "
                "perform approved conversion in the external provider environment."
            )
        return CompactAudio(
            data=data,
            content_type="audio/wav",
            duration_seconds=report.duration_seconds,
            sample_rate=report.sample_rate_hz,
        )
