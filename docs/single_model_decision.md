# Nastech Single-Model Decision

## Selected Base Model

**Nastech TTS will be built on the Apache-2.0 licensed `canopylabs/orpheus-3b-0.1-ft` model family.** Nastech will fine-tune this one English Speech-LLM family rather than merge weights from multiple unrelated TTS models.

The selection is deliberate. The official model card lists Apache-2.0 for the model and identifies it as an English, Llama-based TTS model. The official project includes an English fine-tuning workflow, a CPU-compatible `orpheus-cpp` inference route, and direct non-speech tags for laughter, coughing, sighs, sniffles, groans, yawns, gasps, and chuckles. [1] [2]

## Nastech Modifications

| Nastech layer | Modification to the single Orpheus family | Purpose |
|---|---|---|
| Training data | Curated, consented English recordings carrying transcript, speaker, emotion, behavior-event, and quality labels | Teach reliable anger, sadness, laughter, coughs, and other requested behaviors. |
| Fine-tuning | Parameter-efficient LoRA/QLoRA fine-tune against the selected Orpheus model | Preserve base speech quality while learning Nastech behavior control. |
| Prompt protocol | NastechML compiler that transforms `<emotion>` and `<sound>` elements into the Nastech training/inference prompt schema | Give developers a stable product API. |
| Inference | Nastech runtime with CPU Q4 development mode and GPU Transformers/vLLM production mode | Use one model family across all modes. |
| Evaluation | Behavior-by-behavior manifest, reference audio set, and human-review rubric | Measure whether each requested behavior is direct and natural. |

## Important Access and Training Conditions

The upstream Hugging Face model page asks users to agree to share contact information before accessing its original model files. The existing local Q4 development artifact used by the CPU backend is cached separately; it is suitable for integration testing. A real Nastech fine-tuning run must be performed only after the responsible account accepts the upstream model conditions and provides valid, licensed English training data. [1]

The current no-GPU cloud can exercise the Nastech runtime but cannot train a production-quality 3B-model fine-tune. The official Orpheus training path uses Hugging Face training tools and recommends fine-tuning from audio/text data; Nastech ships a reproducible training contract but does not claim to have trained a new model checkpoint on this CPU-only machine. [2]

## Brand Boundary

The release will use **Nastech TTS** for the package, API, model-card template, runtime configuration, datasets, evaluation reports, and future fine-tuned checkpoints. The upstream Orpheus provenance and Apache-2.0 notices remain in `NOTICE.md`; no ownership of the original model is claimed.

## References

[1] [Orpheus 3B 0.1 Finetuned model card](https://huggingface.co/canopylabs/orpheus-3b-0.1-ft)

[2] [Orpheus TTS source repository and fine-tuning guide](https://github.com/canopyai/Orpheus-TTS)
