# Nastech Compact Agent API

Nastech Compact v0.8.0 provides **local, English-only Supertonic ONNX synthesis** on CPU. It adds portable-runtime inventory and preflight planning for GPU, mobile, and browser targets while retaining agent planning, transparent post-synthesis chunk delivery, deterministic PCM cleanup, compiler, synthesis, diagnostics, warm-up, and cache operations. No endpoint proxies text or audio to a cloud TTS provider. [1] [2]

> **Streaming contract:** `/v1/agent/speech/stream` synthesizes the complete WAV locally first, then transmits the result in bounded chunks. It is useful for memory-bounded clients and progressive transfer, but it is **not** falsely presented as token-level or frame-level model streaming.

## Authentication

Set `NASTECH_API_KEY` to protect every endpoint except `GET /v1/health`:

```text
Authorization: Bearer <NASTECH_API_KEY>
```

## Agent Operations

| Tool | HTTP operation | Local result |
|---|---|---|
| `nastech_plan_speech` | `POST /v1/agent/plan` | Validated execution plan, local delivery route, requested cleanup state, and direct/approximated/unavailable fidelity counts |
| `nastech_compile_speech` | `POST /v1/agent/compile` | Supertonic prompt and auditable NastechML manifest without audio generation |
| `nastech_generate_speech` | `POST /v1/agent/speech` | Completed local `audio/wav` response; optional cleanup |
| `nastech_stream_speech` | `POST /v1/agent/speech/stream` | Completed local WAV delivered in bounded post-synthesis byte chunks |
| `nastech_clean_wav` | `POST /v1/audio/clean` | Deterministically cleaned mono signed-16-bit PCM WAV, with cleanup headers |
| `nastech_list_platforms` | `GET /v1/platforms` | Factual host/runtime facts, registered ONNX providers, and verified/planned target profiles |
| `nastech_platform_preflight` | `POST /v1/platforms/preflight` | Activation requirements, evidence gates, and claim boundary for a named CPU/GPU/mobile/browser target |
| `nastech_runtime_diagnostics` | `GET /v1/runtime/diagnostics` | CPU policy, ONNX model/cache state, and synthesis metrics |
| `nastech_warmup_runtime` | `POST /v1/runtime/warmup` | Loaded local runtime and short warm-up synthesis |
| `nastech_clear_runtime_cache` | `POST /v1/runtime/cache/clear` | Cache entries and bytes cleared without unloading ONNX sessions |

`GET /v1/agent/tools` returns the same ten operations as machine-readable API descriptors. A repository copy is stored in [`agent_tools/nastech_tts_tool.json`](../agent_tools/nastech_tts_tool.json).

## Plan Before Synthesis

Use planning when an agent needs to inspect local behavior before consuming CPU time:

```json
{
  "markup": "<speak voice=\"F1\"><emotion name=\"sad\">The lantern went dark.</emotion><sound type=\"sigh\"/></speak>",
  "objective": "Prepare a cautious local narration response.",
  "delivery": "chunked-wav",
  "cleanup": true
}
```

The plan returns the compiled text, manifest, local model family, delivery endpoint, cleanup request, and a fidelity summary. A plan does **not** claim that an expression is deterministic when the pinned Supertonic release has not been listening-tested for that tag.

## Chunked WAV Delivery

`POST /v1/agent/speech/stream` accepts the speech request plus `chunk_bytes` from 4 KiB to 1 MiB. It returns `audio/wav` with these headers:

| Header | Meaning |
|---|---|
| `X-Nastech-Delivery: chunked-post-synthesis` | The full WAV was generated locally before chunk transmission began |
| `X-Nastech-Chunk-Bytes` | Maximum body chunk size requested by the caller |
| `X-Nastech-Request-Id` | Correlation ID shared with the compilation manifest |
| `X-Nastech-Voice-Cleanup` | `not-requested` or `local-pcm-hygiene` |

## Conservative Voice Cleanup

`POST /v1/audio/clean` accepts `Content-Type: audio/wav`, up to 64 MiB, and only supports **mono signed-16-bit PCM WAV**. It applies four deterministic, local operations: DC-offset removal, a near-silence gate, peak limiting only when needed to prevent clipping, and short edge fades to reduce clicks.

This tool is **not** voice conversion, denoising by a learned second model, speaker cloning, or a claim of professional mastering. It does not change speaker identity and requires no model download or cloud call.

The normal synthesis and OpenAI-compatible endpoints accept `"cleanup": true` when the caller wants this stage after local inference. Cleanup remains opt-in to preserve byte-for-byte compatibility for existing callers.

## Portability Discovery and Preflight

`GET /v1/platforms` reports operating-system/architecture facts, the ONNX Runtime providers registered **on the current host**, and Nastech target profiles. A registered provider is not claimed to run the Supertonic graph.

`POST /v1/platforms/preflight` accepts a target such as `python-cuda`, `android-nnapi`, or `web-webgpu`. It responds with target-specific prerequisites, matching providers on the current host, acceptance evidence required, and an explicit claim boundary. `python-cpu` is the only verified profile in v0.8. GPU, Android, iOS, and browser profiles remain planned until a real target synthesis proves compatibility, audio validity, latency, memory, and package constraints. ONNX Runtime documents that execution-provider results are model and device specific. [3] [4]

```json
{"target": "android-nnapi"}
```

## Core Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/v1/health` | Public readiness, selected CPU policy, and model state |
| `GET` | `/v1/capabilities` | Local model, delivery, cleanup, CPU, and expression contract |
| `POST` | `/v1/agent/plan` | Agent planning without synthesis |
| `POST` | `/v1/agent/compile` | NastechML compilation without synthesis |
| `POST` | `/v1/agent/speech` | Complete local expressive WAV generation |
| `POST` | `/v1/agent/speech/stream` | Completed WAV transferred in bounded chunks |
| `POST` | `/v1/audio/clean` | Local conservative WAV cleanup |
| `POST` | `/v1/audio/speech` | OpenAI-compatible plain-text local synthesis alias |
| `GET` | `/v1/platforms` | Current host ONNX providers and verified/planned platform profiles |
| `POST` | `/v1/platforms/preflight` | Validation-gated target activation plan |
| `GET` | `/v1/runtime/diagnostics` | Local CPU/model/cache diagnostics |
| `POST` | `/v1/runtime/warmup` | Local ONNX warm-up |
| `POST` | `/v1/runtime/cache/clear` | Bounded WAV cache management |

## Daily Verification

GitHub Actions runs the deterministic full quality workflow on push, pull request, manual dispatch, and **daily at 03:17 UTC**. The scheduled run executes formatting, static analysis, the Python suite, generated 500-capability catalog drift detection, machine-readable contract validation, OpenAPI drift detection, source/wheel builds, and distribution checks. It intentionally does not download models or generate cloud audio. See [REPOSITORY_AUTOMATION.md](REPOSITORY_AUTOMATION.md).

The versioned OpenAPI schema is [openapi.json](openapi.json).

## References

[1] [Supertonic official repository](https://github.com/supertone-inc/supertonic)

[2] [Supertonic Python SDK](https://github.com/supertone-inc/supertonic-py)

[3] [ONNX Runtime execution providers](https://onnxruntime.ai/docs/execution-providers/)

[4] [ONNX Runtime mobile deployment guide](https://onnxruntime.ai/docs/tutorials/mobile/)
