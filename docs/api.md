# Nastech TTS API Reference

Nastech Compact v0.9.1 is a **local-first, English expressive TTS provider mixer** published by Nastech Research. It presents a single NastechML request contract, routes each synthesis request through one explicitly selected active provider, applies deterministic optional WAV cleanup, and returns auditable provider metadata. The default core is real local CPU synthesis; network providers are disabled by default and inactive catalog entries cannot synthesize.

> **Provider honesty:** a target in the 50-provider catalog is not necessarily installed, configured, licenced for a particular use, or eligible for synthesis. Call `POST /v1/providers/preflight` to receive its zero-side-effect activation requirements. See [PROVIDER_CATALOG_50.md](PROVIDER_CATALOG_50.md) and [PROVIDER_ARCHITECTURE.md](PROVIDER_ARCHITECTURE.md).

> **Streaming contract:** `/v1/agent/speech/stream` creates the complete WAV first, then transfers it in bounded chunks. This can reduce client buffering but is **not** token-level or frame-level model streaming.

## Authentication

Set `NASTECH_API_KEY` to protect every endpoint except `GET /v1/health`.

```text
Authorization: Bearer <NASTECH_API_KEY>
```

## Provider Selection

Every compile, plan, story, or synthesis request can include an optional `provider_id`. Omitting it selects `nastech-native-onnx`, the currently verified local provider. The router does not silently substitute another provider if the requested ID is inactive.

```json
{
  "markup": "<speak><emotion name=\"sad\">The lantern went dark.</emotion><sound type=\"sigh\" /></speak>",
  "provider_id": "nastech-native-onnx",
  "cleanup": true
}
```

| State | Synthesis result | Network effect |
|---|---|---|
| `active/local` | Eligible for local rendering. | None. |
| `adapter/available` | Returns HTTP 422 with an activation instruction. | None. |
| `planned/license-review` | Returns HTTP 422 with review requirements. | None. |
| `planned/credential-required` | Returns HTTP 422 with credential and privacy requirements. | None. |

## Agent Operations

| Tool | HTTP operation | Result |
|---|---|---|
| `nastech_list_providers` | `GET /v1/providers` | The 50 Nastech provider targets, truthful states, and network-default policy. |
| `nastech_provider_preflight` | `POST /v1/providers/preflight` | A provider activation plan; it never downloads software, tests credentials, or sends text/audio. |
| `nastech_compose_story` | `POST /v1/agent/story` | Deterministic Nastech Agent story markup, optionally rendered by an active local provider. |
| `nastech_plan_speech` | `POST /v1/agent/plan` | Auditable execution plan with selected provider, delivery route, cleanup state, and fidelity counts. |
| `nastech_compile_speech` | `POST /v1/agent/compile` | Provider-selected request manifest without audio generation. |
| `nastech_generate_speech` | `POST /v1/agent/speech` | Completed local `audio/wav`; cleanup is optional. |
| `nastech_stream_speech` | `POST /v1/agent/speech/stream` | Completed WAV delivered in caller-bounded post-synthesis byte chunks. |
| `nastech_clean_wav` | `POST /v1/audio/clean` | Deterministically cleaned mono signed-16-bit PCM WAV. |
| `nastech_list_platforms` | `GET /v1/platforms` | Host/runtime facts plus verified and planned portability profiles. |
| `nastech_platform_preflight` | `POST /v1/platforms/preflight` | Evidence requirements for a CPU, GPU, mobile, or browser target. |
| `nastech_runtime_diagnostics` | `GET /v1/runtime/diagnostics` | Local CPU policy, cache state, and runtime metrics. |
| `nastech_warmup_runtime` | `POST /v1/runtime/warmup` | Short local warm-up synthesis. |
| `nastech_clear_runtime_cache` | `POST /v1/runtime/cache/clear` | Bounded WAV-cache cleanup without unloading runtime sessions. |

`GET /v1/agent/tools` returns the same 13 operations as machine-readable descriptors. The repository copy is [agent_tools/nastech_tts_tool.json](../agent_tools/nastech_tts_tool.json).

## Nastech Agent Stories

`POST /v1/agent/story` composes a short deterministic English NastechML narrative. Supported themes are `innovation`, `discovery`, and `resilience`; supported emotions and sound cues are validated against NastechML. Set `render` to `false` to obtain markup and a provider-selected compilation manifest without model inference.

```json
{
  "theme": "discovery",
  "emotion": "hopeful",
  "sounds": ["sigh"],
  "provider_id": "nastech-native-onnx",
  "render": false
}
```

The response identifies **Nastech Agent** and **Nastech Research** but does not claim a cloud language model or autonomous narration service.

## Conservative WAV Cleanup and Level Gates

`POST /v1/audio/clean` accepts `Content-Type: audio/wav`, up to 64 MiB, and supports **mono signed-16-bit PCM WAV**. It applies DC-offset removal, near-silence gating, peak limiting when required to prevent clipping, and short edge fades. It is not voice conversion, a learned denoiser, speaker cloning, or mastering.

The deterministic level analyser checks channel count, sample rate, duration, peak, RMS, clipping, and DC offset. Real local release voices are generated only in the tag-only workflow, stored as audited fixtures, and revalidated from checksum-bearing manifests. The same workflow runs `generate_longform_continuity_test.py` to create an exact 1,800-second local continuity WAV from unique rendered segments plus M1, M3, F1, and F3 preset-style auditions. See [LONGFORM_CONTINUITY_TEST.md](../release/LONGFORM_CONTINUITY_TEST.md), [release/voice_fixtures](../release/voice_fixtures/), and [RELEASE_CHECKLIST.md](../release/RELEASE_CHECKLIST.md).

## Portability Discovery

`GET /v1/platforms` reports current host facts, registered ONNX Runtime providers, and Nastech target profiles. `POST /v1/platforms/preflight` accepts targets such as `python-cuda`, `android-nnapi`, or `web-webgpu`. A registered runtime provider does not prove that an active Nastech provider runs on the target. Python CPU remains the only verified profile; other profiles require real synthesis, audio validity, latency, memory, package, and applicable device evidence before promotion. ONNX Runtime documents that execution-provider behaviour is model- and device-dependent. [1] [2]

## Core Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/v1/health` | Public readiness and runtime state. |
| `GET` | `/v1/capabilities` | Nastech provider mixer, delivery, cleanup, CPU, expression, and agent contract. |
| `GET` | `/v1/providers` | Provider inventory and state summary. |
| `POST` | `/v1/providers/preflight` | Zero-side-effect provider activation plan. |
| `GET` | `/v1/agent/identity` | Nastech Agent identity and story capability boundary. |
| `POST` | `/v1/agent/story` | Compose or render a Nastech Agent story. |
| `POST` | `/v1/agent/plan` | Agent planning without synthesis. |
| `POST` | `/v1/agent/compile` | NastechML compilation without synthesis. |
| `POST` | `/v1/agent/speech` | Complete expressive WAV generation through an active local provider. |
| `POST` | `/v1/agent/speech/stream` | Completed WAV transferred in bounded chunks. |
| `POST` | `/v1/audio/clean` | Conservative local WAV cleanup. |
| `POST` | `/v1/audio/speech` | OpenAI-compatible local plain-text synthesis alias. |
| `GET` | `/v1/platforms` | Current host runtime facts and portability profiles. |
| `POST` | `/v1/platforms/preflight` | Validation-gated target activation plan. |
| `GET` | `/v1/runtime/diagnostics` | Local CPU/cache diagnostics. |
| `POST` | `/v1/runtime/warmup` | Local warm-up. |
| `POST` | `/v1/runtime/cache/clear` | Bounded WAV-cache management. |

## Daily and Release Verification

The deterministic workflow runs on push, pull request, manual dispatch, and **daily at 03:17 UTC**. It checks formatting, static analysis, all deterministic tests, generated 500+500+1,000 roadmap drift, JSON/YAML contracts, OpenAPI drift, source/wheel builds, and distribution metadata. It intentionally does not download models or call managed TTS services. The tag-only release-audio workflow separately renders and validates the real local voice fixtures. See [REPOSITORY_AUTOMATION.md](REPOSITORY_AUTOMATION.md).

The versioned OpenAPI schema is [openapi.json](openapi.json).

## References

[1] [ONNX Runtime execution providers](https://onnxruntime.ai/docs/execution-providers/)

[2] [ONNX Runtime mobile deployment guide](https://onnxruntime.ai/docs/tutorials/mobile/)
