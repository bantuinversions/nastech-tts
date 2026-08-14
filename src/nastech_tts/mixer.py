"""Audio assembly utilities for Nastech TTS."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf

from .types import AudioChunk


def silence(milliseconds: int, sample_rate: int) -> AudioChunk:
    frames = int(sample_rate * milliseconds / 1000)
    return AudioChunk(samples=np.zeros(frames, dtype="float32"), sample_rate=sample_rate)


def _resample_linear(samples: np.ndarray, source_rate: int, target_rate: int) -> np.ndarray:
    if source_rate == target_rate:
        return samples.astype("float32")
    target_length = max(1, round(len(samples) * target_rate / source_rate))
    source_points = np.linspace(0, 1, len(samples), endpoint=False)
    target_points = np.linspace(0, 1, target_length, endpoint=False)
    return np.interp(target_points, source_points, samples).astype("float32")


def join(chunks: list[AudioChunk], sample_rate: int = 24_000) -> np.ndarray:
    if not chunks:
        raise ValueError("No audio chunks were supplied for mixing.")
    normalized = [
        _resample_linear(np.asarray(chunk.samples).reshape(-1), chunk.sample_rate, sample_rate)
        for chunk in chunks
    ]
    audio = np.concatenate(normalized).astype("float32")
    peak = float(np.max(np.abs(audio))) if len(audio) else 0.0
    if peak > 0.98:
        audio *= 0.98 / peak
    return audio


def write_wav(path: Path, chunks: list[AudioChunk], sample_rate: int = 24_000) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), join(chunks, sample_rate=sample_rate), sample_rate)
    return path
