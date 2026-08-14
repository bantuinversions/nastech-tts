# Changelog

## 0.2.0 — 2026-08-14

Nastech TTS moved from a multi-engine experimentation foundation to a single-model product architecture. The selected ready-made base is the Apache-2.0 `canopylabs/orpheus-3b-0.1-ft` English fine-tune. The local runtime now uses only the corresponding CPU-compatible Orpheus path.

This release adds explicit model provenance, Nastech adapter-training strategy, a consent-aware expressive-speech manifest validator, a LoRA/QLoRA GPU training launcher, a behavior-fidelity suite, release notices, and publication checklists. The direct laugh and cough controls are supported by the selected base model. Named emotions remain correctly reported as approximated until a Nastech adapter is trained and evaluated.

## 0.1.0 — 2026-08-14

Initial NastechML parser, audio assembly, behavior manifest, and local expressive-speech prototype.
