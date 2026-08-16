from __future__ import annotations

import json
import math
import sys
import wave
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, "/home/ubuntu/nastech-luganda-runtime")
from transformers import VitsModel, VitsTokenizer, set_seed  # noqa: E402

MODELS = {
    "lg": ("Luganda", "Buli lunaku abantu bakola wamu okukulaakulanya obulamu."),
    "nyn": ("Runyankole", "Abantu bakorera hamwe okugira obusinge."),
    "ach": ("Acholi", "Wang twero tic karacel pi kwo maber."),
    "teo": ("Ateso", "Erai ngesi akwapakina ngesi."),
    "sw": ("Kiswahili", "Watu wanafanya kazi pamoja kwa maisha bora."),
    "rw": ("Kinyarwanda", "Abantu bakorera hamwe kugira ngo babeho neza."),
    "rn": ("Kirundi", "Abantu bakorera hamwe kugira ubuzima bwiza."),
    "ki": ("Gikuyu", "Andu marutaga hamwe nĩguo matũũre wega."),
    "ts": ("Tsonga", "Vanhu va tirha swin’we ku hanya kahle."),
    "sn": ("Shona", "Vanhu vanoshanda pamwe chete kuti vararame zvakanaka."),
    "ny": ("Chichewa", "Anthu amagwira ntchito limodzi kuti akhale ndi moyo wabwino."),
}

ROOT = Path("/home/ubuntu/nastech-bantu-models")
OUT = Path("/home/ubuntu/nastech-tts/release/bantu_mms_fixtures")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def measure(path: Path, sample_rate: int) -> dict[str, float | int]:
    with wave.open(str(path), "rb") as handle:
        values = (
            np.frombuffer(handle.readframes(handle.getnframes()), dtype=np.int16).astype(np.float64)
            / 32768.0
        )
        peak = float(np.max(np.abs(values))) if values.size else 0.0
        rms = float(np.sqrt(np.mean(values * values))) if values.size else 0.0
        return {
            "sample_rate_hz": sample_rate,
            "channels": handle.getnchannels(),
            "duration_s": handle.getnframes() / sample_rate,
            "peak_dbfs": 20 * math.log10(peak) if peak else float("-inf"),
            "rms_dbfs": 20 * math.log10(rms) if rms else float("-inf"),
            "clipped_samples": int(np.count_nonzero(np.abs(values) >= 0.999969482421875)),
        }


OUT.mkdir(parents=True, exist_ok=True)
report = {"device": DEVICE, "voices": {}}
for code, (label, text) in MODELS.items():
    model_dir = ROOT / code
    print(f"loading {code} {label} on {DEVICE}", flush=True)
    tokenizer = VitsTokenizer.from_pretrained(str(model_dir))
    model = VitsModel.from_pretrained(str(model_dir)).to(DEVICE)
    model.eval()
    set_seed(555)
    inputs = tokenizer(text=text, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        waveform = model(**inputs).waveform[0].detach().cpu().numpy()
    waveform = np.clip(waveform, -1.0, 1.0)
    pcm = (waveform * 32767.0).astype(np.int16)
    target = OUT / f"{code}.wav"
    with wave.open(str(target), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(model.config.sampling_rate)
        handle.writeframes(pcm.tobytes())
    report["voices"][code] = {
        "label": label,
        "model": f"facebook/mms-tts-{code if code != 'sw' else 'swh'}",
        "text": text,
        **measure(target, model.config.sampling_rate),
    }
    print(target, report["voices"][code], flush=True)
    del inputs, waveform, pcm, model, tokenizer
    if DEVICE == "cuda":
        torch.cuda.empty_cache()
(OUT / "manifest.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
