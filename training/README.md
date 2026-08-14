# Nastech Adapter Training

Nastech trains a small LoRA/QLoRA adapter on top of the ready-made `canopylabs/orpheus-3b-0.1-ft` model. It does **not** pre-train a model from scratch and it does **not** merge weights from other TTS brands.

## Required Inputs

The following are required before training can begin.

| Input | Requirement |
|---|---|
| Upstream access | The responsible account must accept the base model’s access conditions. |
| GPU runtime | NVIDIA CUDA GPU compatible with BF16 / Flash Attention training. |
| Audio | Licensed, consented, mono English recordings, 16 kHz or higher, 0.4–30 seconds per clip. |
| Manifest | JSONL records compliant with `templates/nastech_training_record.schema.json`. |
| Tokenized dataset | A Hugging Face dataset containing `train` and `validation` splits with model-ready `input_ids`. |

No audio files or manifests are bundled with Nastech. This prevents accidental training on unverified or unlicensed voices.

## Step 1: Validate the Local Source Manifest

```bash
python training/scripts/validate_manifest.py /secure/data/nastech_expressive_manifest.jsonl
```

The validator checks English text, speaker-consent identifiers, audio existence, mono audio, sample rate, duration, allowed emotions, allowed sound events, and split composition.

## Step 2: Build the Pretokenized Dataset

Use the selected upstream Orpheus data-preparation workflow to turn the validated manifest into a private or authorized Hugging Face dataset containing model-ready `input_ids`. Preserve the Nastech prompt protocol in every record:

```text
[nastech:voice=SPEAKER][emotion=EMOTION][intensity=0.00-1.00][events=EVENTS]
TRANSCRIPT
```

Do not train until the dataset has a separate validation split and every training record is traceable to a valid consent record.

## Step 3: Launch the LoRA Job on a GPU

```bash
pip install -e '.[train]'
python training/scripts/run_nastech_lora.py \
  --config training/configs/nastech_lora.json \
  --dataset YOUR_NAMESPACE/nastech-en-expressive-tokenized \
  --accept-upstream-terms
```

The launcher checks CUDA availability, verifies that `train` and `validation` splits exist, applies LoRA to the Llama attention and MLP modules used by the upstream helper, then saves an adapter rather than overwriting the base model.

## Step 4: Evaluate Behavior Control

Run the deterministic behavior-fidelity suite before and after adapter training:

```bash
python evaluation/run_behavior_suite.py evaluation/fixtures/behavior_suite.json
```

Then perform human listening tests using held-out, consented recordings. A Nastech adapter cannot be called production-ready solely because it trains without error. It must demonstrate intelligibility, stable speaker identity, direct laughter/cough rendering, and reliable anger/sadness behavior across a held-out test set.

## Current Cloud Limitation

This cloud can run CPU inference for integration testing. It cannot train the 3B ready-made model or a LoRA adapter because it has no NVIDIA GPU. The files in this directory are a reproducible handoff for the subsequent GPU fine-tune.
