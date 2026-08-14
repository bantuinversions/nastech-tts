# Fish Provider Protocol Notes

Nastech uses the official Fish Audio `POST /v1/tts` protocol for both cloud and local provider modes. The production cloud endpoint is `https://api.fish.audio/v1/tts`; the configured local endpoint is normally `http://FISH_LOCAL_HOST:8080/v1/tts` after starting the official Fish server.

## Cloud Request Rules

The cloud request requires `Authorization: Bearer <token>`, accepts JSON, and may use the `model` request header. The documented request body includes `text`, optional `reference_id`, `prosody.speed`, `prosody.volume`, `format`, `sample_rate`, `latency`, `temperature`, `top_p`, `chunk_length`, and `condition_on_previous_chunks`. The official endpoint accepts the W3C `traceparent` header for distributed tracing.

## Local Request Rules

The official Fish local server exposes `GET /v1/health` and `POST /v1/tts`. It is started from Fish Speech with a selected model at process startup, so the local request does not select the base model for each call. It can be configured with a bearer API key through the Fish server startup options.

## Nastech Rule

Nastech compiles structured behavior intent into the provider `text` field. It never logs provider tokens. It preserves the source markup, compiled text, mapped controls, provider mode, and response metadata in an auditable manifest.

## References

[1] [Fish Audio official cloud TTS endpoint](https://docs.fish.audio/api-reference/endpoint/openapi-v1/text-to-speech)

[2] [Fish Speech official local server](https://speech.fish.audio/server/)
