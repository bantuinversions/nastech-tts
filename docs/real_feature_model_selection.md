# Nastech Real-Feature Model Selection

## Selected Production Foundation: Fish Audio S2 Pro

Nastech will use **Fish Audio S2 Pro** as its full-feature production foundation. Unlike compact TTS models that only offer limited or inconsistent vocal-effect tags, Fish S2 Pro documents fine-grained inline natural-language controls for emotion and paralinguistic events, including `[angry]`, `[sad]`, `[excited]`, `[laughing]`, `[sigh]`, `[whisper]`, `[shouting]`, `[clearing throat]`, and free-form behavior descriptions. It also provides an official local HTTP server and an official cloud API, enabling actual calls from agent workflows. [1] [2] [3]

## Decision Rationale

| Requirement | Fish S2 Pro evidence | Nastech implementation |
|---|---|---|
| Real emotional control | Official repository documents 15,000+ inline natural-language tags and examples for named emotions and vocal actions. | Nastech compiles expressive directives into Fish bracket tags without pretending that cues are merely text. |
| Agent calls | Official local server exposes `GET /v1/health` and `POST /v1/tts`; the cloud service publishes an OpenAPI schema. | Nastech exposes its own agent-safe REST API and can route calls to a self-hosted Fish server or official cloud endpoint. |
| Voice capabilities | Official docs support reference voices, multi-speaker synthesis, and multi-turn generation. | Nastech request schema supports one or more reference IDs while retaining speaker tokens. |
| Production controls | Official cloud endpoint supports speed, volume, format, latency, and quality-related request options. | Nastech forwards validated controls and writes a per-request behavior manifest. |

## Size and Deployment Boundary

Fish S2 Pro is a **4B-parameter** model, so it is not a roughly 400 MB edge model. A genuine real-feature model with documented broad emotional and event controls requires a GPU-capable serving environment. The smaller S1-mini is 0.5B but uses a CC-BY-NC-SA-4.0 license and is therefore unsuitable as the general Nastech product base. [1] [4]

Supertonic remains a compact approximately 400 MB, 99M-parameter edge option with documented local HTTP serving and a limited tag set, but its own public issue discussion reports inconsistent effects for several tags. It is not selected as Nastech’s real-feature production foundation. [5]

## Licensing and Safety Boundary

The Fish Speech repository and S2 weights are released under the Fish Audio Research License. Nastech must preserve this notice, must not bundle the S2 weights, and must validate the license for the user’s intended deployment before commercial use. Nastech ships an integration gateway, not redistributed model weights.

## References

[1] [Fish Speech official repository and S2 Pro capabilities](https://github.com/fishaudio/fish-speech)

[2] [Fish Speech official local server documentation](https://speech.fish.audio/server/)

[3] [Fish Audio official `/v1/tts` OpenAPI documentation](https://docs.fish.audio/api-reference/endpoint/openapi-v1/text-to-speech)

[4] [Fish Audio S1-mini model card and license](https://huggingface.co/fishaudio/openaudio-s1-mini)

[5] [Supertonic official expression-tag discussion](https://github.com/supertone-inc/supertonic/issues/155)
