# Nastech Compact Agent API

Nastech Compact runs a local Supertonic ONNX model on CPU. An agent can compile English NastechML into an auditable local expression plan, then synthesize 44.1 kHz WAV audio without a cloud provider call. The v0.5.0 gateway adds configurable ONNX CPU threads, bounded synthesis concurrency, bounded response caching, local warm-up, and operational diagnostics. [1] [2]

## Authentication

When `NASTECH_API_KEY` is set, protect agent and runtime endpoints with:

```text
Authorization: Bearer <NASTECH_API_KEY>
```

`GET /v1/health` remains available for local readiness checks. `GET /v1/capabilities` and all endpoints except health require the bearer token when a token is configured.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/v1/health` | Unauthenticated readiness, model-asset, and CPU policy status |
| `GET` | `/v1/capabilities` | Controls, local-runtime capabilities, and CPU optimization features |
| `GET` | `/v1/runtime/diagnostics` | Authenticated CPU profile, queue/cache statistics, and runtime metrics |
| `POST` | `/v1/runtime/warmup` | Authenticated preload plus one short real local synthesis |
| `GET` | `/v1/agent/tools` | Machine-readable agent tool descriptors |
| `POST` | `/v1/agent/compile` | Compile NastechML without generating audio |
| `POST` | `/v1/agent/speech` | Generate local WAV audio from NastechML |
| `POST` | `/v1/audio/speech` | OpenAI-compatible plain-text local synthesis alias |

## CPU Runtime Controls

The gateway protects local CPU inference with a bounded semaphore. The configured number of active synthesis jobs may run concurrently; excess requests wait for `NASTECH_QUEUE_TIMEOUT_SECONDS` before receiving a `503` response. The runtime keeps a bounded in-memory WAV cache for identical requests, which improves repeated-call latency without storing data on disk.

| Environment variable | Default | Meaning |
|---|---:|---|
| `NASTECH_CPU_PROFILE` | `balanced` | `balanced`, `latency`, `throughput`, or `auto` policy |
| `NASTECH_INTRA_OP_THREADS` | Profile value | Explicit ONNX intra-operation worker count |
| `NASTECH_INTER_OP_THREADS` | Profile value | Explicit ONNX inter-operation worker count |
| `NASTECH_MAX_PARALLEL_SYNTHESIS` | Profile value | Active local syntheses permitted before queueing |
| `NASTECH_QUEUE_TIMEOUT_SECONDS` | `120` | Queue timeout in seconds |
| `NASTECH_AUDIO_CACHE_ENTRIES` | `8` | Maximum response-cache entries |
| `NASTECH_AUDIO_CACHE_MIB` | `32` | Maximum response-cache size in MiB |
| `NASTECH_WARMUP_ON_START` | `0` | Preload and synthesize at server startup when truthy |

`GET /v1/runtime/diagnostics` exposes the effective values, model-cache size, response-cache size, request/failure counts, queue wait time, and mean synthesis time. It does not reveal secrets or user input.

## Compile Endpoint

```json
{
  "markup": "<speak voice=\"F1\"><emotion name=\"sad\">The lantern went dark.</emotion><sound type=\"sigh\"/><sound type=\"laugh\"/></speak>",
  "steps": 8
}
```

The compact compiler returns an auditable plan similar to:

```text
<sad> The lantern went dark. <sigh> <laugh>
```

Every requested control is tagged as `direct`, `approximated`, or `unavailable` in the manifest. `<laugh>` and `<sigh>` are documented Supertonic controls. Other preserved tags, including `<sad>`, `<angry>`, `<cough>`, and `<yawn>`, require model-release acceptance testing before deterministic claims are made. [1] [2]

## Synthesis Endpoint

Send the same payload to `POST /v1/agent/speech`. The API returns `audio/wav` bytes at 44.1 kHz. Successful responses include:

| Header | Meaning |
|---|---|
| `X-Nastech-Request-Id` | Request identifier shared with the compilation manifest |
| `X-Nastech-Runtime` | `supertonic-local-onnx-cpu` |
| `X-Nastech-Duration-Seconds` | Generated audio duration |
| `X-Nastech-Manifest-Endpoint` | Compilation endpoint for the matching audit manifest |

## Warm-up Endpoint

Call `POST /v1/runtime/warmup` after deployment when startup warm-up was not enabled. It loads the local ONNX sessions and the default voice vector, then creates a short local WAV to stabilize the first production request. The response includes elapsed warm-up time and the resulting runtime diagnostics.

## OpenAI-Compatible Alias

```json
{
  "model": "nastech-compact-en-v1",
  "input": "The lantern is bright again.",
  "voice": "F1",
  "response_format": "wav",
  "speed": 1.0
}
```

Use `/v1/agent/speech` rather than this alias whenever the agent needs structured emotional or non-speech controls. The full versioned schema is available in [openapi.json](openapi.json).

## References

[1] [Supertonic official repository](https://github.com/supertone-inc/supertonic)

[2] [Supertonic Python SDK](https://github.com/supertone-inc/supertonic-py)
