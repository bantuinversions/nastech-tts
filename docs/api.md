# Nastech Compact Agent API

Nastech Compact v0.6.0 runs a local Supertonic ONNX model on CPU. An agent can validate and compile English NastechML into an auditable local expression plan, then synthesize 44.1 kHz WAV audio without a cloud provider call. The service also exposes bounded CPU scheduling, cached-response management, warm-up, diagnostics, and a stable agent tool catalog. [1] [2]

## Authentication

Set `NASTECH_API_KEY` to protect all non-health endpoints:

```text
Authorization: Bearer <NASTECH_API_KEY>
```

`GET /v1/health` intentionally remains available for local readiness checks. It does not expose the configured key or request contents.

## Endpoint Contract

| Method | Path | Purpose | Authentication |
|---|---|---|---|
| `GET` | `/v1/health` | Readiness, model state, and CPU-policy status | Public |
| `GET` | `/v1/capabilities` | Expression, format, and operational capability listing | Bearer when configured |
| `GET` | `/v1/agent/tools` | Machine-readable catalog of the five agent operations | Bearer when configured |
| `POST` | `/v1/agent/compile` | Compile NastechML without audio generation | Bearer when configured |
| `POST` | `/v1/agent/speech` | Generate local expressive WAV from NastechML | Bearer when configured |
| `POST` | `/v1/audio/speech` | OpenAI-compatible plain-text local synthesis alias | Bearer when configured |
| `GET` | `/v1/runtime/diagnostics` | Effective CPU policy, model/cache state, and metrics | Bearer when configured |
| `POST` | `/v1/runtime/warmup` | Load ONNX sessions and produce a short local warm-up WAV | Bearer when configured |
| `POST` | `/v1/runtime/cache/clear` | Clear cached WAV data without unloading local ONNX sessions | Bearer when configured |

## Agent Tool Catalog

`GET /v1/agent/tools` and `agent_tools/nastech_tts_tool.json` expose the same stable operation set.

| Tool | HTTP operation | Result |
|---|---|---|
| `nastech_compile_speech` | `POST /v1/agent/compile` | Auditable expression plan and fidelity manifest |
| `nastech_generate_speech` | `POST /v1/agent/speech` | Local WAV bytes and request headers |
| `nastech_runtime_diagnostics` | `GET /v1/runtime/diagnostics` | CPU policy, model/cache state, and aggregate metrics |
| `nastech_warmup_runtime` | `POST /v1/runtime/warmup` | Warm-up duration, generated duration, and diagnostics |
| `nastech_clear_runtime_cache` | `POST /v1/runtime/cache/clear` | Entries and bytes cleared plus refreshed diagnostics |

## Compile and Synthesis

Compile before synthesis when an agent needs to inspect the requested behavior:

```json
{
  "markup": "<speak voice=\"F1\"><emotion name=\"sad\">The lantern went dark.</emotion><sound type=\"sigh\"/><sound type=\"laugh\"/></speak>",
  "steps": 8
}
```

The compiler produces a local prompt similar to:

```text
<sad> The lantern went dark. <sigh> <laugh>
```

Every requested control is marked as `direct`, `approximated`, or `unavailable` in the manifest. `<laugh>` and `<sigh>` are documented Supertonic controls. Other preserved tags, including `<sad>`, `<angry>`, `<cough>`, and `<yawn>`, must pass pinned-model acceptance tests before deterministic product claims are made. [1] [2]

Send the same request to `POST /v1/agent/speech` to receive `audio/wav` output. Successful responses include `X-Nastech-Request-Id`, `X-Nastech-Runtime: supertonic-local-onnx-cpu`, `X-Nastech-Duration-Seconds`, and the manifest endpoint.

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

Use the structured agent endpoint for NastechML emotional or non-speech controls. The alias is designed for plain-text clients already using a familiar speech-request shape.

## Runtime Operations

The runtime uses a bounded synthesis queue and a bounded in-memory WAV cache. `GET /v1/runtime/diagnostics` reports the selected CPU policy, ONNX thread values, model assets, cache usage, queue timing, failure count, and mean synthesis time. `POST /v1/runtime/cache/clear` is useful when a long-lived process needs to free retained response bytes without paying model reload cost.

Enable deterministic warm-up at process startup with `NASTECH_WARMUP_ON_START=1`, or call the warm-up endpoint after deployment. See [cpu_optimization.md](cpu_optimization.md) for measured profile evidence and [DEPLOYMENT.md](../deploy/DEPLOYMENT.md) for operational configuration.

The versioned OpenAPI schema is [openapi.json](openapi.json).

## References

[1] [Supertonic official repository](https://github.com/supertone-inc/supertonic)

[2] [Supertonic Python SDK](https://github.com/supertone-inc/supertonic-py)
