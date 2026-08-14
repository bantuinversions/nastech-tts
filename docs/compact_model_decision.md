# Nastech Compact Model Decision

## Selected Base: Supertonic 3

Nastech Compact uses **Supertone Supertonic 3** as its single local synthesis model. It is a 99M-parameter ONNX model designed for CPU, edge, browser, and local-server inference. The official Python SDK states that the first run downloads approximately 400 MB of model assets. [1] [2]

## Verified Budget

The current Nastech cloud downloaded and initialized the actual Supertonic 3 assets, installed the complete Nastech API and release dependencies, and ran the mandatory budget script. The final measured deployment subtotal is **647.16 MiB**: **384.83 MiB** of model assets, **260.68 MiB** of Python runtime and dependencies, and **1.65 MiB** of project/release assets. This is below the user’s **1 GiB hard deployment cap**, leaving **376.84 MiB** of headroom before generated audio.

| Budget area | Measured / defined size | Status |
|---|---:|---|
| Supertonic 3 model assets | 384.83 MiB | Included in the 1 GiB deployment budget |
| Python runtime and dependencies | 260.68 MiB | Included in the 1 GiB deployment budget |
| Nastech source and release assets | 1.65 MiB | Included in the 1 GiB deployment budget |
| Verified deployment subtotal | **647.16 MiB** | **Passes** with 376.84 MiB headroom |
| Generated audio | Runtime output, not bundled in release assets | Keep output storage outside the 1 GiB image budget |

## Real Local Features

Supertonic runs fully locally with ONNX Runtime, without a GPU or cloud synthesis call. It exposes native local and OpenAI-compatible HTTP endpoints and documents inline expression tags, including `<laugh>`, `<breath>`, and `<sigh>`. The Supertonic repository also describes ten expression tags. [1] [2]

Nastech Compact will directly pass the documented native tags, provide a local agent API, and measure a real local synthesis result. It will treat named emotions such as sadness or anger as available native tag requests only after a local audio acceptance test; it will not claim universal deterministic emotion fidelity.

## License Boundary

Supertonic code is MIT licensed, while Supertonic 3 weights are released under OpenRAIL-M. Nastech Compact must preserve the model notice and must not relabel or redistribute the upstream weights as Nastech-owned. [2]

## References

[1] [Supertonic official repository](https://github.com/supertone-inc/supertonic)

[2] [Supertonic Python SDK](https://github.com/supertone-inc/supertonic-py)

[3] [Supertonic 3 model card](https://huggingface.co/Supertone/supertonic-3)
