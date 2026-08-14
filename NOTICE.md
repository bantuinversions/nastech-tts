# Nastech TTS Notices

Copyright 2026 Nastech contributors.

Nastech TTS source code is distributed under the Apache License, Version 2.0. Nastech is an integration and control-plane project: it does **not** redistribute, rename, train, or claim ownership of upstream Fish model weights.

## Upstream Model and Runtime Attribution

| Item | Source | License / access note | Nastech use |
|---|---|---|---|
| Fish Audio S2 Pro | `fishaudio/s2-pro` | Fish Audio Research License; review upstream terms before any deployment or commercial use | Selected real-feature expressive-speech provider. |
| Fish Speech source | `fishaudio/fish-speech` | Fish Audio Research License | Reference local server and self-hosted provider implementation. |
| Fish Audio cloud API | `https://api.fish.audio` | Provider terms and user API key required | Optional managed provider for the Nastech gateway. |
| FastAPI / Uvicorn / HTTPX | Python dependencies | Their respective upstream licenses | Gateway API and provider HTTP client. |

Nastech does not bundle Fish model weights. Users download and run model files only through upstream-approved mechanisms and remain responsible for accepting all applicable access terms.

## Nastech Integration Attribution

NastechML maps structured English speech intent to Fish S2 inline controls. Nastech must preserve original upstream attributions, provider model identifiers, and request fidelity notes when producing manifests. The current implementation distinguishes documented provider-native behavior tags from free-form controls that require release-specific acceptance testing.

## Voice and Training Notice

Any reference voice, custom model, or future fine-tune must use recordings supplied or licensed by the operator with documented speaker consent. Nastech must not be used to impersonate a person without authorization.
