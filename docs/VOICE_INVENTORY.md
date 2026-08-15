# Nastech Compact Voice Inventory and Accent Support Policy

Nastech Compact TTS is published by **Nastech Research** and uses one local Supertonic 3 ONNX model family. This document separates the voices currently shipped in the local model cache from regional-accent targets that require a consented, licensed custom voice-style profile and recorded verification.

> **Truthful current state:** the installed local Supertonic 3 package contains **10 preset styles**—`M1`–`M5` and `F1`–`F5`. It does **not** ship 32 verified British voices, 20 verified American voices, a generic “African accent,” or a Jamaican voice. Those counts and regional targets are retained as named expansion requirements, not presented as current product inventory. [1] [2]

## Verified local presets

The upstream Python reference documents ten built-in voices, and the local deployment cache contains matching JSON style assets. Nastech exposes the identifiers without inventing national, ethnic, or regional labels for them. [1]

| IDs | Count | Local availability | Accent claim |
|---|---:|---|---|
| `M1`–`M5` | 5 | Verified local preset-style assets | No British, American, African, Jamaican, or other regional-accent label is asserted |
| `F1`–`F5` | 5 | Verified local preset-style assets | No British, American, African, Jamaican, or other regional-accent label is asserted |
| Total | **10** | Verified in the Supertonic 3 cache | Speaker-style labels only |

## Requested expansion catalog

The following profiles are **planned**. A profile becomes available only after a Nastech Research review confirms a lawful source style, documented consent or appropriate authorization, model and license compatibility, a verified import into the same Supertonic model family, and English intelligibility plus digital-audio checks. A regional label must describe the verified profile’s approved self-identification and linguistic evaluation; it must never be guessed from a voice or used to portray a protected group as a single accent.

| Requested family | Target count | Current state | Promotion gate |
|---|---:|---|---|
| British English | 32 | `planned/consent-and-evaluation-required` | 32 individually consented and licensed profiles, each with an English regression fixture, a local style import, and documented regional/dialect review |
| American English | 20 | `planned/consent-and-evaluation-required` | 20 individually consented and licensed profiles with the same local synthesis, audio-level, and intelligibility evidence |
| African English regional profiles | Not numerically specified | `planned/region-specific-definition-required` | Nastech Research must define a precise regional English target with representative, authorized speakers and independent linguistic review; “African accent” is too broad to be one voice claim |
| Jamaican English regional profiles | Not numerically specified | `planned/consent-and-evaluation-required` | Authorized Jamaican English profile(s), approved vocabulary/pronunciation handling, independent review, and local release-fixture evidence |

## Technical and licensing boundary

Supertonic 3 supports English text locally, but its open package ships fixed preset styles rather than a documented national-accent catalog. The upstream Python documentation states that custom voice-style JSON can be loaded from a Voice Builder export or other style JSON; the upstream project also cautions that official Voice Builder access ends after August 31, 2026. Nastech will therefore accept only a locally importable, reviewed profile and will not rely on an ongoing hosted service for runtime synthesis. [2] [3]

> **No accent is simulated by spelling tricks or stereotypes.** Nastech’s `voice` parameter selects an installed style. It does not claim to transform a preset voice into British, American, African, Jamaican, or any other accent.

## Release acceptance for a new profile

Every future profile must receive a stable Nastech ID, provenance/consent record kept outside the Git repository, a versioned non-sensitive manifest, one authorized English text fixture, deterministic WAV-level verification, and human review for intelligibility, regional appropriateness, and unintended imitation. No profile is promoted because a reviewer merely perceives an accent.

## References

[1] [Supertonic Python SDK: Voices](https://supertone-inc.github.io/supertonic-py/voices/)

[2] [Supertonic Python SDK: custom voice-style JSON usage](https://supertone-inc.github.io/supertonic-py/)

[3] [Supertonic official repository: service and Voice Builder notice](https://github.com/supertone-inc/supertonic)
