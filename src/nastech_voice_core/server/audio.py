"""Audio encoding helpers for the local TTS server.

Only formats reachable through ``soundfile`` (libsndfile) at the model's
native 44.1 kHz are supported, so the server adds no extra system
dependencies beyond what the SDK already requires. MP3 / AAC / Opus are
intentionally rejected with a clear error rather than silently emitting
WAV — clients should detect the unsupported format and fall back.

(Opus is excluded for now because libsndfile's OGG/OPUS encoder only
accepts 8/12/16/24/48 kHz, and we'd rather error clearly than ship a
broken format. Re-add it once we have a resampling step.)
"""

from __future__ import annotations

import io
from typing import Optional

import numpy as np
import soundfile as sf

# Mapping from public ``response_format`` value → (soundfile format, subtype, mime).
# Keep this list in sync with ``SUPPORTED_FORMATS`` consumers in ``routes.py``
# and the docs.
_FORMATS = {
    "wav": ("WAV", "PCM_16", "audio/wav"),
    "flac": ("FLAC", "PCM_16", "audio/flac"),
    "ogg": ("OGG", "VORBIS", "audio/ogg"),
}

SUPPORTED_FORMATS = tuple(_FORMATS.keys())


class UnsupportedAudioFormat(ValueError):
    """Raised when the caller asks for a format we cannot encode."""


def format_to_mime(fmt: str) -> str:
    entry = _FORMATS.get(fmt)
    if entry is None:
        raise UnsupportedAudioFormat(fmt)
    return entry[2]


def encode_audio(wav: np.ndarray, sample_rate: int, fmt: str) -> bytes:
    """Encode a synthesized waveform into ``fmt`` bytes.

    Args:
        wav: ndarray of shape ``(1, num_samples)`` or ``(num_samples,)`` —
            the shape produced by :meth:`supertonic.TTS.synthesize`.
        sample_rate: model sample rate (e.g. 44100).
        fmt: one of :data:`SUPPORTED_FORMATS`.
    """
    entry = _FORMATS.get(fmt)
    if entry is None:
        raise UnsupportedAudioFormat(fmt)
    sf_format, subtype, _ = entry

    if wav.ndim == 2:
        # soundfile expects (frames,) or (frames, channels). The pipeline
        # returns (1, num_samples), so squeeze the leading singleton.
        wav = wav.squeeze(0)

    buf = io.BytesIO()
    sf.write(buf, wav, sample_rate, format=sf_format, subtype=subtype)
    return buf.getvalue()


def duration_seconds(wav: np.ndarray, sample_rate: int) -> float:
    return float(wav.shape[-1]) / float(sample_rate)


def coerce_response_format(value: Optional[str]) -> str:
    """Validate and normalize a user-supplied ``response_format``.

    ``None`` → ``"wav"`` (sensible default for local-host integrations). An
    unsupported value raises :class:`UnsupportedAudioFormat` so handlers can
    return a 400 with a stable error code.
    """
    if value is None:
        return "wav"
    v = value.lower().strip()
    if v not in _FORMATS:
        raise UnsupportedAudioFormat(value)
    return v
