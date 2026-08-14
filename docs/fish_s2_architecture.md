# Nastech Fish S2 Architecture

## Product Goal

Nastech becomes an **expressive-speech control plane** around Fish Audio S2. It is not a second TTS model and does not redistribute Fish weights. It converts structured agent intent into Fish-native inline controls, applies authentication and safety boundaries, sends a validated request to a configured Fish server, and returns audio with an auditable behavior manifest.

## Components

| Component | Responsibility | Deployment location |
|---|---|---|
| Nastech Agent Gateway | REST API, request authentication, NastechML compilation, provider selection, manifest headers | Lightweight Python service |
| Fish S2 Local Server | GPU model inference through the official Fish Speech HTTP server | GPU host with S2 checkpoints |
| Fish Cloud Provider | Optional remote API route using the official `/v1/tts` protocol | Fish Audio cloud; user-supplied key required |
| Nastech Agent Tool Schema | Machine-readable request schema for agents and workflow tools | `agent_tools/nastech_tts_tool.json` |
| NastechML Compiler | Maps emotions, events, speakers, and prosody to Fish-native tags/payload fields | Gateway package |
| Evaluation and Manifest | Records requested tags, compiled tags, provider, format, trace information, and response status | Gateway output and logs |

## Agent Request Flow

```text
Agent intent or NastechML
          |
          v
Nastech Agent Gateway
  - validates English text and allowable controls
  - applies [emotion] and [event] tags
  - selects a local or cloud Fish provider
          |
          v
Fish S2 /v1/tts
          |
          v
Audio response plus Nastech manifest
```

## NastechML to Fish S2 Mapping

| NastechML | Fish S2 compiled control | Fidelity |
|---|---|---|
| `<emotion name="sad">` | `[sad]` before the sentence | Direct provider-native semantic control |
| `<emotion name="angry">` | `[angry]` before the sentence | Direct provider-native semantic control |
| `<emotion name="happy">` | `[delight]` before the sentence | Direct provider-native semantic control |
| `<emotion name="excited">` | `[excited]` before the sentence | Direct provider-native semantic control |
| `<sound type="laugh" />` | `[laughing]` | Direct provider-native event control |
| `<sound type="sigh" />` | `[sigh]` | Direct provider-native event control |
| `<sound type="cough" />` | `[cough]` | Free-form S2 semantic tag; exact behavior must be acceptance-tested per model release |
| `<pause ms="..." />` | `[short pause]` or `[pause]` plus gateway timing metadata | Provider-native pause request |
| `<prosody rate="fast" />` | `prosody.speed` adjusted in provider request | Direct numeric control |

## Security Boundaries

The gateway accepts credentials only through environment variables. It never writes a provider token to a manifest or log. When `NASTECH_API_KEY` is set, all synthesis endpoints require a matching bearer token. The optional `traceparent` request header is forwarded to the cloud provider for observability.

## Deployment Modes

| Mode | Provider | Capability profile |
|---|---|---|
| `fish-local` | Official self-hosted Fish S2 server | Full real controls; GPU required; highest privacy |
| `fish-cloud` | Official Fish Audio API | Full real controls; requires user API key and network access |
| `compile-only` | No provider invocation | Allows agents to validate and inspect the exact provider payload before synthesis |

## References

[1] [Fish Speech S2 official capabilities](https://github.com/fishaudio/fish-speech)

[2] [Fish Speech local server documentation](https://speech.fish.audio/server/)

[3] [Fish Audio TTS API reference](https://docs.fish.audio/api-reference/endpoint/openapi-v1/text-to-speech)
