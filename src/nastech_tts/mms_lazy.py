"""Lazy local MMS-TTS inference with one-language RAM residency."""

from __future__ import annotations

import io
import threading
import wave
from collections import OrderedDict
from typing import Any

from .hardware import HardwarePlan
from .lazy_packs import ensure_pack, lazy_download_enabled
from .supertonic import CompactAudio

_MODEL_LOCK = threading.RLock()
_MODEL_CACHE: OrderedDict[str, tuple[Any, Any, str]] = OrderedDict()
_MAX_RESIDENT_MODELS = 1


class LazyMMSInferenceError(RuntimeError):
    """Raised when optional MMS inference cannot be completed."""


def _wav_bytes(samples: Any, sample_rate: int) -> bytes:
    import numpy as np

    array = samples.detach().cpu().numpy() if hasattr(samples, "detach") else np.asarray(samples)
    array = np.asarray(array, dtype=np.float32).reshape(-1)
    array = np.nan_to_num(array, nan=0.0, posinf=0.0, neginf=0.0)
    peak = float(np.max(np.abs(array))) if array.size else 0.0
    if peak > 1.0:
        array = array / peak
    pcm = np.clip(array, -1.0, 1.0)
    pcm = (pcm * 32767.0).astype("<i2").tobytes()
    output = io.BytesIO()
    with wave.open(output, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(pcm)
    return output.getvalue()


def _load_model(language: str, path: str, device: str) -> tuple[Any, Any, str]:
    try:
        from transformers import AutoTokenizer, VitsModel
    except ImportError as exc:
        raise LazyMMSInferenceError(
            "transformers is required for lazy MMS inference; install the optional Bantu runtime."
        ) from exc
    tokenizer = AutoTokenizer.from_pretrained(path)
    model = VitsModel.from_pretrained(path)
    model = model.to(device)
    model.eval()
    return tokenizer, model, device


def _resident_model(language: str, path: str, device: str) -> tuple[Any, Any, str]:
    with _MODEL_LOCK:
        current = _MODEL_CACHE.get(language)
        if current is not None and current[2] == device:
            _MODEL_CACHE.move_to_end(language)
            return current
        for key, model in list(_MODEL_CACHE.items()):
            if key != language:
                del _MODEL_CACHE[key]
                try:
                    model[1].to("cpu")
                except Exception:  # noqa: BLE001
                    pass
        loaded = _load_model(language, path, device)
        _MODEL_CACHE[language] = loaded
        return loaded


def clear_resident_models() -> dict[str, Any]:
    with _MODEL_LOCK:
        languages = list(_MODEL_CACHE)
        _MODEL_CACHE.clear()
    return {"cleared_languages": languages, "resident_models": 0}


def resident_languages() -> list[str]:
    with _MODEL_LOCK:
        return list(_MODEL_CACHE)


def synthesize_mms(language: str, text: str) -> CompactAudio:
    """Synthesize one requested language, acquiring and loading only that pack."""
    import torch

    from .lazy_packs import _pack_definitions

    definition = _pack_definitions().get(language)
    if definition is None or not definition.model_id:
        raise LazyMMSInferenceError(f"No verified lazy MMS pack is available for '{language}'.")
    path = ensure_pack(language, allow_download=lazy_download_enabled())
    plan = HardwarePlan.detect()
    device = "cuda" if plan.device == "cuda" and torch.cuda.is_available() else "cpu"
    tokenizer, model, _ = _resident_model(language, str(path), device)
    try:
        inputs = tokenizer(text, return_tensors="pt")
        inputs = {key: value.to(device) for key, value in inputs.items()}
        with torch.no_grad():
            waveform = model(**inputs).waveform
        sample_rate = int(model.config.sampling_rate)
        data = _wav_bytes(waveform, sample_rate)
    except Exception as exc:  # noqa: BLE001
        raise LazyMMSInferenceError(f"MMS inference failed for '{language}': {exc}") from exc
    frame_count = max(0, (len(data) - 44) // 2)
    return CompactAudio(
        data=data,
        content_type="audio/wav",
        duration_seconds=frame_count / sample_rate,
        sample_rate=sample_rate,
    )
