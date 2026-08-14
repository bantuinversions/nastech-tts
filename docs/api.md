# Nastech Compact Agent API

Nastech Compact runs a local Supertonic ONNX model on CPU. An agent can compile English NastechML into an auditable local expression plan, then synthesize WAV audio without a cloud provider call.

## Authentication

When `NASTECH_API_KEY` is set, protect agent endpoints with:

```text
Authorization: Bearer <NASTECH_API_KEY>
```

`GET /v1/health` remains available for local readiness checks.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/v1/health` | Local runtime and model-asset size status |
| `GET` | `/v1/capabilities` | Direct, release-dependent, and unavailable behavior controls |
| `GET` | `/v1/agent/tools` | Machine-readable agent tool descriptors |
| `POST` | `/v1/agent/compile` | Compile NastechML without audio generation |
| `POST` | `/v1/agent/speech` | Generate local WAV audio from NastechML |
| `POST` | `/v1/audio/speech` | OpenAI-compatible plain-text local synthesis alias |

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

Send the same payload to `POST /v1/agent/speech`. The API returns `audio/wav` bytes at 44.1 kHz. It includes `X-Nastech-Request-Id`, `X-Nastech-Runtime: supertonic-local`, and `X-Nastech-Duration-Seconds` headers.

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

Use `/v1/agent/speech` rather than this alias whenever the agent needs structured emotional or non-speech controls.

The full versioned schema is available in [openapi.json](openapi.json).

## References

[1] [Supertonic official repository](https://github.com/supertone-inc/supertonic)

[2] [Supertonic Python SDK](https://github.com/supertone-inc/supertonic-py)
