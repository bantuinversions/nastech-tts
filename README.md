# Nastech Compact TTS

[![CI](https://github.com/bantuinversions/nastech-tts/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/bantuinversions/nastech-tts/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache--2.0-4D8CC9)](LICENSE)
[![Runtime](https://img.shields.io/badge/inference-local%20ONNX%20CPU-0B7A75)](docs/cpu_optimization.md)

**Nastech Compact TTS** is a real, local, English expressive text-to-speech service. It runs one **Supertonic 3 ONNX** model family on CPU, requires no GPU, and makes no cloud synthesis call. The project combines an auditable NastechML markup compiler, a practical local REST API, CPU optimization controls, release templates, and a 72-test quality suite. [1] [2]

> **Deployment contract:** Nastech Compact is kept below a **1 GiB full deployment budget**. The latest verified bundle is recorded in [release/CPU_OPTIMIZATION_BUDGET.json](release/CPU_OPTIMIZATION_BUDGET.json); run `make budget` on every target machine or image before production deployment.

| What it provides | Details |
|---|---|
| Local expressive speech | 44.1 kHz WAV produced by local Supertonic ONNX inference |
| English-only NastechML | Validated `<speak>`, `<emotion>`, `<sound>`, `<pause>`, and `<prosody>` markup |
| Honest expression contract | Direct documented `<laugh>` and `<sigh>` controls; release-dependent controls are explicitly marked in the manifest |
| CPU operations | Configurable ONNX threads, bounded work queue, bounded WAV cache, warm-up, diagnostics, and benchmarks |
| Agent integration | Compile, synthesis, diagnostics, warm-up, and cache-clear operations through REST and a machine-readable tool catalog |
| Quality automation | 69 Python tests, linting, package build checks, OpenAPI export, budget enforcement, dependency updates, and release workflow templates |

## Quick Start

Create an isolated environment, install the project, and inspect the local runtime configuration.

```bash
git clone https://github.com/bantuinversions/nastech-tts.git
cd nastech-tts
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

nastech-tts status
```

The first real synthesis downloads upstream Supertonic assets to the local cache. Generate the included expressive story with local CPU inference:

```bash
nastech-tts synthesize examples/compact_agent_story.xml --output output/story.wav
```

Nastech writes both `output/story.wav` and a matching auditable manifest. Use `nastech-tts validate examples/compact_agent_story.xml` to inspect markup and compilation without loading the model or generating audio.

## Local Tools

| Command | Purpose |
|---|---|
| `nastech-tts validate FILE.xml` | Validate English NastechML and emit a compilation report without synthesis |
| `nastech-tts compile FILE.xml` | Compile NastechML into the local Supertonic prompt and manifest |
| `nastech-tts synthesize FILE.xml --output FILE.wav` | Generate real local WAV audio and an audit manifest |
| `nastech-tts status` | Show model cache, CPU policy, response-cache, and synthesis metrics |
| `nastech-tts warmup` | Preload ONNX sessions and run a brief local synthesis |
| `nastech-tts clear-cache` | Clear in-memory WAV responses without unloading model sessions |
| `nastech-tts benchmark FILE.xml --runs 3` | Run cache-bypassing CPU performance measurements |
| `nastech-tts agent-tools` | Print the machine-readable agent operation catalog |
| `nastech-tts serve` | Start the local FastAPI gateway on port 8765 by default |

## CPU Profiles and Operational Controls

Nastech passes CPU policy settings to the local ONNX runtime and bounds request-level concurrency to avoid uncontrolled oversubscription. The upstream Supertonic loader enables full ONNX graph optimization. [2]

| Profile | Intended use | Default active synthesis jobs |
|---|---|---:|
| `balanced` | Small server or interactive local usage | 1 |
| `latency` | Dedicated machine serving one latency-sensitive request | 1 |
| `throughput` | Available CPU capacity for two independent clients | 2 |
| `auto` | Host-specific ONNX Runtime comparison | 1 |

```bash
export NASTECH_CPU_PROFILE=balanced
export NASTECH_WARMUP_ON_START=1
export NASTECH_API_KEY='choose-a-local-secret'
nastech-tts serve --host 127.0.0.1 --port 8765
```

| Variable | Default | Role |
|---|---:|---|
| `NASTECH_CPU_PROFILE` | `balanced` | Select `balanced`, `latency`, `throughput`, or `auto` |
| `NASTECH_INTRA_OP_THREADS` | Profile value | Explicit ONNX intra-operation worker count |
| `NASTECH_INTER_OP_THREADS` | Profile value | Explicit ONNX inter-operation worker count |
| `NASTECH_MAX_PARALLEL_SYNTHESIS` | Profile value | Maximum active synthesis jobs before queueing |
| `NASTECH_QUEUE_TIMEOUT_SECONDS` | `120` | Maximum request wait before a local capacity error |
| `NASTECH_AUDIO_CACHE_ENTRIES` | `8` | Maximum in-memory WAV cache entries |
| `NASTECH_AUDIO_CACHE_MIB` | `32` | Maximum in-memory WAV cache size |
| `NASTECH_WARMUP_ON_START` | `0` | Warm the local model at API startup when truthy |

## Agent API

The local gateway supports bearer-token protection when `NASTECH_API_KEY` is configured. `GET /v1/health` remains available for local readiness checks; all other endpoints require the configured bearer token.

| Method | Endpoint | Operation |
|---|---|---|
| `GET` | `/v1/health` | Public readiness, model state, and selected CPU policy |
| `GET` | `/v1/capabilities` | Expression contract and operational capability listing |
| `GET` | `/v1/agent/tools` | Machine-readable agent tool descriptors |
| `POST` | `/v1/agent/compile` | Compile NastechML without generating audio |
| `POST` | `/v1/agent/speech` | Generate local expressive WAV from NastechML |
| `POST` | `/v1/audio/speech` | OpenAI-compatible plain-text local synthesis alias |
| `GET` | `/v1/runtime/diagnostics` | Read CPU policy, cache state, and synthesis metrics |
| `POST` | `/v1/runtime/warmup` | Load sessions and create a short local warm-up synthesis |
| `POST` | `/v1/runtime/cache/clear` | Clear cached WAV responses without unloading ONNX |

```bash
curl --request POST http://127.0.0.1:8765/v1/agent/compile \
  --header 'content-type: application/json' \
  --header "authorization: Bearer $NASTECH_API_KEY" \
  --data @- <<'JSON'
{
  "markup": "<speak voice=\"F1\"><emotion name=\"sad\">The lantern went dark.</emotion><sound type=\"sigh\"/><emotion name=\"happy\">Then sunrise filled the room.</emotion><sound type=\"laugh\"/></speak>"
}
JSON
```

The full REST schema is [docs/openapi.json](docs/openapi.json). The agent catalog is [agent_tools/nastech_tts_tool.json](agent_tools/nastech_tts_tool.json). The compact machine-readable project template is [project-summary.yml](project-summary.yml).

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

Every compilation includes a decision manifest that classifies a requested control as `direct`, `approximated`, or `unavailable`. Do not advertise a named emotion as deterministic until it has passed a pinned-model listening acceptance test.

## Quality, CI, and Releases

The repository is configured with GitHub Actions workflows, Dependabot configuration, issue forms, a pull-request template, labels, and release safeguards. Run the same checks locally before opening a pull request:

```bash
make lint
pytest -q
make verify
```

`make verify` runs formatting, static analysis, the test suite, source and wheel builds, OpenAPI export, and the strict 1 GiB budget checker. The [`project-summary.yml`](project-summary.yml) file exposes the core runtime, quality, budget, and agent-contract facts in a reusable YAML format.

| Supporting document | Purpose |
|---|---|
| [docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md) | Product, architecture, operations, and repository roadmap summary |
| [docs/TEST_MATRIX.md](docs/TEST_MATRIX.md) | 69-test coverage matrix and local verification commands |
| [docs/cpu_optimization.md](docs/cpu_optimization.md) | Measured CPU profile evidence and operator procedure |
| [docs/api.md](docs/api.md) | Detailed REST authentication and endpoint reference |
| [deploy/DEPLOYMENT.md](deploy/DEPLOYMENT.md) | Python and Docker deployment guidance |
| [release/RELEASE_CHECKLIST.md](release/RELEASE_CHECKLIST.md) | Git, package, and production handoff checklist |

## License and Model Notice

Nastech source is licensed under Apache-2.0. Supertonic code is MIT licensed, while Supertonic 3 model weights use OpenRAIL-M. Nastech does not relabel upstream model weights as its own or bundle them into the Python distribution. Review [NOTICE.md](NOTICE.md) and the upstream model terms before distribution. [2] [3]

## References

[1] [Supertonic official repository](https://github.com/supertone-inc/supertonic)

[2] [Supertonic Python SDK and local ONNX runtime documentation](https://github.com/supertone-inc/supertonic-py)

[3] [Supertonic 3 model card](https://huggingface.co/Supertone/supertonic-3)
