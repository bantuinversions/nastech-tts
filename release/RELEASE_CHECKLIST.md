# Nastech Compact v0.4 Release Checklist

## Verified in This Build

| Check | Result |
|---|---|
| Unit tests | Passing without any cloud provider credential |
| Lint and formatting | Passing for active code, tests, and release scripts |
| Real local synthesis | Verified with Supertonic ONNX on CPU |
| Live local agent API | Verified with `POST /v1/agent/speech` returning real WAV bytes |
| Source distribution and wheel | Built as `nastech_tts-0.4.0.tar.gz` and `nastech_tts-0.4.0-py3-none-any.whl` |
| OpenAPI schema | Exported to `docs/openapi.json` |
| Agent tool descriptor | Included at `agent_tools/nastech_tts_tool.json` |
| Deployment budget | Verified below 1 GiB by `scripts/check_compact_budget.py` |

## Before Publishing to Git

Confirm that `git status` contains no generated credentials, model caches, voice-style JSON files that should remain private, recordings, or generated customer audio. Preserve `LICENSE`, `NOTICE.md`, and the Supertonic model-license boundary.

## Before Publishing to PyPI

Run:

```bash
make verify
python -m twine check dist/*
```

Publish the Nastech control package only. Do not distribute Supertonic model weights unless the upstream OpenRAIL-M terms and every host’s distribution requirements permit that deployment method. Update the placeholder package URLs after the user provides the Git destination.

## Before Publishing an npm Client

Generate or maintain an HTTP client from `docs/openapi.json`. The npm package should call the local Nastech API; it should not embed Python, model weights, or device-specific cache paths.

## Before Production Deployment

Run the 1 GiB budget checker on the actual target image or runtime. Set `NASTECH_API_KEY`, use TLS and a reverse proxy for Internet-facing access, and perform a short listening acceptance test for every non-direct tag that product material intends to advertise.
