# Cross-Platform Runtime Research Notes

Research date: 2026-08-15.

| Area | Verified finding | Product implication |
|---|---|---|
| Portable ONNX acceleration | ONNX Runtime exposes a consistent execution-provider interface and lists CPU, CUDA, TensorRT, DirectML, OpenVINO, QNN, NNAPI, CoreML, XNNPACK, and WebGPU options. [1] | Nastech can expose a provider **planning and diagnostics contract**, but must only mark a provider active after the platform build and model execute successfully. |
| Provider fallback | ONNX Runtime provider order controls priority and CPU can remain a fallback after a higher-priority provider. [1] | Keep CPU as the verified default; do not replace it with untested GPU selection. |
| Android baseline | ONNX Runtime mobile supports Android Java/C/C++ packages, CPU by default, and Android NNAPI/XNNPACK acceleration options. [2] | A native Android client is technically viable but needs an Android artifact, model compatibility test, device memory check, and performance validation. |
| Android hardware acceleration | The NNAPI execution provider is an Android API 8.1+ interface for CPU, GPU, and NN accelerators; Android 9+ is recommended. Unsupported model operators can cause partitions/fallback and performance is device/model specific. [3] | Android GPU/NPU support must be treated as a **device-specific planned/validated capability**, not a universal promise. |
| Mobile size and performance | ONNX Runtime recommends measuring device disk, memory, latency, and power; custom minimal builds and model quantization can reduce mobile size but require model/operator validation. [2] | The current ~385 MiB model does not meet a universal phone-install target; an Android package should use a separately measured mobile profile and a compatible compact/quantized asset strategy. |
| Nastech Voice Core ecosystem | The upstream repository documents ONNX-based on-device inference and examples across Python, Node.js, browser, Java, C++, C#, Go, Swift, iOS, Rust, and Flutter. It also carries a July 2026 notice of archive/no further official open-source support. [4] | Nastech can build portable clients around a stable ONNX contract, but must pin and mirror all upstream licensing/asset provenance information for long-term maintenance. |

## Architecture Decision

Nastech v0.7 retains the verified CPU Python runtime as the default. The next portable layer will provide capability discovery, platform profiles, request compatibility validation, and client/packaging templates. It will not claim working CUDA, NNAPI, XNNPACK, WebGPU, or Android inference until the real Nastech Voice Core graph has been validated on that provider and target device.

## References

[1] [ONNX Runtime execution providers](https://onnxruntime.ai/docs/execution-providers/)

[2] [ONNX Runtime mobile deployment guide](https://onnxruntime.ai/docs/tutorials/mobile/)

[3] [ONNX Runtime NNAPI execution provider](https://onnxruntime.ai/docs/execution-providers/NNAPI-ExecutionProvider.html)

[4] [Nastech Voice Core official repository](https://github.com/bantuinversions/nastech-tts)

## Capability-Family Research

| Capability family | Verified source evidence | Nastech roadmap treatment |
|---|---|---|
| Zero-shot/cross-language voice cloning | XTTS-v2 documents cloning from short reference audio, multiple references, cross-language generation, style transfer, and 17-language support. Its model card uses the Coqui Public Model License. [5] | **Deferred and separately governed.** It requires explicit consent, abuse controls, different model/runtime assets, and license review; it cannot be silently added to the single-model 1 GiB Compact runtime. |
| True model streaming | XTTS documentation describes streaming inference with chunks produced during generation and says streaming can improve time to first chunk, with different latency/throughput tradeoffs. [6] | Nastech’s current post-synthesis chunk endpoint is correctly labeled as transfer streaming only. True inference streaming needs a model/runtime implementation that emits causal audio chunks. |
| Speaker conditioning and quality controls | XTTS documentation exposes speaker-reference caching, multiple references, text splitting, sampling controls, repetition penalty, speed, and fine-tuning. [6] | These become catalog items with required privacy, model, evaluation, and resource gates rather than unverified current claims. |
| Multi-style/multi-speaker and chunk inference | F5-TTS documents basic chunk inference, multi-style/multi-speaker generation, voice-chat composition, GPU runtime options, and a separate evaluation area. Its pretrained model license is CC-BY-NC. [7] | These are feature categories, not drop-in Compact features: their model family, GPU dependencies, and pretrained-model license conflict with the Compact single-family/product constraints. |

[5] [XTTS-v2 model card](https://huggingface.co/coqui/XTTS-v2)

[6] [Coqui XTTS technical documentation](https://github.com/coqui-ai/TTS/blob/dev/docs/source/models/xtts.md)

[7] [F5-TTS official repository](https://github.com/swivid/f5-tts)
