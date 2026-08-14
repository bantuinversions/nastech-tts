# Nastech Compact TTS

**Nastech Compact** is a real, local, English expressive TTS project built around **Supertonic 3**, a 99M-parameter ONNX model. It runs on CPU, requires no cloud synthesis call or GPU, and exposes a local agent API with auditable behavior controls. [1] [2]

> **Size commitment:** the verified local deployment is approximately **567 MiB** before generated audio: **386 MiB** of real Supertonic model assets plus **181 MiB** for the isolated Python runtime and dependencies. It is below the user-set **1 GiB maximum full deployment budget**.

| Capability | Nastech Compact v0.4 status |
|---|---|
| Real local synthesis | Working through the official Supertonic ONNX runtime |
| CPU-only operation | Supported; no provider account, GPU, or cloud request required |
| Agent calls | Nastech compile and speech endpoints plus an OpenAI-compatible alias |
| Direct documented expression events | `<laugh>` and `<sigh>` |
| Additional native-tag requests | `<sad>`, `<angry>`, `<surprise>`, `<cough>`, and `<yawn>` are preserved and marked release-dependent until local acceptance-tested |
| Output | 44.1 kHz WAV |
| Deployment size target | 1 GiB maximum, measured below the cap |

## Architecture

```text
Agent / workflow
      |
      | NastechML or REST JSON
      v
Nastech Compact API
  - validates English expressive markup
  - compiles local Supertonic expression tags
  - creates a request manifest
      |
      v
Supertonic 3 ONNX runtime (local CPU)
      |
      v
44.1 kHz WAV bytes
```

The model is downloaded into the local Supertonic cache on first use. Nastech does not distribute upstream model weights in its source package.

## Installation

```bash
cd nastech-tts
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

The first synthesis automatically downloads the upstream model assets. Verify the current installed size before serving traffic:

```bash
nastech-tts status
```

The status output includes `model_assets_mib` and `target_max_deployment_mib`.

## Real Local Synthesis

```bash
nastech-tts synthesize examples/compact_agent_story.xml --output output/story.wav
```

This creates both `output/story.wav` and an auditable `output/story.wav.manifest.json`. The example performs real local CPU inference using the cached Supertonic model.

## Agent API

Start a local API server:

```bash
export NASTECH_API_KEY='choose-a-local-secret'
nastech-tts serve --host 127.0.0.1 --port 8765
```

An agent should compile intent first. This does not synthesize audio and lets the agent inspect every tag:

```bash
curl --request POST http://127.0.0.1:8765/v1/agent/compile \
  --header 'content-type: application/json' \
  --header 'authorization: Bearer choose-a-local-secret' \
  --data @- <<'JSON'
{
  "markup": "<speak voice=\"F1\"><emotion name=\"sad\">The lantern went dark.</emotion><sound type=\"sigh\"/><emotion name=\"happy\">Then sunrise filled the room.</emotion><sound type=\"laugh\"/></speak>"
}
JSON
```

The compact compiler returns local Supertonic prompt text such as:

```text
<sad> The lantern went dark. <sigh> Then sunrise filled the room. <laugh>
```

Generate audio by sending the same payload to `/v1/agent/speech`. The response is WAV bytes with `X-Nastech-Request-Id`, `X-Nastech-Runtime`, and `X-Nastech-Duration-Seconds` headers.

Existing agent clients can call the OpenAI-compatible `POST /v1/audio/speech` endpoint:

```bash
curl --request POST http://127.0.0.1:8765/v1/audio/speech \
  --header 'content-type: application/json' \
  --data '{"model":"nastech-compact-en-v1","input":"Hello from Nastech.","voice":"F1"}' \
  --output hello.wav
```

The complete tool descriptor is at [agent_tools/nastech_tts_tool.json](agent_tools/nastech_tts_tool.json), and the generated OpenAPI contract is at [docs/openapi.json](docs/openapi.json).

## NastechML

```xml
<speak voice="F1">
  <emotion name="sad">The rain would not stop.</emotion>
  <sound type="sigh" />
  <pause ms="300" />
  <emotion name="angry">I will not surrender to the storm.</emotion>
  <sound type="cough" />
  <emotion name="happy">At dawn, the lantern shone again.</emotion>
  <sound type="laugh" />
</speak>
```

Nastech always reports whether a requested control is documented direct, release-dependent, or unavailable. Do not market a named emotion as deterministic until the pinned model build has passed a listening acceptance test for that control.

## License and Model Notice

Nastech source is Apache-2.0. Supertonic code is MIT licensed, and Supertonic 3 model weights use the OpenRAIL-M license. Nastech does not relabel the upstream model as its own or bundle the weights. Review [NOTICE.md](NOTICE.md) and the upstream model terms before distribution. [2] [3]

## References

[1] [Supertonic official repository](https://github.com/supertone-inc/supertonic)

[2] [Supertonic Python SDK and local server documentation](https://github.com/supertone-inc/supertonic-py)

[3] [Supertonic 3 model card](https://huggingface.co/Supertone/supertonic-3)
