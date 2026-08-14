# Nastech TTS 0.2 Verification Record

**Verification date:** 2026-08-14  
**Runtime:** Ubuntu 24.04, Python 3.12, six CPU cores, no NVIDIA GPU.

## Single-Model Product Checks

| Check | Result |
|---|---|
| Product model identity | Passed: `nastech-voice-en-v1` is explicitly derived from `canopylabs/orpheus-3b-0.1-ft`. |
| Multi-model fallbacks | Removed: no Kokoro, Dia, EmotiVoice, Fish Audio, or other model runtime remains in the Nastech product code. |
| Local selected-model runtime | Passed: `orpheus-cpp` is available through the Nastech local runtime. |
| NastechML parser | Passed: parser tests validate speech, sounds, pauses, English-only input, and unknown-tag rejection. |
| API contract | Passed: local health and model-provenance tests completed without a model render. |
| Behavior fidelity suite | Passed: 5 of 5 expected base-model capability checks. |
| Unit suite | Passed: 9 of 9 tests. |
| Static checks | Passed: Ruff completed without findings. |
| Package build | Passed: source distribution and wheel for version 0.2.0 were built. |
| Clean wheel installation | Passed: the wheel installed into a fresh virtual environment and exposed the correct model metadata. |

## End-to-End Single-Model Render

The packaged Nastech v0.2 runtime generated `output/nastech_v02_scene.wav` using the selected Orpheus model family only. The file is a 10.40-second, 24 kHz mono WAV with a companion Nastech manifest.

| Requested behavior | Render result |
|---|---|
| English speech | Direct |
| Cough | Direct |
| Laughter | Direct |
| 250 ms pause | Direct |
| Anger | Approximated pending a trained Nastech adapter |
| Sadness | Approximated pending a trained Nastech adapter |

The manifest includes the base model identifier, Apache-2.0 provenance, Nastech adapter strategy, every span-level fidelity decision, and warnings for the two named emotions. This is intentional product behavior: Nastech does not overstate untrained emotion control.

## Training Boundary

Nastech 0.2 includes the LoRA/QLoRA launch configuration, data schema, data validator, behavior suite, and model-card/release requirements needed to modify the ready-made fine-tuned base. It does not claim to have trained an adapter in this cloud, because the current environment has no NVIDIA GPU and no licensed behavior-labelled English audio dataset was supplied.

## Release Artifacts

The verified Python distributions are:

- `dist/nastech_tts-0.2.0-py3-none-any.whl`
- `dist/nastech_tts-0.2.0.tar.gz`

These are ready for TestPyPI and later PyPI publication after the user provides the destination account and repository details.
