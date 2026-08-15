# Changelog

## 0.8.0 — 2026-08-15

Nastech Compact adds a provider-aware portability layer. Local users and agents can inspect host ONNX providers through `nastech-tts platforms` or `GET /v1/platforms`, and create evidence-gated CPU, GPU, Android, iOS, and browser activation plans through `nastech-tts preflight TARGET` or `POST /v1/platforms/preflight`. Python CPU remains the sole verified runtime. All accelerator and mobile targets explicitly remain planned until real target-provider synthesis, audio, latency, memory, package, and relevant device evidence are recorded.

The repository adds a generated, exact 500-record capability catalog across 20 product domains, with every record labelled by delivery/validation status instead of being falsely claimed as implemented. The deterministic suite expands to 90 tests and hosted CI now rejects drift in both the catalog and OpenAPI contract during its daily and event-driven quality workflow.

## 0.7.0 — 2026-08-15

Nastech Compact adds an auditable local agent planning endpoint, a chunked WAV-delivery endpoint with explicit post-synthesis semantics, and an opt-in deterministic local PCM cleanup stage. The cleanup tool removes DC offset, gates near-digital-silence samples, prevents clipping when necessary, and applies short edge fades; it does not introduce a second learned model or perform voice conversion.

The command-line interface adds `plan` and `clean`. The agent catalog now documents eight local operations. The Python suite expands to 81 tests, including cleanup, planning, chunked-transfer, and CLI coverage. GitHub Actions now executes the complete deterministic quality workflow daily at 03:17 UTC in addition to existing push, pull-request, and manual triggers.

## 0.6.0 — 2026-08-14

Nastech Compact now provides a GitHub-ready maintenance layer. It includes 69 deterministic Python tests across markup validation, compiler fidelity, CPU configuration, runtime cache behavior, authenticated API behavior, and agent tool discovery. The package adds `validate` and `clear-cache` CLI commands plus an authenticated `POST /v1/runtime/cache/clear` operation.

The repository adds expanded GitHub Actions CI and draft-release workflows, Dependabot configuration, YAML bug and feature issue forms, pull-request review guidance, a reusable labels taxonomy, a project summary YAML contract, API/tool catalog updates, a test matrix, and repository automation documentation.

## 0.5.0 — 2026-08-14

Nastech Compact now includes a production CPU optimization layer for the real local Supertonic ONNX runtime. It exposes validated `balanced`, `latency`, `throughput`, and `auto` CPU profiles; explicit ONNX intra-operation and inter-operation thread overrides; bounded concurrent synthesis; a queue timeout; and a bounded in-memory WAV response cache.

The local gateway adds authenticated `GET /v1/runtime/diagnostics` and `POST /v1/runtime/warmup` endpoints. The CLI adds `warmup` and cache-bypassing `benchmark` commands, including bounded parallel workload testing. A six-logical-CPU verification measured a 12.04-second expressive story at a 2.16-second mean synthesis time with the balanced profile, a 0.180 real-time factor. Four requests with two concurrent synthesis slots completed at 0.758 requests per second under the throughput policy.

## 0.4.0 — 2026-08-14

Nastech TTS has been rebuilt as **Nastech Compact**, a real local Supertonic 3 ONNX runtime with an English NastechML agent API. The external Fish S2 provider architecture, GPU requirement, and cloud-provider dependency have been removed.

The compact system performs local CPU synthesis, serves `POST /v1/agent/compile`, `POST /v1/agent/speech`, and an OpenAI-compatible alias, and produces a behavior manifest for every request. It supports documented direct Supertonic `<laugh>` and `<sigh>` expression tags while honestly marking named emotions and other native-tag requests as release-dependent until acceptance-tested.

The measured complete development deployment subtotal is **647.16 MiB**, under the **1 GiB** budget. This includes 384.83 MiB of actual Supertonic assets, 260.68 MiB of runtime dependencies, and 1.65 MiB of Nastech release assets.

## 0.3.0 — 2026-08-14

Nastech was a Fish S2 agent gateway. This architecture is superseded by v0.4.0.

## 0.2.0 — 2026-08-14

Nastech was an Orpheus experimentation foundation. This architecture is superseded by v0.4.0.

## 0.1.0 — 2026-08-14

Initial NastechML parser and expressive-speech prototype.
