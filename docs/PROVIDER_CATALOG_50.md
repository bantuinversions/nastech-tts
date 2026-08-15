# Nastech TTS Provider Catalog: 50 Integration Targets

Nastech TTS is the product identity. It uses a **provider mixer**: one request contract, one NastechML compiler, one audio-quality gate, and a provider router that can select an activated engine. A catalog entry is **not** an assertion that the provider is installed, licensed for a particular use, locally bundled, configured with credentials, or eligible for automatic routing.

> **Core deployment rule:** the default Nastech build remains local-first and network-disabled. It activates only the configured providers whose combined runtime, model assets, and release evidence fit the **1 GiB** deployment contract. The other catalog entries are inert integration targets until separately installed, reviewed, and enabled.

## Activation states

| State | Meaning |
|---|---|
| `active/local` | Installed and validated for real local synthesis in this Nastech deployment. |
| `adapter/available` | A Nastech adapter contract exists; the provider still needs installation, configuration, and acceptance tests. |
| `planned/license-review` | Listed as a research target only; license, model, security, size, and quality review are unfinished. |
| `planned/credential-required` | A managed provider target; disabled by default and requires an account, secret, cost approval, and network opt-in. |

## Catalog

| # | Nastech provider ID | Provider family or target | Route type | State | Activation boundary |
|---:|---|---|---|---|---|
| 1 | `nastech-native-onnx` | Nastech native local ONNX engine | Local Python | `active/local` | Current verified local runtime; provider name is not the Nastech product brand. |
| 2 | `kokoro-local` | Kokoro 82M | Local Python | `adapter/available` | Separate optional environment and model-budget verification required. [1] |
| 3 | `piper-native` | Piper native binary | Local command | `adapter/available` | Voice model licence and executable validation required. [2] |
| 4 | `coqui-cli` | Coqui TTS command line | Local command | `adapter/available` | Must be installed in a compatible isolated environment. [3] |
| 5 | `coqui-python` | Coqui TTS Python API | Local Python | `adapter/available` | Python/runtime compatibility and exact model licence are required. [3] |
| 6 | `coqui-server` | Coqui TTS local HTTP server | Local HTTP | `adapter/available` | Local endpoint must be explicitly configured; no automatic server launch. [3] |
| 7 | `coqui-container` | Coqui CPU container | Local command | `adapter/available` | Container image digest, network policy, and deployment budget required. [3] |
| 8 | `coqui-xtts-v2` | Coqui XTTS v2 profile | Local Python | `planned/license-review` | Custom-voice consent, model terms, and size review required. [3] |
| 9 | `coqui-yourtts` | Coqui YourTTS profile | Local Python | `planned/license-review` | Model terms, consent, and CPU-quality evidence required. [3] |
| 10 | `coqui-vits` | Coqui VITS profile | Local Python | `planned/license-review` | Exact model and voice licence review required. [3] |
| 11 | `coqui-fairseq-vits` | Coqui Fairseq/MMS profile | Local Python | `planned/license-review` | Language/model terms and size review required. [3] |
| 12 | `coqui-bark` | Coqui Bark profile | Local Python | `planned/license-review` | Model terms, expressiveness evaluation, and safety review required. [3] |
| 13 | `coqui-tortoise` | Coqui Tortoise profile | Local Python | `planned/license-review` | CPU latency and model-size evidence required. [3] |
| 14 | `melo-local` | MeloTTS | Local Python | `adapter/available` | English locale selection, weights, and package budget required. [4] |
| 15 | `f5-local` | F5-TTS | Local Python | `planned/license-review` | Exact checkpoint licence and CPU feasibility required. [5] |
| 16 | `styletts2-local` | StyleTTS 2 | Local Python | `planned/license-review` | Model licensing, voice-consent, and CPU evidence required. |
| 17 | `chatterbox-local` | Chatterbox | Local Python | `planned/license-review` | Checkpoint licence and resource validation required. |
| 18 | `parler-local` | Parler-TTS | Local Python | `planned/license-review` | Checkpoint terms and CPU evaluation required. |
| 19 | `fish-speech-local` | Fish Speech | Local Python | `planned/license-review` | Checkpoint terms, consent, and deployment evidence required. |
| 20 | `openvoice-local` | OpenVoice | Local Python | `planned/license-review` | Voice-conversion consent controls and licence review required. |
| 21 | `cosyvoice-local` | CosyVoice | Local Python | `planned/license-review` | Model terms and hardware feasibility required. |
| 22 | `gpt-sovits-local` | GPT-SoVITS | Local Python | `planned/license-review` | Consent, model terms, and safe reference-audio handling required. |
| 23 | `index-tts-local` | IndexTTS | Local Python | `planned/license-review` | Model licence and CPU acceptance evidence required. |
| 24 | `qwen3-tts-local` | Qwen TTS family | Local Python | `planned/license-review` | Checkpoint licence, size, and English test evidence required. |
| 25 | `e2-tts-local` | E2-TTS | Local Python | `planned/license-review` | Checkpoint licence, resource profile, and consent review required. |
| 26 | `bark-local` | Bark | Local Python | `planned/license-review` | Model terms, content controls, and CPU evaluation required. |
| 27 | `tortoise-local` | Tortoise TTS | Local Python | `planned/license-review` | Model terms and latency budget required. |
| 28 | `sherpa-onnx-local` | Sherpa ONNX TTS | Local command | `planned/license-review` | Selected model and ONNX runtime validation required. |
| 29 | `rhvoice-local` | RHVoice | Local command | `planned/license-review` | Voice-data licences and packaging review required. |
| 30 | `mimic3-local` | Mimic 3 | Local HTTP | `planned/license-review` | Local endpoint, voice licence, and version pinning required. |
| 31 | `marytts-local` | MaryTTS | Local HTTP | `planned/license-review` | Java runtime and voice licence verification required. |
| 32 | `festival-local` | Festival | Local command | `planned/license-review` | Voice-data licensing and quality acceptance required. |
| 33 | `espeak-ng-local` | eSpeak NG | Local command | `planned/license-review` | Distribution terms and quality-positioning review required. |
| 34 | `openai-speech` | OpenAI Speech API | Managed HTTP | `planned/credential-required` | Explicit network opt-in, API secret, cost approval, and AI-voice disclosure required. [6] |
| 35 | `azure-speech` | Azure Speech | Managed HTTP | `planned/credential-required` | Region, subscription key, configured voice, and cost approval required. [7] |
| 36 | `google-cloud-tts` | Google Cloud Text-to-Speech | Managed HTTP | `planned/credential-required` | Service account, project billing, locale and cost approval required. [8] |
| 37 | `aws-polly` | Amazon Polly | Managed HTTP | `planned/credential-required` | AWS credential, region, selected voice, and cost approval required. |
| 38 | `elevenlabs-tts` | ElevenLabs TTS | Managed HTTP | `planned/credential-required` | API key, voice rights, pricing, and provider-terms approval required. [9] |
| 39 | `cartesia-tts` | Cartesia TTS | Managed HTTP | `planned/credential-required` | API key, terms, and streaming-output validation required. |
| 40 | `deepgram-aura` | Deepgram Aura | Managed HTTP | `planned/credential-required` | API key, model selection, cost, and output validation required. |
| 41 | `playht-tts` | PlayHT | Managed HTTP | `planned/credential-required` | API credential, licensed voice, and billing approval required. |
| 42 | `resemble-tts` | Resemble AI | Managed HTTP | `planned/credential-required` | API credential, consented voice source, and billing approval required. |
| 43 | `murf-tts` | Murf API | Managed HTTP | `planned/credential-required` | API credential, voice terms, and billing approval required. |
| 44 | `speechify-tts` | Speechify API | Managed HTTP | `planned/credential-required` | API credential, voice terms, and billing approval required. |
| 45 | `lovo-tts` | LOVO API | Managed HTTP | `planned/credential-required` | API credential, voice terms, and billing approval required. |
| 46 | `wellsaid-tts` | WellSaid Labs API | Managed HTTP | `planned/credential-required` | API credential, voice terms, and billing approval required. |
| 47 | `rime-tts` | Rime API | Managed HTTP | `planned/credential-required` | API credential, voice terms, and billing approval required. |
| 48 | `sarvam-tts` | Sarvam AI speech | Managed HTTP | `planned/credential-required` | API credential, language fit, voice terms, and billing approval required. |
| 49 | `inworld-tts` | Inworld TTS | Managed HTTP | `planned/credential-required` | API credential, voice terms, and billing approval required. |
| 50 | `supertone-api` | Supertone managed speech API | Managed HTTP | `planned/credential-required` | API credential, voice terms, and billing approval required. |

## Why a mixer rather than one merged model

Nastech never combines model weights or claims to train a synthetic “combined model” merely by routing requests. The mixer normalizes requests, applies consent and privacy policy, selects **one eligible provider per render**, converts provider output into a documented Nastech delivery format, measures the result, and reports the selected adapter. Cross-provider mixing is permitted only as a deliberate, separately auditable audio-composition operation after each source render is complete.

## Budget and privacy policy

The audited current local Nastech core measures **677.73 MiB**, leaving **346.27 MiB** beneath the 1 GiB limit. Therefore, an additional local provider is activated only if a clean measurement of the combined runtime, selected model cache, and release assets stays at or below 1 GiB. Managed providers add no local model weight but are disabled unless the operator explicitly enables network providers and supplies credentials. The default request policy does not send text or audio to a network service.

## References

[1] [Kokoro official repository](https://github.com/hexgrad/kokoro)

[2] [Piper official repository](https://github.com/rhasspy/piper)

[3] [Coqui TTS official repository](https://github.com/coqui-ai/TTS)

[4] [MeloTTS official repository](https://github.com/myshell-ai/MeloTTS)

[5] [F5-TTS official repository](https://github.com/SWivid/F5-TTS)

[6] [OpenAI Text-to-Speech documentation](https://developers.openai.com/api/docs/guides/text-to-speech)

[7] [Azure Speech REST Text-to-Speech documentation](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/rest-text-to-speech)

[8] [Google Cloud Text-to-Speech documentation](https://cloud.google.com/text-to-speech)

[9] [ElevenLabs Text-to-Speech API](https://elevenlabs.io/text-to-speech-api)
