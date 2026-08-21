# Nastech TTS Project Summary

## Purpose

Nastech TTS is an **English-only, real local expressive TTS service**. It runs Nastech Voice Core inference on the host CPU and layers stable markup, agent operations, conservative local audio hygiene, and operational safeguards around that one model family. It never routes speech text or audio through a cloud synthesis provider. [1] [2]

> **Scope boundary:** Nastech is a local application/control layer. It does not claim ownership of Nastech Voice Core model weights, merge unrelated speech models, or advertise unverified expression tags as deterministic behavior.

## Architecture

| Layer | Responsibility | Principal artifacts |
|---|---|---|
| NastechML parser | Validates English markup and produces typed speech, sound, and pause spans | `src/nastech_tts/markup.py` |
| Compiler and runtime | Builds the auditable Nastech Voice Core prompt, loads ONNX locally, and manages CPU, queue, cache, and warm-up | `src/nastech_tts/voice_core.py`, `src/nastech_tts/cpu.py` |
| Agent planning | Presents delivery choice, cleanup intent, local execution steps, and fidelity counts before synthesis | `POST /v1/agent/plan` |
| Delivery | Returns standard WAV or a completed local WAV in bounded post-synthesis chunks | `POST /v1/agent/speech`, `POST /v1/agent/speech/stream` |
| Cleanup | Performs deterministic mono PCM hygiene with no learned second model | `src/nastech_tts/cleanup.py`, `POST /v1/audio/clean` |
| Portability layer | Reports host ONNX providers and generates evidence-gated target preflight plans | `src/nastech_tts/platforms.py`, `/v1/platforms`, `/v1/platforms/preflight` |
| CLI | Provides validation, planning, compilation, synthesis, cleanup, CPU operations, portability inspection, and benchmarks | `src/nastech_tts/cli.py` |
| Quality system | Validates code, contracts, generated catalog, packaging, budget, and GitHub workflows | `tests/`, `Makefile`, `.github/`, `scripts/validate_project_contracts.py` |

## Advanced Local Operations

| Operation | What it guarantees | What it does not claim |
|---|---|---|
| Agent planning | No synthesis occurs; execution/fidelity/delivery choices are visible first | Autonomous cloud model reasoning or hidden provider delegation |
| Chunked transfer | One local WAV is sent in bounded byte chunks after completion | Incremental ONNX inference, lower model time-to-first-audio, or text-token streaming |
| PCM cleanup | DC bias removal, near-silence gating, clipping protection, and short click-safe fades | Voice conversion, speaker cloning, learned denoising, or professional mastering |
| Platform preflight | Host/provider facts and evidence requirements for CPU, GPU, Android, iOS, and browser targets | That an available provider, a listed target, or a roadmap item has executed Nastech Voice Core successfully |
| 500-capability catalog | A classified, reproducible product/research roadmap | That every catalog record is currently implemented or tested |
| Daily CI | Repeatable deterministic checks every day at 03:17 UTC | Real model downloading, cloud speech calls, or listening acceptance tests |

## Quality and Operations

The current Python suite contains **90 deterministic tests** across parser constraints, compiler fidelity, CPU configuration, cache behavior, CLI tools, conservative cleanup, agent planning, stream-transfer semantics, API authorization, platform inventory, platform preflight, and runtime contracts. The suite does not require model download, GPU access, a live web service, or cloud credentials.

| Automation | Result |
|---|---|
| Push, pull-request, manual, and daily workflow | Runs formatting, static analysis, tests across Python 3.10–3.12, generated 500-catalog drift detection, contract validation, OpenAPI drift check, builds, and Twine metadata validation |
| Daily schedule | `03:17 UTC` through `.github/workflows/ci.yml` |
| Release workflow | Builds and validates a tagged package, then creates a reviewable draft GitHub release |
| Dependabot | Proposes limited monthly Python and workflow dependency updates |
| Repository forms | Capture redacted bugs and constrained features while avoiding credentials/private audio in public issues |

The measured environment remains under the 1 GiB deployment target. The current measurement is retained in [release/CPU_OPTIMIZATION_BUDGET.json](../release/CPU_OPTIMIZATION_BUDGET.json); every target image must run its own `make budget` check.

## Maintainer Workflow

Run `make verify` before every release-oriented change. Update or add focused tests for every behavioral change. Regenerate and commit `docs/openapi.json` when API contracts change, and regenerate `docs/CAPABILITY_CATALOG_500.md` with `make catalog` when the taxonomy changes. Use `project-summary.yml` and `agent_tools/nastech_tts_tool.json` as machine-readable integration sources. A GPU, mobile, or browser profile can become verified only after target-provider evidence is committed. Tag a verified release as `vX.Y.Z`; GitHub prepares a draft release for explicit human review before public publication.

## References

[1] [Nastech Voice Core official repository](https://github.com/bantuinversions/nastech-tts)

[2] [Nastech Voice Core Python SDK](https://github.com/bantuinversions/nastech-tts)
