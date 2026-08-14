# Nastech TTS Local API

The Nastech HTTP API is optional and local by default. It wraps the same single-model runtime used by the CLI. Install the API and local runtime extras, then start the service:

```bash
pip install 'nastech-tts[api,local]'
nastech-tts serve --host 127.0.0.1 --port 8765
```

The development sandbox is not an always-on service host. Use the API locally for integration tests; deploy it only on a suitable persistent GPU environment for production use.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/v1/health` | Returns runtime availability and selected-model status. |
| `GET` | `/v1/models/nastech-voice-en-v1` | Returns selected-model provenance and capability metadata. |
| `POST` | `/v1/audio/speech` | Accepts NastechML and returns `audio/wav`. |

## Generate Speech

```bash
curl --request POST http://127.0.0.1:8765/v1/audio/speech \
  --header 'Content-Type: application/json' \
  --data '{"markup":"<speak voice=\"tara\">Hello from Nastech.<sound type=\"laugh\" /></speak>"}' \
  --output speech.wav
```

The response includes two headers:

| Header | Meaning |
|---|---|
| `X-Nastech-Model` | Nastech product model ID used for the synthesis. |
| `X-Nastech-Fidelity` | Comma-separated direct/approximated fidelity entries for each generated audio span. |

The API does not accept arbitrary upstream model IDs. It runs only the selected Nastech base model family and, once trained, its matching Nastech adapter.
