# Changelog

## 0.12.0 — 2026-08-17

Nastech Compact adds a lazy Bantu model-pack registry. Startup performs zero optional downloads and zero optional model loads; an operator can inspect pack states and explicitly download one requested language through REST, CLI, or agent tools. The `mms-lazy` provider loads one requested local MMS model at a time, evicts the previous model from RAM, and uses the shared CPU/GPU hardware planner.

The registry maps verified public MMS routes for Luganda, Runyankole, Acholi, Ateso, Kiswahili, Kinyarwanda, Kirundi, Gikuyu, Sepedi, Tshivenda, Xitsonga, Shona, and Chichewa/Nyanja. Targets without a verified checkpoint—such as isiZulu—remain truthful `no-verified-pack` entries; Nastech never downloads a different language under the requested name. MMS packs remain external CC-BY-NC-4.0 assets and are not bundled into the Apache-2.0 compact core.

The release contains **135 passing deterministic tests**, regenerated OpenAPI and agent contracts, one-language cache/eviction tests, and no-startup-download safeguards. The compact budget remains measured separately from all optional model packs.

GitHub Actions now audits all 23 registered language targets and runs a parallel five-minute native-language story matrix for English plus the 13 verified Bantu packs. The English story covers Nastech Research branding, emotional transitions, and all nine registered non-verbal cues: laugh, chuckle, sigh, cough, sniffle, groan, yawn, gasp, and cry. Each matrix job validates duration, non-silence, sample rate, clipping, checksums, and uploads WAV/report artifacts to the draft release. Planned languages remain explicit failures rather than substitutions.

## 0.11.0 — 2026-08-16

Nastech Compact now reports an automatic hardware plan through the package and REST diagnostics. It detects CPU count, host RAM, CUDA availability, ONNX providers, safe precision, bounded concurrency, and batch recommendations; `NASTECH_DEVICE=gpu` fails closed unless a real CUDA path is available. The compact CPU core remains verified and does not require a GPU.

The optional Bantu runtime installer and local inference harness now support 11 public MMS-TTS packs—Luganda, Runyankole, Acholi, Ateso, Kiswahili, Kinyarwanda, Kirundi, Gikuyu, Xitsonga, Shona, and Chichewa/Nyanja—stored outside the compact core. All 11 generated non-silent, unclipped CPU WAV smoke outputs on the current host. This is local generation evidence, not native-speaker or production-quality certification; MMS model use remains bounded by its CC-BY-NC-4.0 licence.

The repository remains under the 1 GiB compact deployment limit at approximately 699.10 MiB, and the deterministic suite now contains **129 passing tests**. The Common Voice Luganda training corpus and 30-minute generated WAV remain external research/release assets rather than source-package contents.

## 0.10.1 — 2026-08-15

This patch makes the Luganda `configured-local` registry test explicitly provide the required WAV normalizer command, matching the provider adapter’s documented activation gate in clean CI environments. No language-support claim or model/provider boundary changed.

## 0.10.0 — 2026-08-15

Nastech Compact adds a 23-target **Bantu-language registry**, language-aware NastechML compilation, API and CLI inventory/preflight commands, and a 59-entry strict no-fallback provider catalog. English remains the verified native local synthesis path. Luganda now has an explicitly configured optional local OpenBible VITS route exposed only as a `configured-local` technical preview; it is not claimed as native-speaker verified and remains subject to licence, repeatability, and competent Luganda review gates.

This release also records real local expressive English evidence for sadness, anger, happiness, sigh, cough, and laugh markup, plus isolated local Luganda technical-preview fixtures. The tag-only audio workflow regenerates the expressive English WAV and its compiler/level reports. Deterministic coverage now contains **125 passing tests**; the measured compact core remains below the 1 GiB deployment budget, excluding the separately managed Luganda language pack.

## 0.9.1 — 2026-08-15

Nastech Compact adds a reproducible **real local 30-minute continuity test**. The generator renders unique NastechML narrative segments locally, cleans every PCM segment, and joins the resulting frames only up to the requested duration; it does not loop, pad, or time-stretch audio. The completed F1 continuity run produced exactly 1,800 seconds of mono 16-bit PCM 44.1 kHz audio with no digital full-scale clipping. Four short verified preset-style auditions—M1, M3, F1, and F3—are also generated as release evidence without regional-accent claims.

The tag-only release-audio workflow now regenerates and uploads the 30-minute continuity artifact, its source markup, four auditions, and the complete machine-readable manifest alongside the existing expressive fixture suite. The long WAV is a release asset rather than Git history, keeping source clones practical while preserving the evidence and checksum in the draft release.

## 0.9.0 — 2026-08-15

Nastech Compact becomes a **Nastech provider-mixer platform**. Its public API, CLI, OpenAPI contract, and agent descriptor now expose a 50-target provider catalog, explicit `provider_id` selection, strict no-fallback routing, a network-disabled default, and zero-side-effect provider preflights. The verified local core remains active as `nastech-native-onnx`; every other target is accurately classified as adapter-available, licence-review, or credential-required until separately installed, reviewed, and accepted. A Coqui-compatible local command, Python, HTTP, and container path is cataloged without bundling an incompatible runtime or unreviewed model.

Nastech Research is now the clear publisher in package metadata, agent identity, governance materials, release documentation, and visual assets. The public product surface uses Nastech identity; third-party identifiers remain only in the required notice, exact dependency declarations, adapter catalog, and provider evidence.

The release adds deterministic Nastech Agent story composition, WAV-level analysis, real local release voice fixtures with manifests and checksums, and a tag-only audio workflow. The deterministic suite now contains **115 tests**. The capability roadmap is completed as a generated 500-record foundation, 500-record researched expansion, and authoritative 1,000-record master catalog.

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
