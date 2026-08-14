# Nastech TTS

**Nastech TTS** is an English expressive-speech product built on one ready-made open-source TTS model family: `canopylabs/orpheus-3b-0.1-ft`.

Nastech does **not** train a foundation model from random weights and does **not** merge unrelated model checkpoints. It uses the ready-made Orpheus English fine-tune for inference and prepares a small Nastech LoRA/QLoRA adapter to improve deterministic control of emotions and natural vocal behaviors from licensed English recordings.

## Product Status

| Capability | Status in Nastech v0.2 |
|---|---|
| One selected model family | Complete: Orpheus 3B fine-tuned English model |
| Natural English speech | Working in local CPU development mode |
| Direct laughs, coughs, sighs, gasps, and related documented vocal events | Working through the selected model |
| NastechML behavior markup | Complete |
| Nastech behavior manifest | Complete |
| Deterministic `angry` / `sad` control | Pending Nastech LoRA adapter training on licensed data |
| New Nastech model checkpoint | Pending GPU adapter training |

## Model Provenance

```text
Product model ID: nastech-voice-en-v1
Base model: canopylabs/orpheus-3b-0.1-ft
Base license: Apache-2.0
Language: English
Modification: Nastech LoRA/QLoRA behavior adapter
```

Read [single_model_decision.md](docs/single_model_decision.md) and [adapter_training_strategy.md](docs/adapter_training_strategy.md) before attempting a fine-tuning run.

## Installation

The local runtime uses the official CPU-compatible Orpheus path. Install Nastech and the local runtime in a Python environment:

```bash
pip install 'nastech-tts[local]'
```

For this development checkout:

```bash
cd nastech-tts
pip install -e '.[local]'
```

## Render an Expressive Scene

```bash
nastech-tts status
nastech-tts render examples/expressive_scene.xml --output output/scene.wav
```

Each generated WAV has a companion `*.manifest.json` file containing model provenance, span-by-span behavior fidelity, and warnings. Nastech never labels a named emotion as deterministic until its own adapter has passed evaluation.

## NastechML

```xml
<speak voice="tara">
  <emotion name="angry" intensity="0.80">I asked you not to touch that.</emotion>
  <sound type="cough" />
  <pause ms="250" />
  <emotion name="sad" intensity="0.70">I am sorry that I hurt you.</emotion>
  <sound type="laugh" />
</speak>
```

The current selected base supports these direct vocal event types: `laugh`, `chuckle`, `sigh`, `cough`, `sniffle`, `groan`, `yawn`, and `gasp`.

## Adapter Training

Nastech is designed to train a small adapter on top of the ready-made fine-tuned base model. The training process needs a GPU plus a dataset of consented, licensed English recordings labelled for transcript, speaker, emotion, intensity, and vocal events. See the `training/` directory for the dataset contract, configuration template, and validation commands.

## Product Boundaries

Nastech is a product layer and a future adapter; it does not claim ownership of the upstream Orpheus checkpoint. The upstream model’s source, license, and access conditions continue to apply. See [NOTICE.md](NOTICE.md).

## Development

```bash
python -m unittest discover -s tests -v
```

## References

[1] [Orpheus 3B 0.1 Finetuned model card](https://huggingface.co/canopylabs/orpheus-3b-0.1-ft)

[2] [Orpheus TTS source repository](https://github.com/canopyai/Orpheus-TTS)
