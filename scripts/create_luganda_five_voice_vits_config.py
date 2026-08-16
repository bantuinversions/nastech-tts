"""Create a Coqui VITS experiment config for five Common Voice Luganda speakers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-config", type=Path, required=True)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output-config", type=Path, required=True)
    parser.add_argument("--output-path", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.baseline_config.read_text(encoding="utf-8"))
    config["output_path"] = str(args.output_path)
    config["datasets"] = [
        {
            "formatter": "common_voice",
            "dataset_name": "nastech_luganda_common_voice_v22_five_speakers",
            "path": str(args.dataset_root),
            "meta_file_train": "metadata.tsv",
            "language": "lg",
        }
    ]
    config["eval_split_size"] = 0.1
    config["eval_split_max_size"] = 100
    config["batch_size"] = 2
    config["eval_batch_size"] = 2
    config["run_name"] = "nastech_luganda_vits_common_voice_five_speakers"
    config["model"] = "vits"
    model_args = config.setdefault("model_args", {})
    model_args["use_speaker_embedding"] = True
    model_args["num_speakers"] = 5
    model_args["speaker_embedding_channels"] = 256
    model_args["use_d_vector_file"] = False
    model_args["d_vector_dim"] = 0
    config["num_speakers"] = 5
    config["use_speaker_embedding"] = True
    args.output_config.parent.mkdir(parents=True, exist_ok=True)
    args.output_config.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(args.output_config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
