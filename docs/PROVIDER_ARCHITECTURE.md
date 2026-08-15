# Nastech Provider-Mixer Architecture

Nastech TTS exposes a Nastech-owned request and response contract while routing synthesis through eligible providers. It does not relabel external model weights, remove licence notices, merge third-party weights, or imply that a catalog entry is installed.

## Request path

```text
Nastech client
  -> NastechML compiler and policy checks
  -> provider registry and activation gate
  -> one selected provider adapter
  -> normalised WAV result
  -> deterministic level validation / optional cleanup
  -> Nastech delivery response and audit metadata
```

The standard request selects `nastech-native-onnx`, the locally verified engine. The provider name is intentionally Nastech-facing; the implementation’s third-party model and code notices remain in `NOTICE.md` and provider evidence rather than the normal product surface.

## Provider states

| State | Request behaviour | Network | Deployment effect |
|---|---|---|---|
| `active/local` | May render after local policy checks. | Disabled. | Included in the measured core. |
| `adapter/available` | Returns an activation plan, not audio, until installed and tested. | Disabled. | No model or dependency is bundled by the registry itself. |
| `planned/license-review` | Returns a research plan only. | Disabled. | No runtime effect. |
| `planned/credential-required` | Returns a credential and privacy plan only. | Disabled unless an operator explicitly enables it. | No local model weight is counted. |

## Selection rules

Each request carries an optional `provider_id`. A selection is accepted only when its registry entry is `active/local`, declared English-capable, and compatible with the requested operation. The router selects **one provider for synthesis**. It may never silently fall back from a requested provider to a different provider.

Cross-provider audio composition is a separate, future pipeline. It accepts completed, authorized source WAVs, records every source provider, and passes through the same WAV-level analysis. It does not blend model weights or conceal the source engines.

## Coqui-compatible route

Nastech defines a `coqui-cli` adapter contract for an operator-provided local command or container. It is not installed in the Nastech core because the upstream library’s stated Python support does not include this project’s Python 3.12 runtime and individual model licences differ. The adapter activates only in a compatible isolated environment with a pinned executable/image, a named model, auditable model terms, and a measured combined deployment size. [1]

## Coqui-Compatible Local Adapter

Nastech implements `coqui-cli` as an **operator-managed local command adapter**. It is inactive by default and does not install a package, download a model, start a service, invoke a shell, or contact a network endpoint during preflight. The operator must provision a compatible isolated environment, a reviewed local model, and a local `tts`-compatible executable before enabling it.

```bash
export NASTECH_ENABLE_COQUI_ADAPTER=1
export NASTECH_COQUI_TTS_COMMAND='/opt/nastech-coqui/bin/tts'
export NASTECH_COQUI_TTS_MODEL='tts_models/en/your-reviewed-model'
# Optional only when the selected model uses indexed speakers.
export NASTECH_COQUI_TTS_SPEAKER='0'

nastech-tts provider-preflight coqui-cli
```

When explicitly configured, `coqui-cli` becomes an active local provider and can be selected with `provider_id: "coqui-cli"`. Nastech invokes a fixed argv list with `shell=False`, writes into an isolated temporary directory, and requires the command to return a mono 16-bit PCM 44.1 kHz WAV. The adapter does not silently resample or conceal incompatible provider output. The combined runtime, model cache, release assets, exact model terms, and English/audio-level acceptance evidence must still pass before production use. [1]

## Provider preflight contract

`POST /v1/providers/preflight` returns the provider state, installation/configuration prerequisites, a privacy boundary, licence-review requirement, and budget test requirement. It never downloads a model, opens a network connection, tests a remote credential, or starts a provider executable.

## Attribution boundary

Nastech product copy, API titles, CLI names, artifacts, and client headers use **Nastech TTS**. External names appear only where needed to identify an adapter, fulfil a licence or notice obligation, or support an operator’s installation choice. Each activated third-party provider requires its own current licence and model-card review.

## References

[1] [Coqui TTS official repository](https://github.com/coqui-ai/TTS)
