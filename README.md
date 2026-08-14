# Nastech TTS

**Nastech TTS** is an English-first **expressive-speech control plane** for Fish Audio S2. It gives agents one stable markup format, compiles that intent into Fish-native emotion and vocal-event controls, and exposes an authenticated local REST API for generation or dry-run inspection.

> Nastech is **not** a separate 4B foundation model and does not redistribute Fish model weights. It is a production integration layer for a model family with documented, direct controls such as `[angry]`, `[sad]`, `[excited]`, `[laughing]`, `[sigh]`, `[whisper]`, and `[shouting]`. [1]

| Capability | Nastech v0.3 status |
|---|---|
| Real named emotion controls | Compiles to Fish S2 provider-native inline tags |
| Real vocal-event controls | Direct mappings for laugh, chuckle, sigh, gasp, groan, and cry |
| Cough, sniffle, yawn | Compiled as free-form S2 tags and marked release-dependent in the manifest |
| Agent calls | Native Nastech agent endpoints and OpenAI-compatible `/v1/audio/speech` |
| Self-hosted inference | Routes to the official Fish local server on a GPU host |
| Hosted inference | Routes to the official Fish cloud API when `FISH_AUDIO_API_KEY` is supplied |
| Agent audit trail | Returns a request ID and offers a compile-only endpoint with the full provider payload |

## Architecture

```text
Agent / workflow
      |
      | NastechML or REST JSON
      v
Nastech Agent Gateway
  - validates English expressive markup
  - compiles Fish S2 behavior tags
  - validates provider controls and creates a manifest
      |
      +---- fish-local ---> official Fish Speech S2 server (GPU)
      |
      +---- fish-cloud ---> official Fish Audio `/v1/tts` API
      v
Audio bytes plus Nastech request ID
```

Read [Fish S2 Architecture](docs/fish_s2_architecture.md), [Model Selection](docs/real_feature_model_selection.md), and [Provider Protocol](docs/fish_provider_protocol.md) for the complete technical and licensing boundaries.

## Installation

```bash
cd nastech-tts
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

Nastech itself is lightweight. A **real Fish S2 model server is a separate GPU workload**. Start an official local Fish server first, then point Nastech to it:

```bash
export NASTECH_PROVIDER=fish-local
export FISH_BASE_URL=http://127.0.0.1:8080
nastech-tts status
nastech-tts serve --host 127.0.0.1 --port 8765
```

For the official cloud route, set an API key that you obtain from Fish Audio; do not store it in source control:

```bash
export NASTECH_PROVIDER=fish-cloud
export FISH_AUDIO_API_KEY='your-provider-key'
export FISH_CLOUD_MODEL=s2.1-pro-free
nastech-tts serve --host 127.0.0.1 --port 8765
```

Set `NASTECH_API_KEY` to protect the gateway's own API with bearer authentication.

## Agent Calls

An agent should first compile a request. This exposes the exact emotion and event controls that will be sent to Fish S2 without generating audio:

```bash
curl --request POST http://127.0.0.1:8765/v1/agent/compile \
  --header 'content-type: application/json' \
  --data @- <<'JSON'
{
  "markup": "<speak><emotion name=\"sad\">I thought the lantern was gone.</emotion><sound type=\"sigh\"/><emotion name=\"happy\">But the sunrise brought it home.</emotion><sound type=\"laugh\"/></speak>",
  "output_format": "wav"
}
JSON
```

The resulting manifest includes a Fish-native payload similar to this:

```text
[sad] I thought the lantern was gone. [sigh] [delight] But the sunrise brought it home. [laughing]
```

When the output is approved, call `/v1/agent/speech` with the same JSON. The response body is audio and response headers include `X-Nastech-Request-Id` and `X-Nastech-Provider`.

Existing OpenAI-style clients can instead call:

```bash
curl --request POST http://127.0.0.1:8765/v1/audio/speech \
  --header 'content-type: application/json' \
  --data '{"model":"nastech-fish-s2","input":"Hello from Nastech.","response_format":"wav"}' \
  --output hello.wav
```

The complete agent tool descriptor is available at [agent_tools/nastech_tts_tool.json](agent_tools/nastech_tts_tool.json), or dynamically at `GET /v1/agent/tools`.

## NastechML

```xml
<speak voice="narrator-voice-id">
  <emotion name="sad" intensity="0.70">I thought we had lost the way.</emotion>
  <sound type="sigh" />
  <pause ms="400" />
  <emotion name="angry" intensity="0.85">Then the storm tore down the sign.</emotion>
  <sound type="cough" />
  <prosody rate="fast" volume="loud">
    <emotion name="excited">But the lantern flared, and everyone cheered.</emotion>
  </prosody>
  <sound type="laugh" />
</speak>
```

Use `nastech-tts compile examples/story.xml` to produce a local manifest before any provider call.

## Deployment

The default Manus sandbox is not a persistent service host and has no GPU. The gateway can run anywhere Python runs, but a self-hosted Fish S2 provider needs a separate persistent GPU server. The repository includes a Docker image for the Nastech gateway, compose templates, environment examples, health checks, and deployment instructions under `deploy/`.

## License and Model Notice

Nastech source code is Apache-2.0. The selected Fish Speech repository and Fish S2 weights are released under the **Fish Audio Research License**, which remains binding. Nastech does not bundle weights and is not a commercial-license substitute. Review [NOTICE.md](NOTICE.md) and the upstream terms before use.

## References

[1] [Fish Speech official S2 repository](https://github.com/fishaudio/fish-speech)

[2] [Fish Speech local server documentation](https://speech.fish.audio/server/)

[3] [Fish Audio official `/v1/tts` API](https://docs.fish.audio/api-reference/endpoint/openapi-v1/text-to-speech)
