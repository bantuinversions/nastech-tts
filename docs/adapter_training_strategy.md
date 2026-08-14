# Nastech Adapter Training Strategy

## Starting Point: a Ready-Made Fine-Tuned Model

Nastech does **not** start from random weights and does not pre-train a foundation model. It starts from the ready-made English `canopylabs/orpheus-3b-0.1-ft` model, which is already a fine-tuned Orpheus Speech-LLM checkpoint built on a Llama 3B family base. The model card is Apache-2.0 and the upstream repository provides an English fine-tuning workflow. [1] [2]

Nastech’s output will be a small **Nastech behavior adapter** on top of that checkpoint. The adapter is the Nastech-owned modification; the base checkpoint remains separately attributed and subject to its upstream access conditions.

## Parameter-Efficient Training Plan

| Stage | Starting artifact | Trainable artifact | Intended outcome |
|---|---|---|---|
| 1. Base | `canopylabs/orpheus-3b-0.1-ft` | None | High-quality English speech, known voice behavior, direct non-speech tags. |
| 2. Nastech behavior LoRA | Ready-made Orpheus fine-tune | Small LoRA/QLoRA adapter | More reliable Nastech control tokens for anger, sadness, laughter, coughs, pauses, whispers, and pacing. |
| 3. Nastech production adapter | Best evaluated behavior adapter | Versioned adapter plus model card | A release candidate that can be loaded with the same base model. |

The training package will use a LoRA/QLoRA configuration rather than full-model updating. This keeps the modification artifact small, versionable, reversible, and clearly separate from the upstream model.

## Nastech Prompt Protocol

The adapter will be trained on a constrained English prompt scheme such as:

```text
[nastech:voice=tara][emotion=angry][intensity=0.82]
I asked you not to touch that.
[nastech:sound=cough]
[nastech:emotion=sad][intensity=0.66]
I am sorry that I hurt you.
[nastech:sound=laugh]
```

During training, each prompt must match a licensed audio file that naturally demonstrates the requested behavior. A token is not considered supported until it has sufficient recorded examples and passes human evaluation.

## Data Rules

All training records must include documented permission for the speaker’s voice and commercial/product training use. Nastech will not train on scraped voices, unauthorized clones, synthetic audio as a substitute for behavior data, or unlabeled emotional recordings.

Each record must include the following: `audio_path`, `transcript`, `speaker_id`, `consent_id`, `emotion`, `intensity`, `behavior_events`, `recording_quality`, and `split`.

## Current Runtime Boundary

The present cloud has no NVIDIA GPU, so it can run the existing Q4 CPU inference model but cannot execute a reliable 3B LoRA/QLoRA training run. Nastech therefore provides the configuration, dataset validator, evaluation harness, and launch contract now. Training begins once a GPU environment and a licensed dataset are supplied.

## References

[1] [Orpheus 3B 0.1 Finetuned model card](https://huggingface.co/canopylabs/orpheus-3b-0.1-ft)

[2] [Orpheus TTS source and fine-tuning workflow](https://github.com/canopyai/Orpheus-TTS)
