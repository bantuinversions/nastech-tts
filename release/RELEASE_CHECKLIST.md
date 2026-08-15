# Nastech Compact v0.8 Release Checklist

## Required Verification

| Check | Command or evidence | Expected result |
|---|---|---|
| Formatting and static analysis | `make lint` | No formatting or Ruff failures |
| Deterministic Python quality suite | `pytest -q` | **90 tests passing** without model download, GPU, cloud TTS credentials, or a live network service |
| Capability catalog | `make catalog && git diff --exit-code -- docs/CAPABILITY_CATALOG_500.md` | Exact 500-record roadmap is current and generation is reproducible |
| JSON and YAML contracts | `make openapi && make contract` | Ten agent tools, portability routes, project summary, workflow templates, and daily CI schedule validate |
| Source and wheel build | `make build` | `nastech_tts-0.8.0.tar.gz` and `nastech_tts-0.8.0-py3-none-any.whl` build successfully |
| Distribution metadata | `python -m twine check dist/*` | Package long description and metadata validate |
| Deployment budget | `make budget` | Full bundle remains at or below 1 GiB |
| Real local synthesis | `nastech-tts synthesize examples/compact_agent_story.xml --output output/release_story.wav --clean` | Local CPU returns valid 44.1 kHz WAV, manifest, and cleanup report |
| Local cleanup smoke test | `nastech-tts clean output/release_story.wav --output output/release_story.cleaned.wav` | Mono signed-16-bit PCM WAV remains readable and cleanup report is auditable |
| Agent API smoke test | Plan, standard speech, chunked transfer, cleanup, platform inventory, platform preflight, diagnostics, warm-up, and cache-clear endpoints | Local endpoint contracts and headers match OpenAPI/agent catalog |
| CPU portability evidence | `nastech-tts platforms` and `nastech-tts preflight python-cpu` | CPU profile reports as verified only after local runtime acceptance |
| GPU/mobile/browser boundary | `nastech-tts preflight python-cuda`, `android-nnapi`, and `web-webgpu` | Profiles remain planned until actual target-provider/device execution evidence is committed |
| Daily workflow | `.github/workflows/ci.yml` schedule | Full deterministic quality workflow is scheduled for 03:17 UTC |

## Before Publishing to GitHub

Confirm that no generated credentials, bearer tokens, private audio, model caches, customer text, or release-local debugging artifacts are committed. Preserve `LICENSE`, `NOTICE.md`, Supertonic model-license boundaries, `project-summary.yml`, `docs/openapi.json`, `docs/CAPABILITY_CATALOG_500.md`, and `agent_tools/nastech_tts_tool.json`.

Review GitHub Actions permissions. The release workflow must create only a **draft** release. Inspect checksums, distribution contents, license notices, changelog, and generated release notes before public publication.

## Before Publishing to PyPI

Run:

```bash
make verify
python -m twine check dist/*
```

Publish the Nastech control package only. Do not distribute Supertonic weights unless upstream OpenRAIL-M terms and the intended distribution method permit it. Use a dedicated PyPI token stored outside source control.

## Before Publishing an npm Client

Generate or maintain an HTTP client from `docs/openapi.json`. The client must expose planning, compilation, synthesis, post-synthesis chunked delivery, PCM cleanup, platform inventory, target preflight, diagnostics, warm-up, and cache clear. It must not embed Python, model weights, cache paths, user audio, or credentials.

## Before Platform Claims or Production Deployment

Set `NASTECH_API_KEY` outside source control. Use TLS and a reverse proxy for Internet-facing use. Choose a CPU profile deliberately, warm the runtime, inspect diagnostics, and run a cache-bypassing benchmark against the target host.

Do not promote GPU, Android, iOS, or browser profiles from planned to verified based only on runtime-provider discovery. The target must execute real Supertonic synthesis and record active provider, audio validity, latency, memory, package size, and relevant device/thermal evidence. Describe chunked delivery as post-synthesis transfer, not model-inference streaming. Apply PCM cleanup only to eligible mono 16-bit WAVs and do not market it as voice conversion or a second-model feature.
