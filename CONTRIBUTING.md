# Contributing to Nastech TTS

Nastech accepts contributions that improve the single-model runtime, NastechML behavior schema, evaluation tooling, data validation, packaging, and documentation. Contributors must not submit proprietary model weights, scraped voices, recordings without documented consent, credentials, or copyrighted datasets without clear redistribution and training rights.

All code contributions should include focused tests and must preserve the single-model boundary: Nastech v0.2 modifies the selected Orpheus model family through an adapter rather than mixing unrelated checkpoints. Proposed changes that add a new behavior must document its NastechML syntax, dataset-label requirements, expected fidelity, and evaluation criteria.

Before opening a pull request, install the development dependencies, run the unit suite, run the behavior fixture suite, and confirm that generated assets and caches are excluded from the change. Model adapters and dataset manifests require a model card or dataset card detailing provenance and consent.
