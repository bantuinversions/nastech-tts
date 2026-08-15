# Nastech Compact TTS Test Matrix

## Quality Objective

Nastech Compact maintains **81 collected deterministic Python tests**. The suite is designed to run without model download, GPU access, cloud credentials, or a running network service. Real local synthesis, optional cleanup, API smoke checks, builds, and budget enforcement remain separate release-verification steps.

| Test area | Focus | Coverage style |
|---|---|---|
| NastechML | Valid English markup, all supported sounds/emotions/prosody, and invalid-document boundaries | Unit and parameterized parser tests |
| Compiler | Voice aliases, local expression-tag mapping, rate conversion, and honest fidelity reporting | Unit and parameterized compiler tests |
| CPU/runtime | Profiles, queue/cache bounds, cache keys, cache clear reporting, and status fields | Unit tests without model loading |
| Local cleanup | Readable PCM output, audit report, DC removal, near-silence gating, and unsupported-format rejection | Deterministic WAV fixture tests |
| CLI | Validation, cache management, agent tool discovery, planning, and WAV cleanup commands | CLI integration tests with local fakes/fixtures |
| Agent API | Bearer protection, planning, compilation, plain WAV, chunked transfer, cleanup input validation, diagnostics, warm-up, and capability contracts | FastAPI test-client tests |
| Machine-readable contracts | Agent catalog, OpenAPI paths, project summary, YAML templates, and daily CI schedule | `scripts/validate_project_contracts.py` |

## Required Local Commands

```bash
make lint
pytest -q
pytest --collect-only -q
make contract
make verify
```

## Runtime Verification Commands

The deterministic suite deliberately does not load the real ONNX model. Run these checks on a host with Supertonic assets when validating a release candidate.

```bash
# Inspect local CPU policy, model cache, response cache, and metrics.
nastech-tts status

# Validate and prepare an agent plan before synthesis.
nastech-tts validate examples/compact_agent_story.xml
nastech-tts plan examples/compact_agent_story.xml --delivery chunked-wav --clean

# Run one real local synthesis, then run cleanup as a separate auditable stage.
nastech-tts synthesize examples/compact_agent_story.xml --output output/release_story.wav --clean
nastech-tts clean output/release_story.wav --output output/release_story.cleaned.wav

# Measure uncached local synthesis.
NASTECH_CPU_PROFILE=balanced \
  nastech-tts benchmark examples/compact_agent_story.xml --runs 3
```

## Daily Hosted Verification

`.github/workflows/ci.yml` runs the full deterministic workflow automatically at **03:17 UTC every day** as well as on pushes, pull requests, and manual dispatch. It runs the 3-version test matrix, validates JSON/YAML contracts, regenerates the OpenAPI schema to detect drift, builds distributions, and validates package metadata. It does not incur model-download or cloud-synthesis work.

## Contribution Gate

Every behavior change must include a focused test that would have failed before the change. Changes to package contents, dependencies, or local model assets must also pass `make budget` against the intended target environment. API or agent-catalog changes must regenerate `docs/openapi.json` and pass `make contract`.
