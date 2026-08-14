# Nastech TTS v0.3 Release Checklist

## Verified in This Build

| Check | Result |
|---|---|
| Unit tests | Passing without model weights or a provider credential |
| Formatting and lint | Passing for active `src/` and `tests/` code |
| Source distribution and wheel | Built as `nastech_tts-0.3.0.tar.gz` and `nastech_tts-0.3.0-py3-none-any.whl` |
| Agent OpenAPI schema | Exported to `docs/openapi.json` |
| Agent tool descriptor | Included at `agent_tools/nastech_tts_tool.json` |
| Compile-only behavior path | Verified with `examples/fish_s2_agent_story.xml` |

## Before Publishing to Git

Confirm that `git status` contains no generated credentials, voice recordings, reference IDs intended to remain private, model weights, cache directories, or customer audio. Push the tagged source and release files only after reviewing `NOTICE.md` and the Fish Audio Research License terms.

## Before Publishing to PyPI

Run:

```bash
make verify
python -m twine check dist/*
```

Publish only the Nastech gateway package; do not distribute Fish model weights or provider tokens. Update the `Documentation` and `Source` URLs in `pyproject.toml` after the user supplies the repository destination.

## Before Publishing an npm Client

Generate or hand-maintain an npm client from `docs/openapi.json`. Keep the npm package as an HTTP client for Nastech; it should not embed a provider token or attempt to ship model weights. Test it against `GET /v1/health`, `POST /v1/agent/compile`, and `POST /v1/agent/speech`.

## Before Production Deployment

Set `NASTECH_API_KEY`, use TLS and a reverse proxy, restrict the Fish provider to private networking, configure provider credentials only in a secret manager, and run a short behavior acceptance suite for the exact Fish S2 release and selected reference voices.
