# Changelog

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
