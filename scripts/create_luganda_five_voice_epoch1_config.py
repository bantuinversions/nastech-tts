from __future__ import annotations

import json
from pathlib import Path

root = Path("/home/ubuntu/nastech-tts/data/common_voice_luganda/experiment_v22_5voice/coqui")
source = root / "config.five-speaker.json"
target = root / "config.five-speaker.epoch1.json"
data = json.loads(source.read_text(encoding="utf-8"))
data["output_path"] = str(root / "epoch1-checkpoints")
data["epochs"] = 1
data["run_eval"] = True
data["test_delay_epochs"] = 999
data["save_step"] = 100
data["print_step"] = 50
data["batch_size"] = 2
data["eval_batch_size"] = 2
data["mixed_precision"] = False
data["precision"] = "fp32"
target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(target)
