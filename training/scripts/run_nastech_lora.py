#!/usr/bin/env python3
"""Launch a parameter-efficient Nastech adapter fine-tune on a GPU machine.

This script starts from the ready-made Orpheus fine-tuned model and saves only a
Nastech LoRA adapter. It intentionally refuses to run without CUDA, a supplied
pretokenized dataset, and an explicit accepted upstream model access path.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require_gpu() -> None:
    import torch

    if not torch.cuda.is_available():
        raise SystemExit(
            "Nastech LoRA training requires an NVIDIA CUDA GPU. This CPU-only machine can run "
            "development inference but cannot perform the intended adapter fine-tune."
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Train the Nastech LoRA adapter on the ready-made base fine-tune.")
    parser.add_argument("--config", type=Path, required=True, help="Nastech LoRA JSON configuration.")
    parser.add_argument(
        "--dataset",
        required=True,
        help="Accepted Hugging Face dataset identifier containing pretokenized `input_ids` training records.",
    )
    parser.add_argument(
        "--accept-upstream-terms",
        action="store_true",
        help="Required acknowledgement that the model owner’s access conditions have been accepted.",
    )
    args = parser.parse_args()

    if not args.accept_upstream_terms:
        raise SystemExit("Pass --accept-upstream-terms only after accepting the selected base model’s access conditions.")
    require_gpu()

    from datasets import load_dataset
    from peft import LoraConfig, get_peft_model
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        Trainer,
        TrainingArguments,
    )

    config = load_config(args.config)
    adapter = config["adapter"]
    train_config = config["training"]
    model_id = config["base_model_id"]
    output_dir = Path(config["output_dir"])

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype="auto",
        attn_implementation="flash_attention_2",
    )
    lora_config = LoraConfig(
        r=int(adapter["rank"]),
        lora_alpha=int(adapter["alpha"]),
        lora_dropout=float(adapter["dropout"]),
        target_modules=list(adapter["target_modules"]),
        bias="none",
        task_type="CAUSAL_LM",
        use_rslora=True,
    )
    model = get_peft_model(model, lora_config)

    dataset = load_dataset(args.dataset)
    if "train" not in dataset or "validation" not in dataset:
        raise SystemExit("The pretokenized dataset must include train and validation splits.")
    required_columns = {"input_ids"}
    missing = required_columns - set(dataset["train"].column_names)
    if missing:
        raise SystemExit(f"Pretokenized dataset missing required columns: {sorted(missing)}")

    training_args = TrainingArguments(
        output_dir=str(output_dir),
        run_name=config["run_name"],
        num_train_epochs=float(train_config["epochs"]),
        learning_rate=float(train_config["learning_rate"]),
        per_device_train_batch_size=int(train_config["per_device_train_batch_size"]),
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=int(train_config["gradient_accumulation_steps"]),
        logging_steps=int(train_config["logging_steps"]),
        save_strategy=str(train_config["save_strategy"]),
        eval_strategy=str(train_config["evaluation_strategy"]),
        bf16=bool(train_config["bf16"]),
        gradient_checkpointing=bool(train_config["gradient_checkpointing"]),
        remove_unused_columns=False,
        report_to="none",
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],
    )
    trainer.train()
    output_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    (output_dir / "nastech_adapter_metadata.json").write_text(
        json.dumps(
            {
                "product_model_id": "nastech-voice-en-v1",
                "base_model_id": model_id,
                "adapter_method": adapter["method"],
                "dataset": args.dataset,
                "status": "trained",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Nastech adapter saved to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
