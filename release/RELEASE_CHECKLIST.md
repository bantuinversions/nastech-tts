# Nastech Compact v0.6 Release Checklist

## Required Verification

| Check | Command or evidence | Expected result |
|---|---|---|
| Formatting and static analysis | `make lint` | No formatting or Ruff failures |
| Deterministic Python quality suite | `pytest -q` | **72 tests passing** without model download, GPU, cloud TTS credentials, or network service |
| JSON and YAML contracts | `make contract` | Agent catalog, OpenAPI paths, project summary, workflow, issue-form, labels, and Dependabot contracts validate |
| Source and wheel build | `make build` | `nastech_tts-0.6.0.tar.gz` and `nastech_tts-0.6.0-py3-none-any.whl` build successfully |
| Distribution metadata | `python -m twine check dist/*` | Package long description and metadata validate |
| OpenAPI contract | `make openapi && git diff --exit-code -- docs/openapi.json` | Intentional API changes are represented in the checked-in schema |
| Deployment budget | `make budget` | Full bundle remains at or below 1 GiB |
| Real local synthesis | `nastech-tts synthesize examples/compact_agent_story.xml --output output/release_story.wav` | Local CPU returns a valid 44.1 kHz WAV and manifest |
| Live local agent API | `POST /v1/agent/speech`, diagnostics, warm-up, and cache-clear smoke tests | Local endpoint returns expected status and WAV response |

## Before Publishing to GitHub

Confirm that `git status` contains no generated credentials, bearer tokens, private audio, model caches, voice-style JSON files not intended for distribution, or customer text. Preserve `LICENSE`, `NOTICE.md`, and the Supertonic model-license boundary. Commit the generated OpenAPI schema, project summary YAML, agent tool catalog, and any intentionally updated benchmark or budget evidence.

Review the GitHub Actions workflows and make sure the repository’s Actions permissions allow the release workflow to create only a **draft** release. The draft must be reviewed for checksums, license notice, changelog, release notes, and artifact contents before publication.

## Before Publishing to PyPI

Run:

```bash
make verify
python -m twine check dist/*
```

Publish the Nastech control package only. Do not distribute Supertonic model weights unless the upstream OpenRAIL-M terms and every host’s distribution requirements permit that method. Use a dedicated PyPI token configured outside source control; never place it in issues, pull requests, the project summary, or workflow files.

## Before Publishing an npm Client

Generate or maintain an HTTP client from `docs/openapi.json`. The npm package should call the local Nastech API and should not embed Python, model weights, local cache paths, or user audio. Surface the five agent operations: compile, synthesis, diagnostics, warm-up, and cache clear.

## Before Production Deployment

Set `NASTECH_API_KEY` outside source control. Use TLS and a reverse proxy for Internet-facing use. Choose a CPU profile deliberately, run the cache-bypassing benchmark against the target machine, and inspect `GET /v1/runtime/diagnostics` after warm-up. Perform a listening acceptance test for every release-dependent tag that product material intends to advertise.
