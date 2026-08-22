# Nastech Portability Architecture

## Goal

Nastech TTS keeps **CPU Python inference** as its current verified deployment. The portability layer adds a stable way for agents and clients to discover host capabilities, plan a platform target, and reject unsupported configurations before work begins. It does not activate a GPU, Android accelerator, or mobile client merely because a label exists.

| Target | Current state | Activation rule |
|---|---|---|
| Python CPU | Verified local runtime | Default Nastech Voice Core Python/ONNX path passes synthesis and budget checks |
| NVIDIA CUDA | Provider-detected/planned | Nastech Voice Core session must accept CUDA provider selection and pass real ONNX synthesis on the target GPU |
| TensorRT | Planned | Export/build compatibility, supported graph partitions, and real latency/quality acceptance must pass |
| Windows DirectML | Planned | Platform build and real provider/session validation must pass |
| Intel OpenVINO | Planned | Compatible model conversion/provider run and output acceptance must pass |
| Android CPU/XNNPACK | Planned | Native Android runtime, app memory budget, and real model run on target device must pass |
| Android NNAPI | Planned/device-specific | Android API level, graph partitioning, provider fallback, and real device performance must pass |
| Apple CoreML | Planned | Native iOS/macOS artifact and real CoreML validation must pass |
| Browser WebGPU/WASM | Planned | Browser ONNX package, supported graph, memory budget, and real-device test must pass |

## Portable Contract

The `nastech_tts.platforms` module and `/v1/platforms` API expose four factual layers.

| Layer | Purpose |
|---|---|
| Host facts | Operating system, CPU architecture, Python version, ONNX Runtime registered providers, and model budget inputs |
| Target profiles | Provider/runtime/mobile requirements and whether the profile is verified, planned, or device-specific |
| Preflight plan | Exact target, missing prerequisites, acceptance tests, configuration hints, and claim boundary |
| Evidence record | Runtime probe output and a place to attach actual target-device execution/latency/battery reports |

## GPU Rule

ONNX Runtime supports hardware execution providers, but provider availability alone does not prove that the Nastech Voice Core graph executed there. Nastech will expose a GPU target as **planned** until the Nastech Voice Core loader can pass explicit provider ordering into the ONNX session and a real synthesis test records active provider, correctness, latency, memory, and audio acceptance.

## Android Rule

Android support requires an Android application artifact using the ONNX Runtime mobile package and a target-device test. Android NNAPI can route work toward CPU/GPU/NPU hardware, but model partitioning and fallback are device-specific. A 385 MiB model cache also requires an app-download, disk, memory, and startup budget measurement; it is not a universal phone install assumption. [1] [2]

## Acceptance Evidence

A platform profile changes from planned to verified only when all relevant evidence is committed:

| Requirement | CPU | GPU | Android |
|---|---:|---:|---:|
| Provider/runtime registration | yes | yes | yes |
| Real Nastech Voice Core synthesis | yes | yes | yes |
| Audio-duration and waveform validity | yes | yes | yes |
| Latency and memory measurement | yes | yes | yes |
| Model/app size measurement | yes | yes | yes |
| Thermal/battery observation | optional | optional | yes |
| Device/model compatibility record | optional | GPU/driver | device/API/provider |
| License and distribution check | yes | yes | yes |

## References

[1] [ONNX Runtime execution providers](https://onnxruntime.ai/docs/execution-providers/)

[2] [ONNX Runtime mobile deployment guide](https://onnxruntime.ai/docs/tutorials/mobile/)
