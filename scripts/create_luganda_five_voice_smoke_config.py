from __future__ import annotations

import json
from pathlib import Path

source = Path(
    "/home/ubuntu/nastech-tts/data/common_voice_luganda/experiment_v22_5voice/coqui/config.five-speaker.json"
)
target = source.with_name("config.five-speaker.smoke.json")
data = json.loads(source.read_text(encoding="utf-8"))
data["output_path"] = str(source.parent / "smoke-checkpoints")
data["epochs"] = 1
data["run_eval"] = False
data["test_delay_epochs"] = 999
data["save_step"] = 1
data["print_step"] = 1
data["model_param_stats"] = False
data["batch_size"] = 2
data["eval_batch_size"] = 2
data["datasets"][0]["meta_file_train"] = "metadata.tsv"
target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(target)
