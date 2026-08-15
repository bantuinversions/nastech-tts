"""Deterministic PCM WAV level analysis for Nastech Compact release verification.

The analyzer only measures decoded PCM. It does not judge intelligibility,
voice identity, emotion, or model quality; those require human or dedicated
model evaluation. Its purpose is to prevent malformed, silent, clipped, or
wrong-format WAV assets from being released as local synthesis evidence.
"""

from __future__ import annotations

import io
import math
import struct
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PCM16_FULL_SCALE = 32767
REQUIRED_SAMPLE_RATE = 44100


class AudioLevelError(ValueError):
    """Raised when audio cannot meet a deterministic WAV-level requirement."""


@dataclass(frozen=True)
class WavLevelReport:
    """Auditable measurements for one decoded mono signed-16-bit PCM WAV."""

    channels: int
    sample_width_bytes: int
    sample_rate_hz: int
    frames: int
    duration_seconds: float
    peak_pcm: int
    peak_dbfs: float | None
    rms_pcm: float
    rms_dbfs: float | None
    dc_offset_pcm: float
    clipped_samples: int

    def as_dict(self) -> dict[str, Any]:
        """Return JSON-safe measurements with deliberate display rounding."""
        return {
            "format": "mono-16-bit-pcm-wav",
            "channels": self.channels,
            "sample_width_bytes": self.sample_width_bytes,
            "sample_rate_hz": self.sample_rate_hz,
            "frames": self.frames,
            "duration_seconds": round(self.duration_seconds, 4),
            "peak_pcm": self.peak_pcm,
            "peak_dbfs": None if self.peak_dbfs is None else round(self.peak_dbfs, 4),
            "rms_pcm": round(self.rms_pcm, 4),
            "rms_dbfs": None if self.rms_dbfs is None else round(self.rms_dbfs, 4),
            "dc_offset_pcm": round(self.dc_offset_pcm, 4),
            "clipped_samples": self.clipped_samples,
        }


def _dbfs(amplitude: float) -> float | None:
    if amplitude <= 0:
        return None
    return 20 * math.log10(amplitude / PCM16_FULL_SCALE)


def _decode_pcm16_wav(data: bytes) -> tuple[int, int, int, list[int]]:
    if not data:
        raise AudioLevelError("Audio data is empty.")
    try:
        with wave.open(io.BytesIO(data), "rb") as reader:
            channels = reader.getnchannels()
            sample_width = reader.getsampwidth()
            sample_rate = reader.getframerate()
            compression = reader.getcomptype()
            frame_count = reader.getnframes()
            raw_frames = reader.readframes(frame_count)
    except (EOFError, wave.Error) as exc:
        raise AudioLevelError(f"Audio is not a readable WAV file: {exc}") from exc

    if channels != 1 or sample_width != 2 or compression != "NONE":
        raise AudioLevelError("Level analysis supports mono 16-bit PCM WAV audio only.")
    if sample_rate <= 0:
        raise AudioLevelError("WAV sample rate must be positive.")
    if frame_count == 0:
        raise AudioLevelError("WAV contains no PCM frames.")
    if len(raw_frames) != frame_count * sample_width:
        raise AudioLevelError("WAV PCM frame data is incomplete.")
    return channels, sample_width, sample_rate, list(struct.unpack(f"<{frame_count}h", raw_frames))


def analyze_wav_levels(data: bytes) -> WavLevelReport:
    """Measure a valid mono signed-16-bit PCM WAV deterministically."""
    channels, sample_width, sample_rate, samples = _decode_pcm16_wav(data)
    frames = len(samples)
    peak = max(abs(sample) for sample in samples)
    mean = sum(samples) / frames
    rms = math.sqrt(sum(sample * sample for sample in samples) / frames)
    return WavLevelReport(
        channels=channels,
        sample_width_bytes=sample_width,
        sample_rate_hz=sample_rate,
        frames=frames,
        duration_seconds=frames / sample_rate,
        peak_pcm=peak,
        peak_dbfs=_dbfs(peak),
        rms_pcm=rms,
        rms_dbfs=_dbfs(rms),
        dc_offset_pcm=mean,
        clipped_samples=sum(abs(sample) == PCM16_FULL_SCALE for sample in samples),
    )


def analyze_wav_file(path: Path) -> WavLevelReport:
    """Read and analyze a WAV file without changing its bytes."""
    return analyze_wav_levels(path.read_bytes())


def validate_release_wav(
    data: bytes,
    *,
    expected_sample_rate_hz: int = REQUIRED_SAMPLE_RATE,
    minimum_duration_seconds: float = 0.25,
    maximum_duration_seconds: float = 60.0,
    maximum_peak_dbfs: float = -0.1,
    minimum_rms_dbfs: float = -60.0,
    maximum_abs_dc_offset_pcm: float = 512.0,
) -> WavLevelReport:
    """Apply conservative deterministic release gates and return measurements.

    The bounds verify file integrity and sane digital level only. They do not
    prove linguistic correctness or expressive quality. Release fixtures are
    intentionally cleaned first, so their peak must stay below the clipping
    guard and their DC offset must remain bounded.
    """
    if minimum_duration_seconds <= 0 or maximum_duration_seconds <= minimum_duration_seconds:
        raise AudioLevelError("Release duration bounds must be positive and ordered.")
    report = analyze_wav_levels(data)
    if report.sample_rate_hz != expected_sample_rate_hz:
        raise AudioLevelError(
            f"Expected {expected_sample_rate_hz} Hz WAV, received {report.sample_rate_hz} Hz."
        )
    if not minimum_duration_seconds <= report.duration_seconds <= maximum_duration_seconds:
        raise AudioLevelError(
            "WAV duration must be between "
            f"{minimum_duration_seconds:.2f} and {maximum_duration_seconds:.2f} seconds."
        )
    if report.clipped_samples:
        raise AudioLevelError("WAV contains digital full-scale clipping samples.")
    if report.peak_dbfs is None or report.peak_dbfs > maximum_peak_dbfs:
        raise AudioLevelError("WAV peak exceeds the release clipping guard.")
    if report.rms_dbfs is None or report.rms_dbfs < minimum_rms_dbfs:
        raise AudioLevelError("WAV is silent or below the release audibility floor.")
    if abs(report.dc_offset_pcm) > maximum_abs_dc_offset_pcm:
        raise AudioLevelError("WAV DC offset exceeds the release hygiene bound.")
    return report
