# Nastech Agent API

The Nastech gateway exposes a stable agent-facing API. All behavior controls are expressed in English NastechML and compiled to Fish S2 before a provider call.

## Authentication

When `NASTECH_API_KEY` is set, call protected endpoints with:

```text
Authorization: Bearer <NASTECH_API_KEY>
```

The health endpoint is intentionally unauthenticated so orchestration systems can monitor readiness.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/v1/health` | Nastech and configured provider status |
| `GET` | `/v1/capabilities` | Supported English controls and output formats |
| `GET` | `/v1/agent/tools` | Machine-readable tool descriptors |
| `POST` | `/v1/agent/compile` | Compile NastechML without a provider call |
| `POST` | `/v1/agent/speech` | Generate expressive audio from NastechML |
| `POST` | `/v1/audio/speech` | OpenAI-compatible plain-text synthesis alias |

## Compile Before Generation

Agents should compile when they need a visible audit of what the provider will receive.

```json
{
  "markup": "<speak><emotion name=\"angry\">Do not leave me here.</emotion><sound type=\"sigh\" /></speak>",
  "reference_id": "optional-voice-id",
  "output_format": "wav",
  "latency": "normal",
  "temperature": 0.7
}
```

The compile response includes `provider_payload.text`, a request ID, and a manifest containing each mapped control. For the example above, the compiled text starts with `[angry]` and includes `[sigh]`.

## Generate Audio

Send the same request body to `POST /v1/agent/speech`. The response is raw audio bytes. Store the `X-Nastech-Request-Id` response header with downstream workflow records; it links the audio output to the compile manifest. `X-Nastech-Provider` identifies `fish-local` or `fish-cloud`.

## OpenAI-Compatible Alias

`POST /v1/audio/speech` accepts this smaller request shape:

```json
{
  "model": "nastech-fish-s2",
  "input": "The story begins at dawn.",
  "voice": "optional-voice-id",
  "response_format": "wav",
  "speed": 1.0
}
```

This path intentionally accepts plain text only. Use `/v1/agent/speech` for real Fish S2 emotion and event controls.

## Reference Voices

The self-hosted Fish server accepts a single saved `reference_id` per Nastech request. The Fish cloud S2 API can support multi-speaker requests with an array of reference IDs and `<|speaker:n|>` tokens; use the cloud provider only after checking its current terms and model availability.

The complete versioned schema is available in [openapi.json](openapi.json).
