# Nastech Compact Notices

Copyright 2026 Nastech contributors.

Nastech Compact source code is distributed under the Apache License, Version 2.0. Nastech is a local integration and agent-control project: it does **not** redistribute, rename, train, or claim ownership of upstream Supertonic model weights.

## Upstream Model and Runtime Attribution

| Item | Source | License / access note | Nastech use |
|---|---|---|---|
| Supertonic 3 model assets | `Supertone/supertonic-3` | OpenRAIL-M; review upstream terms before hosting or distributing assets | Sole local inference model family. |
| Supertonic Python SDK | `supertone-inc/supertonic-py` | MIT | Local ONNX runtime and voice-style loading. |
| Supertonic main repository | `supertone-inc/supertonic` | MIT | Documentation and cross-platform runtime reference. |
| FastAPI / Uvicorn | Python dependencies | Their respective upstream licenses | Local agent HTTP interface. |

Nastech does not bundle upstream Supertonic weights in its PyPI source distribution. Deployments download the model through the upstream SDK or explicitly bake the upstream assets into a private, license-reviewed image.

## Nastech Integration Attribution

NastechML maps structured English speech intent to Supertonic inline expression tags. Nastech preserves the source markup, compiled local text, and per-control fidelity in a manifest. It distinguishes documented controls from model-release-dependent tags and must not advertise release-dependent behavior as deterministic without an acceptance test.

## Voice and Training Notice

Any custom voice-style JSON or future fine-tune must use recordings supplied or licensed by the operator with documented speaker consent. Nastech must not be used to impersonate a person without authorization.
