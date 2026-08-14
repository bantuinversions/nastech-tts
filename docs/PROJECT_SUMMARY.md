# Nastech Compact TTS Project Summary

## Purpose

Nastech Compact TTS is an **English-only, real local expressive TTS service**. It packages a stable application contract around Supertonic 3 ONNX inference while keeping every synthesis request on the host CPU. The project is designed for agent workflows that need an auditable markup compiler, predictable resource controls, and a small deployment footprint. [1] [2]

> **Project boundary:** Nastech is an application and control layer. It does not claim ownership of the upstream Supertonic model, does not merge unrelated models, and does not proxy user text to a cloud speech provider.

## Architecture

| Layer | Responsibility | Main artifacts |
|---|---|---|
| NastechML parser | Validates English markup and produces typed speech/sound/pause spans | `src/nastech_tts/markup.py` |
| Compiler | Maps the stable application syntax into an auditable Supertonic prompt and fidelity manifest | `src/nastech_tts/supertonic.py` |
| Local runtime | Loads Supertonic ONNX sessions, manages CPU policy, cache, queue, warm-up, and synthesis | `src/nastech_tts/supertonic.py`, `src/nastech_tts/cpu.py` |
| CLI | Provides validation, compilation, synthesis, status, warm-up, cache clear, benchmarking, and serving | `src/nastech_tts/cli.py` |
| Agent gateway | Exposes local REST endpoints, OpenAPI schema, and a tool catalog | `src/nastech_tts/api.py`, `docs/openapi.json`, `agent_tools/nastech_tts_tool.json` |
| Quality controls | Tests, linting, package build, budget check, CI, and release workflows | `tests/`, `Makefile`, `.github/` |

## Operations

| Operation | Why it exists |
|---|---|
| `validate` | Lets callers verify English NastechML and inspect its compilation without model loading or WAV generation |
| `compile` | Produces the local prompt and a per-span behavior/fidelity manifest |
| `synthesize` | Runs real local CPU inference and writes WAV output |
| `warmup` | Removes first-request model/session latency before production traffic |
| `status` and diagnostics | Exposes model state, effective CPU policy, cache state, and metrics |
| `clear-cache` | Frees retained WAV response bytes without discarding loaded ONNX sessions |
| `benchmark` | Measures cache-bypassing local synthesis latency and bounded parallel work |

The active CPU policy is configurable through environment variables and intentionally bounded to avoid uncontrolled oversubscription. The original measured deployment remains below the 1 GiB project cap; the exact current measurement is stored in [release/CPU_OPTIMIZATION_BUDGET.json](../release/CPU_OPTIMIZATION_BUDGET.json).

## Quality Model

The repository has a **72-test Python suite** that covers parser validity boundaries, compiler mappings and fidelity, CPU configuration, runtime cache behavior, API authentication and contracts, local tool discovery, and existing agent behavior. GitHub Actions runs formatting, static analysis, tests, distribution builds, OpenAPI export, and the strict bundle-budget check on supported Python versions.

| Repository automation | Outcome |
|---|---|
| CI workflow | Tests the active package across Python 3.10, 3.11, and 3.12; verifies the generated OpenAPI contract and size budget |
| Release workflow | Builds distributable artifacts and creates a reviewable GitHub draft release when a `v*` tag is pushed |
| Dependabot | Proposes monthly Python and GitHub Actions dependency updates |
| Issue forms and PR template | Standardizes bug reports, feature requests, security routing, test evidence, and deployment-budget review |
| Project summary YAML | Gives external tooling a compact source of truth in [`project-summary.yml`](../project-summary.yml) |

## Near-Term Maintainer Workflow

First, create a branch, run `make verify`, and update tests for every behavioral change. Next, open a pull request using the repository template and include the output of `pytest -q` and `make budget`. Finally, tag a validated release as `vX.Y.Z`; the release workflow builds artifacts and prepares a draft release for human review.

## References

[1] [Supertonic official repository](https://github.com/supertone-inc/supertonic)

[2] [Supertonic Python SDK](https://github.com/supertone-inc/supertonic-py)
