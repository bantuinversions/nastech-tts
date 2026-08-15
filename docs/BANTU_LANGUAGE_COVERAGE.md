# Nastech Bantu-Language Coverage Registry

## Purpose and Claim Boundary

Nastech TTS is a **single product API** with optional language packs. A language is not described as supported merely because a research model, a hosted service, or a provider catalog mentions it. A language progresses through explicit evidence states:

| State | Meaning | May synthesize through the default Nastech core? | May be advertised as available? |
|---|---|---:|---:|
| `verified-local` | An installed provider produced an accepted local fixture; its exact model, licence, quality gate, and human language review are recorded. | Yes, when explicitly selected | Yes, with provider and review scope |
| `configured-local` | An installed local provider can render a valid digital WAV but has not completed human language review. | Yes, when explicitly selected | Only as technical preview |
| `adapter-available` | A concrete provider and configuration route exists, but the optional runtime/model is not installed or validated. | No | No; shown as an installable candidate |
| `research-candidate` | A relevant source exists, but licence, runtime, model-card, or quality evidence is incomplete. | No | No |
| `planned` | Nastech has a defined language target but no acceptable provider route has been accepted. | No | No |
| `rejected` | A discovered model is gated, licence-incompatible, or too poorly documented for Nastech use. | No | No |

> **Pure-language rule:** A `verified-local` Luganda, isiZulu, isiXhosa, Sesotho, Setswana, Shona, Tshivenda, or other Bantu-language claim requires a text fixture written and approved by a competent language reviewer, a local output WAV, deterministic digital-audio acceptance, intelligibility review, and a documented pronunciation issue log. English orthography or an approximate transliteration cannot be used to claim pure speech.

## Current Registry

The table establishes the current Nastech product boundary. It is intentionally broader than the active local core but narrower than a claim that every Bantu language is already usable.

| Region | Language | BCP 47 / ISO 639-3 | Candidate route | Current state | Reason and next gate |
|---|---|---|---|---|---|
| Global | English | `en` / `eng` | Nastech native local ONNX | `verified-local` | Existing real local synthesis, expressive markup, audio-level tests, and release fixtures. |
| Uganda / Great Lakes | Luganda | `lg` / `lug` | OpenBible Luganda VITS through an isolated Coqui-compatible adapter; MMS evaluation candidate | `configured-local` only when explicitly installed and configured; otherwise `adapter-available` | The optional local pack generated a valid technical-preview fixture. Preserve CC-BY-SA-4.0 attribution/share-alike obligations and complete reviewer-approved pure-Luganda intelligibility and dialect review before any `verified-local` claim. |
| Uganda / Great Lakes | Runyankole | `nyn` / `nyn` | USOAL Orpheus optional model | `research-candidate` | USOAL documents the language but the 3B model is outside the Compact core budget and needs licence/runtime review. |
| Uganda | Acholi | `ach` / `ach` | USOAL Orpheus optional model | `research-candidate` | Documented by USOAL; requires optional-pack licensing and real local validation. |
| Uganda | Ateso | `teo` / `teo` | USOAL Orpheus optional model | `research-candidate` | Documented by USOAL; requires optional-pack licensing and real local validation. |
| East Africa | Kiswahili | `sw` / `swa` | Provider research required | `planned` | The first MMS repository probe did not establish the exact public checkpoint route; register only after model-level evidence. |
| East Africa | Kinyarwanda | `rw` / `kin` | MMS optional evaluation adapter | `adapter-available` | Public `facebook/mms-tts-kin` repository probe returned an available CC-BY-NC-4.0 checkpoint. Non-commercial evaluation only until a compatible commercial route is reviewed. |
| East Africa | Kirundi | `rn` / `run` | MMS optional evaluation adapter | `adapter-available` | Public `facebook/mms-tts-run` repository probe returned an available CC-BY-NC-4.0 checkpoint. Non-commercial evaluation only. |
| East Africa | Gikuyu | `ki` / `kik` | MMS optional evaluation adapter | `adapter-available` | Public `facebook/mms-tts-kik` repository probe returned an available CC-BY-NC-4.0 checkpoint. Non-commercial evaluation only. |
| East Africa | Kamba | `kam` / `kam` | Provider research required | `planned` | No public MMS repository was established in the initial exact-code probe. |
| East Africa | Luhya | `luy` / `luy` | Provider research required | `planned` | No public MMS repository was established in the initial exact-code probe. |
| East Africa | Dholuo | `luo` / `luo` | Provider research required | `planned` | No public MMS repository was established in the initial exact-code probe. |
| Southern Africa | isiZulu | `zu` / `zul` | Provider research required | `planned` | The reviewed South-African-TTS-11 model is gated, non-commercial, and incompletely documented; it is rejected as a release route. |
| Southern Africa | isiXhosa | `xh` / `xho` | Provider research required | `planned` | The reviewed South-African-TTS-11 model is gated, non-commercial, and incompletely documented; it is rejected as a release route. |
| Southern Africa | Sesotho | `st` / `sot` | Provider research required | `planned` | No accepted local model route has been established. |
| Southern Africa | Sepedi / Northern Sotho | `nso` / `nso` | Provider research required | `planned` | No accepted local model route has been established. |
| Southern Africa | Setswana | `tn` / `tsn` | Provider research required | `planned` | No accepted local model route has been established. |
| Southern Africa | Tshivenda | `ve` / `ven` | Provider research required | `planned` | No accepted local model route has been established. |
| Southern Africa | Xitsonga | `ts` / `tso` | MMS optional evaluation adapter | `adapter-available` | Public `facebook/mms-tts-tso` repository probe returned an available CC-BY-NC-4.0 checkpoint. Non-commercial evaluation only. |
| Southern Africa | siSwati | `ss` / `ssw` | Provider research required | `planned` | No public MMS repository was established in the initial exact-code probe. |
| Southern Africa | isiNdebele | `nr` / `nbl` | Provider research required | `planned` | No public MMS repository was established in the initial exact-code probe. |
| Southern Africa | Shona | `sn` / `sna` | MMS optional evaluation adapter | `adapter-available` | Public `facebook/mms-tts-sna` repository is documented as a Shona VITS model under CC-BY-NC-4.0. Non-commercial evaluation only. |
| Southern Africa | Chichewa / Nyanja | `ny` / `nya` | MMS optional evaluation adapter | `adapter-available` | Public `facebook/mms-tts-nya` repository probe returned an available CC-BY-NC-4.0 checkpoint. Non-commercial evaluation only. |

## Luganda First-Provider Plan

Nastech prioritizes Luganda because a documented multi-speaker route is available. The chosen initial candidate is `multilingual-tts/VITS-OpenBible-Luganda`, not because it is automatically the best Luganda voice, but because its card documents the language, architecture, local Coqui inference path, training-set speaker selection, 22.05 kHz output, and licence.[1]

The candidate is an **optional external local pack**. Its published storage is approximately 952 MiB before a Coqui-compatible runtime, so including it in the already measured Nastech Compact core would exceed the 1 GiB deployment target. The Nastech API therefore exposes Luganda as `configured-local` only while an isolated, explicitly configured provider environment is active; otherwise it reports the catalog route as `adapter-available`.[2]

## Expressive Long-Form Test Policy

The existing 30-minute continuity release used neutral F1 speech to establish duration and PCM stability. A separate expressive long-form fixture must include an approved, bounded schedule of `<emotion>` and `<sound>` markup; every segment must preserve its compiler decision record. Its release gate has three layers:

| Layer | Required evidence |
|---|---|
| Compiler fidelity | The manifest proves each requested expressive span was compiled directly or records the exact supported fallback. |
| Audio integrity | Every generated segment passes the WAV format, duration, peak, RMS, clipping, DC-offset, and checksum checks. |
| Human listening | A reviewer listens at least to all transitions into and out of emotional/sound spans and documents severe artifacts, intelligibility regressions, or inappropriate portrayal. |

No expressive test may be used to imitate a named individual, a protected group, or a regional accent that has not been separately approved.

## References

[1] [OpenBible Luganda VITS model card](https://huggingface.co/multilingual-tts/VITS-OpenBible-Luganda)

[2] [OpenBible Luganda VITS model API metadata](https://huggingface.co/api/models/multilingual-tts/VITS-OpenBible-Luganda)

[3] [MMS Shona model card](https://huggingface.co/facebook/mms-tts-sna)

[4] [MMS language coverage overview](https://dl.fbaipublicfiles.com/mms/misc/language_coverage_mms.html)

[5] [Uganda Open Source AI Lab TTS catalogue](https://huggingface.co/USOAL)

[6] [South-African-TTS-11-Vits model card](https://huggingface.co/guymandude/South-African-TTS-11-Vits)
