# Nastech TTS Release Checklist

This checklist prepares Nastech for publication after the repository, PyPI account, and optional npm scope are supplied.

## Product Identity

- [ ] Confirm the final public product name after professional trademark and domain review.
- [ ] Replace placeholder source and documentation URLs in `pyproject.toml`.
- [ ] Add the final maintainer and support contact.
- [ ] Create a public `nastech-voice-en-v1` model card when an adapter has been trained.

## Legal and Model Provenance

- [ ] Preserve `LICENSE` and `NOTICE.md` in every release archive.
- [ ] Confirm that the upstream Orpheus model terms have been accepted by the publishing account.
- [ ] Publish only adapter weights produced from licensed, consented English recordings.
- [ ] Publish a dataset card listing consent, licensing, retention, and removal procedures.
- [ ] Do not distribute any upstream model weight unless its license and access terms expressly permit it.

## Quality Gates

- [ ] Run unit tests and the Nastech behavior suite.
- [ ] Run local CPU render smoke tests for speech, laughter, cough, and pause.
- [ ] Run held-out human listening evaluation on clarity, naturalness, speaker stability, laughter, cough, anger, and sadness.
- [ ] Verify each NastechML behavior has a declared fidelity in its manifest.
- [ ] Confirm that no unsupported direct-emotion claim remains in documentation or marketing.

## Python Release

- [ ] Increment `nastech-tts` version.
- [ ] Generate source distribution and wheel using `python -m build`.
- [ ] Inspect distributions with `twine check dist/*`.
- [ ] Publish first to TestPyPI and install in a clean environment.
- [ ] Publish to PyPI only after TestPyPI smoke tests pass.

## npm Client Release

- [ ] Create a separate `@nastech/tts-client` package that calls Nastech’s documented HTTP API.
- [ ] Keep model inference out of the npm client; model execution remains server-side or local Python runtime.
- [ ] Publish to npm only after the Python API contract is versioned and tested.

## Repository Publication

- [ ] Initialize the final remote repository.
- [ ] Add a README banner, contributing guide, security policy, code of conduct, issue templates, and CI workflow.
- [ ] Exclude model files, datasets, credentials, consent records, generated audio, and cache directories via `.gitignore`.
- [ ] Add tags for the Python release and Nastech adapter version.
