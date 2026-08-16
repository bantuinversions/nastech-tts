from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, "/home/ubuntu/nastech-luganda-runtime")
from TTS.api import TTS  # noqa: E402

run = Path(
    "/home/ubuntu/nastech-tts/data/common_voice_luganda/experiment_v22_5voice/coqui/epoch1-checkpoints/nastech_luganda_vits_common_voice_five_speakers-August-16-2026_01+49PM-0000000"
)
model = TTS(
    model_path=str(run / "best_model_450.pth"),
    config_path=str(run / "config.json"),
    progress_bar=False,
    gpu=False,
)
text = "Nastech etegeka tekinologiya eyamba abantu okwogera Luganda."
out = run / "samples"
out.mkdir(exist_ok=True)
for speaker in ("MCV_F1", "MCV_F2", "MCV_F3", "MCV_M1", "MCV_M2"):
    target = out / f"{speaker}.wav"
    model.tts_to_file(text=text, speaker=speaker, file_path=str(target))
    print(target)
