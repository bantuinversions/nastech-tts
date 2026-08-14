# Nastech Compact v0.5 Release Checklist

## Verified in This Build

| Check | Result |
|---|---|
| Unit tests | 13 passing without any cloud provider credential |
| Lint and formatting | Passing for active code, tests, and release scripts |
| Real local synthesis | Verified with Supertonic ONNX on CPU |
| Live local agent API | Verified with `POST /v1/agent/speech` returning real WAV bytes |
| CPU diagnostics and warm-up | Verified through `/v1/runtime/diagnostics` and `/v1/runtime/warmup` |
| Balanced CPU benchmark | 12.04-second expressive story synthesized in 2.16 seconds mean, 0.180 real-time factor |
| Throughput benchmark | Four real requests at two scheduled clients completed at 0.758 requests/second |
| Source distribution and wheel | Build as `nastech_tts-0.5.0.tar.gz` and `nastech_tts-0.5.0-py3-none-any.whl` |
| OpenAPI schema | Exported to `docs/openapi.json` |
| Agent tool descriptor | Included at `agent_tools/nastech_tts_tool.json` |
| Deployment budget | Verified below 1 GiB by `scripts/check_compact_budget.py` |

## Before Publishing to Git

Confirm that `git status` contains no generated credentials, model caches, voice-style JSON files that should remain private, recordings, or generated customer audio. Preserve `LICENSE`, `NOTICE.md`, and the Supertonic model-license boundary. Keep the source tag and release archive aligned with the wheel, source distribution, OpenAPI schema, benchmark JSON files, and checksum manifest.

## Before Publishing to PyPI

Run:

```bash
make verify
python -m twine check dist/*
```

Publish the Nastech control package only. Do not distribute Supertonic model weights unless the upstream OpenRAIL-M terms and every host’s distribution requirements permit that deployment method. Update the placeholder package URLs after the user provides the Git destination.

## Before Publishing an npm Client

Generate or maintain an HTTP client from `docs/openapi.json`. The npm package should call the local Nastech API; it should not embed Python, model weights, or device-specific cache paths. Surface the agent speech, OpenAI-compatible speech, runtime diagnostics, and warm-up endpoints.

## Before Production Deployment

Run the 1 GiB budget checker on the actual target image or runtime. Set `NASTECH_API_KEY`, use TLS and a reverse proxy for Internet-facing access, and perform a short listening acceptance test for every non-direct tag that product material intends to advertise.

Set `NASTECH_CPU_PROFILE` deliberately, then run the cache-bypassing benchmark against the real target machine. Confirm `GET /v1/runtime/diagnostics` reports expected thread limits, bounded concurrency, cache limits, successful warm-up, and no synthesis failures before accepting production traffic.
