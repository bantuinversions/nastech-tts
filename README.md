# Nastech Compact TTS

[![CI](https://github.com/bantuinversions/nastech-tts/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/bantuinversions/nastech-tts/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache--2.0-4D8CC9)](LICENSE)
[![Provider mixer](https://img.shields.io/badge/providers-59%20catalog-0B7A75)](docs/PROVIDER_CATALOG_50.md)

**Nastech Compact TTS** is a Nastech Research, local-first expressive text-to-speech platform. Version **0.10.1** adds a Bantu-language registry to the Nastech provider mixer, with one stable request format, **59 provider targets**, strict explicit provider and language selection, and a network-disabled default. English is verified in the compact local core; Luganda is a separately configured local technical preview. Unconfigured adapters never download a model, contact a provider, or claim to be active.

> **Deployment contract:** The full verified environment remains below the strict **1 GiB** cap. Run `make budget` for the exact target-host measurement before any production deployment.

| Capability | What it does |
|---|---|
| Local expressive synthesis | Produces real 44.1 kHz WAV through the active Nastech local provider |
| Language-aware NastechML | Validates `<speak>`, `<emotion>`, `<sound>`, `<pause>`, and `<prosody>` markup against the selected provider and language route |
| Bantu-language registry | Lists Luganda, isiZulu, isiXhosa, Sesotho, Setswana, Shona, Tshivenda, and other East/Southern African targets with explicit evidence states |
| Agent planning | Inspects compilation, fidelity, intended delivery, and optional cleanup before spending synthesis CPU time |
| Chunked transfer | Sends a completed local WAV in bounded byte chunks without falsely claiming incremental model streaming |
| Local voice cleanup | Applies conservative mono PCM hygiene: DC removal, near-silence gate, clipping protection, and edge fades |
| Operations | Bounded CPU queue, configurable threads, response cache, warm-up, diagnostics, cache management, and benchmarks |
| Portability planner | Reports registered ONNX providers and preflights CPU, GPU, Android, iOS, and browser targets with evidence requirements |
| Provider mixer | Catalogs 59 local and managed integration targets, blocks inactive selections, and preflights every activation without side effects |
| Automated quality | Deterministic tests, a Python 3.10–3.12 CI matrix, source/wheel checks, contract validation, 1,000-roadmap drift checks, and daily scheduled verification |

## Install

```bash
git clone https://github.com/bantuinversions/nastech-tts.git
cd nastech-tts
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

nastech-tts status
```

The first real synthesis prepares the configured local provider assets in the local cache. Generate the supplied expressive story locally:

```bash
nastech-tts synthesize examples/compact_agent_story.xml --output output/story.wav
```

## Verified 30-Minute Continuity Test

Nastech v0.9.1 includes a real local long-form release test. It synthesizes distinct English NastechML narrative segments locally until exactly **1,800 seconds**, applies deterministic PCM cleanup to each segment, and joins only the real PCM output. It does not loop, pad, time-stretch, or repeat a WAV. The current F1 test passed at 44.1 kHz mono 16-bit PCM with zero full-scale clipped samples. Four short M1, M3, F1, and F3 preset-style auditions are generated alongside the long-form WAV; these are style IDs, not regional-accent labels.

```bash
python scripts/generate_longform_continuity_test.py \
  --target-seconds 1800 \
  --output-dir release/longform_continuity \
  --max-chunks 96
```

The resulting 30-minute WAV is published as a release artifact rather than committed into Git history. See [release/LONGFORM_CONTINUITY_TEST.md](release/LONGFORM_CONTINUITY_TEST.md) for exact measurements, checksum, and the current listening evidence.

## Expressive Audio and Luganda Technical Preview

The neutral continuity test isolates duration and PCM stability. Its separate [expressive audition](release/multilingual_fixtures/nastech-expressive-audition.xml) exercises sadness, anger, happiness, sighing, coughing, and laughter through the real local Nastech runtime, with a generated decision manifest and deterministic WAV-level report.

Nastech also includes a real local **Luganda** technical preview through a separately installed OpenBible VITS provider pack. It uses a declared training-set speaker, performs CPU-only local inference, and normalizes the provider output to Nastech mono 16-bit PCM at 44.1 kHz. The preview is not bundled in Nastech Compact’s 1 GiB core and is not yet called a pure or quality-verified Luganda voice: that claim requires native-speaker review. The exact Bantu-language states, licence boundaries, and next evidence gates are in [BANTU_LANGUAGE_COVERAGE.md](docs/BANTU_LANGUAGE_COVERAGE.md).

```bash
nastech-tts languages
nastech-tts language-preflight lg
nastech-tts synthesize release/multilingual_fixtures/nastech-luganda-pure.xml \
  --provider coqui-luganda-openbible --language lg --output luganda.wav --clean
```

## Local CLI

| Command | Purpose |
|---|---|
| `nastech-tts validate FILE.xml --language lg` | Validate NastechML for a registered language without model loading or synthesis |
| `nastech-tts plan FILE.xml --delivery chunked-wav --clean` | Create an auditable local agent plan before synthesis |
| `nastech-tts compile FILE.xml --provider nastech-native-onnx` | Compile NastechML into an active Nastech provider request and fidelity manifest |
| `nastech-tts synthesize FILE.xml --output FILE.wav --clean` | Run local inference and optionally apply PCM cleanup |
| `nastech-tts clean INPUT.wav --output CLEAN.wav` | Clean an existing mono signed-16-bit PCM WAV without a model or cloud service |
| `nastech-tts status` / `warmup` / `clear-cache` | Inspect and operate the local ONNX runtime |
| `nastech-tts benchmark FILE.xml --runs 3` | Measure cache-bypassing CPU synthesis |
| `nastech-tts providers` | List the 59 Nastech provider targets and their truthful activation states |
| `nastech-tts languages` | List Bantu-language targets, evidence states, and provider routes |
| `nastech-tts language-preflight lg` | Inspect Luganda local-pack, licence, and native-review requirements without side effects |
| `nastech-tts provider-preflight coqui-cli` | Produce a zero-side-effect activation plan for one provider target |
| `nastech-tts agent-tools` | Print the machine-readable Nastech agent operations |
| `nastech-tts platforms` | List factual host ONNX providers and portability profiles |
| `nastech-tts preflight python-cuda` | Produce a validation-gated activation plan for a named platform target |
| `nastech-tts serve` | Run the FastAPI gateway on port 8765 by default |

## Agent API

Set a bearer token for non-health endpoints and start the local gateway:

```bash
export NASTECH_API_KEY='choose-a-local-secret'
export NASTECH_WARMUP_ON_START=1
nastech-tts serve --host 127.0.0.1 --port 8765
```

| Operation | Endpoint | Result |
|---|---|---|
| Provider inventory | `GET /v1/providers` | Full 59-entry Nastech provider catalog, state summary, and network-default policy |
| Language inventory | `GET /v1/languages` | Bantu-language targets, active/adapter/planned evidence states, and provider routes |
| Language preflight | `POST /v1/languages/preflight` | Zero-side-effect provider, licence, and native-review plan for one language target |
| Provider preflight | `POST /v1/providers/preflight` | Zero-side-effect installation, review, or credential plan for one provider target |
| Agent planning | `POST /v1/agent/plan` | Validated execution plan, selected provider, local delivery route, cleanup request, and fidelity summary |
| Standard speech | `POST /v1/agent/speech` | Completed local WAV, optionally cleaned |
| Chunked transfer | `POST /v1/agent/speech/stream` | Completed WAV transferred in caller-bounded chunks after local synthesis |
| WAV cleanup | `POST /v1/audio/clean` | Conservatively cleaned mono signed-16-bit PCM WAV |
| Plain-text alias | `POST /v1/audio/speech` | OpenAI-compatible local plain-text synthesis request |
| Portability inventory | `GET /v1/platforms` | Factual host/provider inventory plus verified and planned target profiles |
| Target preflight | `POST /v1/platforms/preflight` | Evidence-gated CPU, GPU, Android, iOS, or browser target activation plan |
| Runtime operations | `/v1/runtime/diagnostics`, `/v1/runtime/warmup`, `/v1/runtime/cache/clear` | CPU, model, queue, cache, and warm-up management |

```bash
curl --request POST http://127.0.0.1:8765/v1/agent/plan \
  --header 'content-type: application/json' \
  --header "authorization: Bearer $NASTECH_API_KEY" \
  --data @- <<'JSON'
{
  "markup": "<speak voice=\"F1\"><emotion name=\"sad\">The lantern went dark.</emotion><sound type=\"sigh\" /></speak>",
  "objective": "Prepare an auditable local narration.",
  "delivery": "chunked-wav",
  "cleanup": true
}
JSON
```

> **Streaming honesty:** The chunk endpoint produces the complete WAV first, then emits it in chunks. It reduces client-side buffering needs, but it does not reduce model time-to-first-audio and is not incremental ONNX inference.

> **Cleanup boundary:** Local cleanup is deterministic PCM hygiene, not a second learned model, voice conversion, denoising claim, or speaker-identity transformation. It supports only mono signed-16-bit PCM WAV and remains opt-in.

The complete REST schema is [docs/openapi.json](docs/openapi.json). The machine-readable agent catalog is [agent_tools/nastech_tts_tool.json](agent_tools/nastech_tts_tool.json). The project summary is [project-summary.yml](project-summary.yml).

## Cross-Platform Contract and 1,000-Capability Roadmap

**Python CPU is the only currently verified Nastech runtime profile.** The platform interface lists CUDA, TensorRT, DirectML, OpenVINO, Android CPU/XNNPACK, Android NNAPI, iOS CoreML, and browser WebGPU as planned targets. A target is never marked verified merely because an ONNX provider is registered: it requires a real active-Nastech-provider synthesis run on the target, audio validity, latency/memory/package evidence, and applicable device/thermal observations. ONNX Runtime documents that execution-provider performance and operator partitioning are model and device dependent. [1] [2]

```bash
nastech-tts platforms
nastech-tts preflight python-cuda
nastech-tts preflight android-nnapi
```

The repository includes the authoritative [1,000-capability catalog](docs/CAPABILITY_CATALOG_1000.md), comprising the [500-record foundation](docs/CAPABILITY_CATALOG_500.md) and [500-record researched expansion](docs/CAPABILITY_EXPANSION_500.md). It is a classified product and research roadmap, not a claim that all records are active. The [provider catalog](docs/PROVIDER_CATALOG_50.md), [provider architecture](docs/PROVIDER_ARCHITECTURE.md), [voice inventory policy](docs/VOICE_INVENTORY.md), [cross-platform research notes](docs/cross_platform_research_notes.md), and [portability architecture](docs/PORTABILITY_ARCHITECTURE.md) define activation evidence and claim boundaries.

## NastechML Example

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

Every compilation emits a decision manifest that classifies requested controls as `direct`, `approximated`, or `unavailable`. `<laugh>` and `<sigh>` are documented direct controls. Release-dependent controls are retained as explicit requests rather than falsely advertised as deterministic.

## Daily CI and Releases

GitHub Actions runs the complete deterministic quality workflow on push, pull request, manual launch, and **daily at 03:17 UTC**. The scheduled run checks formatting, static analysis, all tests, generated 500+500+1,000 roadmap drift, JSON/YAML contracts, OpenAPI drift, source/wheel builds, and package metadata. It does not download models or use a managed TTS service. Tag-only audio verification separately renders and validates real local release fixtures.

```bash
make lint
pytest -q
make verify
```

| Supporting document | Purpose |
|---|---|
| [docs/api.md](docs/api.md) | Detailed agent, stream, cleanup, authentication, and runtime API reference |
| [docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md) | Product, architecture, operations, and maintenance summary |
| [docs/TEST_MATRIX.md](docs/TEST_MATRIX.md) | Deterministic test coverage and local verification commands |
| [docs/REPOSITORY_AUTOMATION.md](docs/REPOSITORY_AUTOMATION.md) | CI, daily schedule, release workflow, Dependabot, and template guide |
| [docs/cpu_optimization.md](docs/cpu_optimization.md) | CPU profiles, measured evidence, and operational guidance |
| [docs/CAPABILITY_CATALOG_1000.md](docs/CAPABILITY_CATALOG_1000.md) | Authoritative 1,000-record classified capability roadmap |
| [docs/PROVIDER_CATALOG_50.md](docs/PROVIDER_CATALOG_50.md) | Original 50-provider research catalog; runtime inventory is extended to 59 targets |
| [docs/BANTU_LANGUAGE_COVERAGE.md](docs/BANTU_LANGUAGE_COVERAGE.md) | Luganda and major East/Southern Bantu-language evidence registry and activation gates |
| [docs/PROVIDER_ARCHITECTURE.md](docs/PROVIDER_ARCHITECTURE.md) | Provider mixer, no-fallback routing, and attribution boundary |
| [docs/VOICE_INVENTORY.md](docs/VOICE_INVENTORY.md) | Verified local voices and consent-first regional voice roadmap |
| [docs/PORTABILITY_ARCHITECTURE.md](docs/PORTABILITY_ARCHITECTURE.md) | CPU/GPU/mobile/browser evidence rules and target contract |
| [docs/cross_platform_research_notes.md](docs/cross_platform_research_notes.md) | Research evidence and current platform constraints |
| [deploy/DEPLOYMENT.md](deploy/DEPLOYMENT.md) | Python and Docker deployment guide |

## Licence and Provider Notice

Nastech source is Apache-2.0. Each provider, model, voice asset, and managed service has independent licence, consent, attribution, privacy, and use restrictions. Nastech does not relabel third-party weights as its own or bundle unreviewed provider assets into its Python distribution. Review [NOTICE.md](NOTICE.md), the [provider catalog](docs/PROVIDER_CATALOG_50.md), and the exact provider/model terms before activation or distribution.

## References

[1] [ONNX Runtime execution providers](https://onnxruntime.ai/docs/execution-providers/)

[2] [ONNX Runtime mobile deployment guide](https://onnxruntime.ai/docs/tutorials/mobile/)
