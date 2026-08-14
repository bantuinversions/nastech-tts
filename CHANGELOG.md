# Changelog

## 0.3.0 — 2026-08-14

Nastech TTS is now a complete **Fish Audio S2 expressive-speech gateway** rather than an Orpheus CPU prototype. The project compiles English NastechML into provider-native Fish S2 controls for documented emotions and vocal events, exposes agent-first compile and synthesis endpoints, offers an OpenAI-compatible speech alias, and supports both official self-hosted Fish servers and the official Fish cloud API.

This release adds a typed Fish provider adapter, request manifests, optional gateway bearer authentication, distributed-trace forwarding, an OpenAPI contract, a machine-readable agent tool descriptor, Docker and compose deployment templates, CI configuration, release automation, and provider-free tests. Nastech does not bundle Fish weights and preserves the Fish Audio Research License boundary.

## 0.2.0 — 2026-08-14

Nastech TTS moved from a multi-engine experimentation foundation to a single-model Orpheus product architecture. This version is superseded by v0.3.0.

## 0.1.0 — 2026-08-14

Initial NastechML parser, audio assembly, behavior manifest, and local expressive-speech prototype.
