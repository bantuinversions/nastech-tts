# Nastech GPU Training Handoff

## Objective

Train the first small **Nastech behavior LoRA adapter** on top of the ready-made Apache-2.0 `canopylabs/orpheus-3b-0.1-ft` model. The adapter should improve reliable English control of `angry`, `sad`, `laugh`, `cough`, pauses, and related natural vocal behavior without replacing or merging the base model.

## What Is Already Complete

| Asset | Location |
|---|---|
| Single-model runtime | `src/nastech_tts/engines/orpheus.py` |
| Nastech model metadata | `src/nastech_tts/model.py` |
| NastechML behavior contract | `src/nastech_tts/markup.py` |
| Data validator | `training/scripts/validate_manifest.py` |
| JSONL record schema | `training/templates/nastech_training_record.schema.json` |
| QLoRA configuration | `training/configs/nastech_lora.json` |
| GPU LoRA launcher | `training/scripts/run_nastech_lora.py` |
| Behavior fidelity suite | `evaluation/fixtures/behavior_suite.json` |
| Release checks | `release/RELEASE_CHECKLIST.md` |

## GPU Prerequisites

Use a CUDA-enabled Linux environment with sufficient VRAM for a 3B Speech-LLM adapter run, accepted upstream model access conditions, and a private dataset storage location. The dataset must contain consented, licensed, mono English recordings; do not upload consent documents or raw private audio to the code repository.

## Execution Order

First validate the local source manifest:

```bash
python training/scripts/validate_manifest.py /secure/data/nastech_expressive_manifest.jsonl
```

Next, use the upstream Orpheus preprocessing workflow to produce an authorized Hugging Face dataset with `train` and `validation` splits and model-ready `input_ids`. Then launch the Nastech adapter job:

```bash
pip install -e '.[train]'
python training/scripts/run_nastech_lora.py \
  --config training/configs/nastech_lora.json \
  --dataset YOUR_NAMESPACE/nastech-en-expressive-tokenized \
  --accept-upstream-terms
```

The result is an adapter directory, not a replacement copy of the base model. Review its metadata, run behavior and human listening evaluation, create a Nastech model card, and only then publish a `nastech-voice-en-v1` adapter release.

## Current Limitation

This development cloud has no NVIDIA GPU. It successfully verifies CPU inference but cannot perform the intended LoRA/QLoRA training. No unlicensed data or fabricated model checkpoint was used.
