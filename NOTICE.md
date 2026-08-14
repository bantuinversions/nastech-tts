# Nastech TTS Notices

Copyright 2026 Nastech contributors.

Nastech TTS project code is distributed under the Apache License, Version 2.0. The project is built to load, but does not redistribute or claim ownership of, one upstream model family.

## Upstream Model and Runtime Attribution

| Item | Source | License / access note | Nastech use |
|---|---|---|---|
| Orpheus 3B 0.1 Finetuned | `canopylabs/orpheus-3b-0.1-ft` | Apache-2.0 model card; model page requests agreement to its access conditions before original files are accessed | Sole ready-made base model for `nastech-voice-en-v1`. |
| Orpheus TTS source | `canopyai/Orpheus-TTS` | Apache-2.0 | Reference implementation and documented fine-tuning workflow. |
| orpheus-cpp | PyPI package `orpheus-cpp` | Review upstream package terms before redistribution | Optional CPU-compatible local inference runtime. |
| llama-cpp-python | PyPI package `llama-cpp-python` | MIT license; review upstream notice on distribution | Optional CPU inference dependency. |

Nastech does not bundle upstream model weights in this repository. Users download model files through the selected upstream runtime and remain responsible for accepting applicable terms.

## Nastech Adapter Attribution

A future `nastech-voice-en-v1` LoRA/QLoRA adapter will be trained on licensed, consented English recordings. Its model card must list the base model, dataset licenses, speaker-consent policy, evaluation protocol, and known behavior limitations.
