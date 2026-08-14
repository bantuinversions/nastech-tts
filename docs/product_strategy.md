# Nastech TTS Product Strategy

## Product Identity

**Nastech TTS** is an English-first, local-first expressive speech platform. Its public product identity is Nastech: package name, local API, command-line interface, configuration format, evaluation artifacts, documentation, and release process all use the Nastech name.

Nastech does **not** rebrand upstream model weights as its own. Each upstream runtime remains an optional adapter with an explicit source, license record, capability declaration, and installation requirement. This protects users from the false claim that unrelated neural models can be merged into one high-end model simply by joining their repositories.

> A “single Nastech model” is a future fine-tuned checkpoint trained from one selected base model family and licensed English data. It is not a blend of incompatible checkpoints.

## Product Scope for Version 0.2

| Area | Nastech deliverable | Product rule |
|---|---|---|
| Runtime | Python package, CLI, local API, typed settings, output manifests | All public Nastech interfaces are engine-neutral. |
| Behavior control | NastechML tags for emotion, sounds, pauses, rate, and volume | Every behavior is labelled direct, approximated, or unavailable. |
| Models | Registry plus isolated backend adapters | No model weight is copied, merged, or silently downloaded without its own upstream terms. |
| Release | PyPI-ready source package, wheel, changelog, tests, notices, and release checklist | Publishing is deferred until the user supplies a repository and package account. |
| Training | Dataset manifest format and model-training contract | Training is a GPU workload and must use licensed, consented English audio. |

## Approved Initial Adapter Strategy

| Adapter | Role | Upstream license / terms posture | Product decision |
|---|---|---|---|
| `orpheus-cpp` | Direct non-speech events such as laughter and coughs | Orpheus repository is Apache-2.0; use as an optional runtime | Included as a CPU-capable optional adapter. |
| Kokoro | Fast neutral English fallback | Kokoro repository and package are Apache-2.0 | Included as an optional adapter. |
| EmotiVoice | Future direct named-emotion adapter | Repository is Apache-2.0; official quick-start targets NVIDIA GPU and Python 3.8 | Defined as an isolated remote/GPU integration, not bundled locally. |
| Fish Audio S1 | Not bundled | Model card has gated access and CC-BY-NC-SA-4.0 terms | Explicitly excluded from a general Nastech release. |

## Brand and Legal Boundary

Public web search returns unrelated technology entities using “Nastech” or “NasTech.” This project uses the requested name as an internal software identity only. A professional trademark and domain review must be completed before public distribution, company formation, or a claim of exclusive brand ownership.

## Definition of Release-Ready

Nastech TTS 0.2 is release-ready when it has all of the following.

1. A clean installation path with pinned optional extras.
2. A stable, documented NastechML schema.
3. A local HTTP API and a Python client that share one behavior manifest format.
4. Model adapters that disclose source, license posture, capabilities, and availability.
5. Automated parser, routing, API, and packaging tests.
6. A data manifest and training contract that do not distribute unlicensed audio.
7. An Apache-2.0 project license, third-party notice file, security policy, contributing guide, changelog, and publishing checklist.

## References

[1] [Orpheus TTS official repository](https://github.com/canopyai/Orpheus-TTS)

[2] [Kokoro official repository](https://github.com/hexgrad/kokoro)

[3] [EmotiVoice official repository](https://github.com/netease-youdao/emotivoice)

[4] [Fish Audio S1 Mini model card](https://huggingface.co/fishaudio/s1-mini)
