# Nastech Multilingual Bantu TTS Research Notes

## Initial authoritative findings — 2026-08-15

| Source | Confirmed finding | Nastech implication |
|---|---|---|
| [Meta MMS announcement](https://ai.meta.com/blog/multilingual-model-speech-recognition/) | MMS reports text-to-speech systems for more than 1,100 languages. The announcement also explains that many language systems are trained with relatively few speakers, often a single speaker. | MMS is a plausible optional language-coverage adapter family, but its model-specific quality, voice, language code, licensing, and local-runtime evidence must be verified before Nastech exposes a language. No broad coverage count is an availability claim. |
| [Uganda Open Source AI Lab model catalogue](https://huggingface.co/USOAL) | USOAL documents fine-tuned Orpheus 3B models for English, Luganda, Runyankole, Teso, and Acholi. Its Luganda examples name Christopher, Charles, Sandra, Michelle, and Daniel. The page warns that some non-English output may be lower quality because its audio codec was not pretrained on local African phonetics. | USOAL is the strongest identified candidate for a multi-speaker Luganda provider adapter. It must remain optional because the listed 3B model family cannot fit inside Nastech TTS’s 1 GiB local core. A lawfully installed external local runtime, documented license, real Luganda text fixture, and human Luganda review are required before promotion to verified availability. |

## Current conclusion

The existing Nastech local core remains **English-only**. It must not claim Luganda or other Bantu languages until a provider-specific local test creates valid audio and language-appropriate review evidence. The upcoming Nastech language registry must differentiate `planned`, `adapter-available`, `configured-local`, and `verified-local` states.

## MMS model-card and coverage-table findings

| Source | Confirmed finding | Nastech implication |
|---|---|---|
| [facebook/mms-tts-sna model card](https://huggingface.co/facebook/mms-tts-sna) | The model card identifies `facebook/mms-tts-sna` as a **Shona** TTS checkpoint. It is VITS-based, available through Transformers 4.33+, and licensed **CC-BY-NC-4.0**. | Shona can be represented as an optional MMS adapter candidate, never part of commercial Nastech core distribution. Any commercial Nastech release needs a separately compatible provider/license; a local non-commercial evaluation adapter must say so explicitly. |
| [MMS language coverage overview](https://dl.fbaipublicfiles.com/mms/misc/language_coverage_mms.html) | The official coverage table is the authoritative location for language-specific MMS task entries and ISO 639-3 identifiers. Its very large dynamically presented table did not yield target-language rows in the first browser extraction. | Nastech must parse and record the exact row for each requested language before registering an MMS candidate; it must not infer coverage from geographic or language-family similarity. |

## License boundary discovered

The MMS Shona model card’s **CC-BY-NC-4.0** license means it cannot be treated as a commercial provider option. The registry must carry a `non-commercial-evaluation-only` state for that provider family until a model-specific compatible licence and product-use decision are documented.

## Southern African and dedicated Luganda candidate review

| Source | Confirmed finding | Nastech decision |
|---|---|---|
| [South-African-TTS-11-Vits model card](https://huggingface.co/guymandude/South-African-TTS-11-Vits) | The repository advertises 11 languages and a CC-BY-NC-4.0 licence, but it requires contact-information sharing before access. Its card is largely an unfilled template, reports invalid configuration parsing, and lacks concrete language/runtime/evaluation documentation. | Do **not** add it as an active or adapter-available Nastech provider. It can only appear in a rejected/review-required research record because the model is gated, non-commercial, and not sufficiently documented. |
| [Sunbird Luganda VITS model card](https://huggingface.co/Sunbird/tts-vits-lug) | The model card states that it is trained on high-quality Luganda data and gives an inference path based on Sunbird’s `vits` inference package, `Sunbird/VITS_Luganda_Studio`, custom cleaners, and 22 kHz audio. It does not show a licence field or complete model-card metadata. | This is the primary **Luganda adapter candidate**, but it is not a verified release provider until its model and runtime licence are confirmed, its exact runtime is installed in an isolated optional environment, a native-speaker-reviewed Luganda fixture is synthesized locally, and Nastech normalizes the result to the public WAV contract. |

The direct Luganda VITS candidate is narrower and potentially lighter than the USOAL 3B models, but its missing licence metadata is a release blocker rather than a detail to assume.

## Preferred Luganda candidate identified

| Source | Confirmed finding | Nastech decision |
|---|---|---|
| [multilingual-tts/VITS-OpenBible-Luganda model card](https://huggingface.co/multilingual-tts/VITS-OpenBible-Luganda) | This is a multi-speaker **Luganda** VITS model trained from scratch on the Open Bible Luganda corpus. It uses Coqui TTS, requires a supplied training-set speaker name, emits 22,050 Hz audio, has approximately 21,553 training utterances, and carries a **CC-BY-SA-4.0** model-card licence. |
| [Model API metadata](https://huggingface.co/api/models/multilingual-tts/VITS-OpenBible-Luganda) | The public, ungated repository is tagged `coqui-tts` and `text-to-speech`, lists model/config/speaker artifacts, and reports `usedStorage` of 997,713,840 bytes. | This is the preferred first local Luganda integration candidate. It is **not** part of Nastech TTS’s 1 GiB core because the model pack alone is approximately 952 MiB before its isolated runtime. It must be an opt-in provider pack. The CC-BY-SA-4.0 licence requires attribution and share-alike compliance review before a product distribution. |

### Integration boundary

Nastech can implement a **Coqui-compatible optional local adapter** for this exact model and normalize its 22.05 kHz output into Nastech’s standard mono 16-bit 44.1 kHz WAV response. Availability remains `adapter-available` until an isolated runtime is installed and an actual Luganda fixture is rendered locally. A native Luganda review is still required before any `verified-language-quality` claim.
