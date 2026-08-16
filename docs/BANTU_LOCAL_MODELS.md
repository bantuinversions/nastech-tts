# Nastech optional Bantu local model packs

Nastech TTS keeps the compact English core separate from optional multilingual model packs. The following local checkpoints were downloaded and exercised on the current CPU host through the Hugging Face Transformers VITS interface. They are external assets under `/home/ubuntu/nastech-bantu-models`; they are not included in the compact package, Git history, or the 1 GiB core budget.

| Nastech code | Language | Local checkpoint | State | License boundary |
|---|---|---|---|---|
| `lg` | Luganda | `facebook/mms-tts-lug` | downloaded, local inference exercised | CC-BY-NC-4.0; evaluation/non-commercial use only |
| `nyn` | Runyankole | `facebook/mms-tts-nyn` | downloaded, local inference exercised | CC-BY-NC-4.0; evaluation/non-commercial use only |
| `ach` | Acholi | `facebook/mms-tts-ach` | downloaded, local inference exercised | CC-BY-NC-4.0; evaluation/non-commercial use only |
| `teo` | Ateso | `facebook/mms-tts-teo` | downloaded, local inference exercised | CC-BY-NC-4.0; evaluation/non-commercial use only |
| `sw` | Kiswahili | `facebook/mms-tts-swh` | downloaded, local inference exercised | CC-BY-NC-4.0; evaluation/non-commercial use only |
| `rw` | Kinyarwanda | `facebook/mms-tts-kin` | downloaded, local inference exercised | CC-BY-NC-4.0; evaluation/non-commercial use only |
| `rn` | Kirundi | `facebook/mms-tts-run` | downloaded, local inference exercised | CC-BY-NC-4.0; evaluation/non-commercial use only |
| `ki` | Gikuyu | `facebook/mms-tts-kik` | downloaded, local inference exercised | CC-BY-NC-4.0; evaluation/non-commercial use only |
| `ts` | Xitsonga | `facebook/mms-tts-tso` | downloaded, local inference exercised | CC-BY-NC-4.0; evaluation/non-commercial use only |
| `sn` | Shona | `facebook/mms-tts-sna` | downloaded, local inference exercised | CC-BY-NC-4.0; evaluation/non-commercial use only |
| `ny` | Chichewa / Nyanja | `facebook/mms-tts-nya` | downloaded, local inference exercised | CC-BY-NC-4.0; evaluation/non-commercial use only |

The models are separate single-language VITS checkpoints, not a single universal multilingual voice. Their existence and local generation do not by themselves establish pronunciation quality, native-speaker acceptance, commercial redistribution rights, or production readiness. The Nastech language registry must retain those evidence boundaries.

## Hardware behavior

The optional inference harness detects CUDA through PyTorch and uses CUDA only when CUDA is available and the ONNX provider inventory also registers `CUDAExecutionProvider`. Otherwise it uses CPU float32 inference and loads one model at a time to control RAM. The current host has 6 logical CPUs, approximately 23.8 GiB RAM, no CUDA device, and no registered ONNX Runtime providers; its automatic plan is CPU execution, four intra-operation threads, one inter-operation thread, at most two parallel synthesis requests, and batch size one.

The core runtime exposes the same plan through `HardwarePlan` and the `/v1/platforms`, `/v1/health`, and `/v1/runtime/diagnostics` metadata. Set `NASTECH_DEVICE=auto` for automatic selection, `NASTECH_DEVICE=cpu` to force CPU, or `NASTECH_DEVICE=gpu` to require a verified CUDA plus CUDAExecutionProvider environment. A forced GPU request fails closed rather than silently falling back to CPU.

## Reproducible local test

From the repository root, install the optional download dependency and run:

```bash
sudo pip3 install huggingface_hub
python3 scripts/install_mms_bantu_models.py
PYTHONPATH=/home/ubuntu/nastech-luganda-runtime python3 scripts/test_installed_bantu_mms_voices.py
```

The test writes WAV fixtures and a deterministic `manifest.json` under `release/bantu_mms_fixtures/`. The current CPU run produced non-silent, unclipped 16 kHz mono WAVs for all eleven installed packs. This is an audio-generation smoke result, not a native-language quality certification.

## References

[1]: https://huggingface.co/facebook/mms-tts "Meta MMS-TTS model collection and language coverage"

[2]: https://huggingface.co/docs/transformers/en/model_doc/mms "Transformers MMS documentation and local VITS inference"

[3]: https://huggingface.co/BrianMwangi/African-Kikuyu-TTS "Kikuyu MMS-derived model card and license metadata"
