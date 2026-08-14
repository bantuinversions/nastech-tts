# Nastech TTS Architecture

## One Model Family

**Nastech TTS v0.2 uses one model family only:** the Apache-2.0 licensed ready-made `canopylabs/orpheus-3b-0.1-ft` English TTS fine-tune. Nastech modifies this base through a future versioned LoRA/QLoRA adapter trained on licensed English expressive-speech recordings.

No weights from Kokoro, Dia, EmotiVoice, Fish Audio, or other TTS projects are merged into the Nastech model. Those projects are not runtime dependencies of Nastech v0.2.

> Nastech’s first owned model artifact will be a small `nastech-voice-en-v1` adapter loaded on top of the selected ready-made Orpheus fine-tune. This is efficient, reversible, and technically valid.

## Runtime Stack

| Layer | Nastech responsibility | Implementation |
|---|---|---|
| Public markup | Portable expressive request syntax | NastechML parser and validator |
| Behavior compiler | Converts markup to typed speech, sound, and pause spans | `nastech_tts.markup` |
| Selected model | Generates all speech and direct supported sounds | `NastechOrpheusEngine` using `orpheus-cpp` for CPU development |
| Audio assembly | Inserts pauses, resamples only if needed, normalizes output | `nastech_tts.mixer` |
| Audit trail | Records model provenance and behavior fidelity | `*.manifest.json` written beside each WAV output |
| Training | Learns new Nastech controls from licensed examples | Planned LoRA/QLoRA adapter workflow |

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

The current base model directly supports the documented sound elements `laugh`, `chuckle`, `sigh`, `cough`, `sniffle`, `groan`, `yawn`, and `gasp`. Generic named emotion control is requested in NastechML today but marked **approximated** until the Nastech LoRA adapter has been trained and evaluated.

## Model Provenance

The Nastech runtime exposes this explicit model identity:

```text
Product model: nastech-voice-en-v1
Base model: canopylabs/orpheus-3b-0.1-ft
License: Apache-2.0
Adaptation: Nastech LoRA/QLoRA adapter (not yet trained)
Language: English
```

## Deployment Modes

| Mode | Intended use | Requirements |
|---|---|---|
| CPU development | Functional local testing and batch rendering | `orpheus-cpp` plus CPU `llama-cpp-python`; slow and memory-intensive |
| GPU inference | Low-latency product inference | NVIDIA GPU, Transformers/vLLM runtime, accepted upstream model access conditions |
| GPU adapter training | Train the Nastech behavior adapter | NVIDIA GPU, accepted upstream access conditions, licensed expressive English dataset |

## References

[1] [Orpheus 3B 0.1 Finetuned model card](https://huggingface.co/canopylabs/orpheus-3b-0.1-ft)

[2] [Orpheus TTS source repository](https://github.com/canopyai/Orpheus-TTS)
