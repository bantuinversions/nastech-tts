# Common Voice Luganda research notes

## Initial findings

The Mozilla Data Collective lists a current **Common Voice Scripted Speech 26.0 — Luganda** dataset and identifies its licence as **Creative Commons Zero v1.0 Universal (CC0-1.0)**. The search result also identifies a Mozilla Data Collective organization entry for Luganda with the same CC0 signal. These official pages require direct review before using the corpus in a release or redistribution workflow.

A Zindi page for the Mozilla Luganda ASR competition states that the competition used a complete Luganda Common Voice dataset and a test set of approximately 7,000 recordings. This is competition evidence, not a current TTS distribution source.

A Mozilla discourse result reports a historical Luganda Common Voice volume above 467 hours, with approximately 117 hours of training data and 21 hours each for test and validation in one release/accounting context. This must not be treated as the current version 26.0 size without checking the authoritative metadata.

Recent Luganda TTS research is directly relevant. A 2024 arXiv paper, *Building a Luganda text-to-speech model from crowdsourced data*, reports work using monolingual Luganda Common Voice version 12.0 data. A 2025 *Data in Brief* paper describes a curated crowdsourced Luganda and Kiswahili speech dataset for TTS and states that Mozilla Common Voice data was used as a source. These papers may provide preprocessing and speaker-selection guidance, but their exact dataset redistribution terms and model code must be audited before adoption.

The current Nastech OpenBible VITS route should remain a baseline. Common Voice is promising because it offers larger crowdsourced coverage and may support speaker filtering, transcript cleaning, and fine-tuning, but **dataset size alone does not establish TTS quality**. The next research step is to inspect the official dataset page, the 2024/2025 TTS papers, and any reproducible training repositories or checkpoints, then determine whether a local CPU-feasible adaptation is realistic under Nastech’s compact core boundary.

## Candidate sources

1. https://mozilladatacollective.com/datasets/cmqinhruw00vinq07tohj4fd3 — Common Voice Scripted Speech 26.0, Luganda.
2. https://mozilladatacollective.com/organization/cmfh0j9o10006ns07jq45h7xk — Mozilla Data Collective Common Voice organization entry.
3. https://commonvoice.mozilla.org/en/datasets — Mozilla Common Voice dataset access page.
4. https://zindi.africa/competitions/mozilla-luganda-automatic-speech-recognition/data — Mozilla Luganda competition data description.
5. https://arxiv.org/abs/2405.10211 — Building a Luganda text-to-speech model from crowdsourced data.
6. https://www.sciencedirect.com/science/article/pii/S2352340925006390 — A curated crowdsourced dataset of Luganda and Swahili speech for text-to-speech synthesis.
7. https://discourse.mozilla.org/t/discrepancy-in-hours-between-common-voice-datasets-page-and-hugging-face-download/131722 — Historical Common Voice Luganda size discussion.

## Verified source details

The official Common Voice catalogue describes the platform as a free, open-source, community-led speech-data platform. Its catalogue labels Common Voice Scripted Speech 26.0 datasets as CC0-1.0, MP3 format, and ASR task data. The dedicated Luganda Data Collective page confirms the current dataset title, although its dynamically loaded page does not expose the full size in static extraction.

The 2024 Luganda TTS paper reports that Common Voice recordings are intelligible but lower quality than studio-grade speech because of preprocessing, varying intonation, and background noise. Its improvement path selected six female speakers with close intonation, trimmed leading and trailing silence, applied pretrained speech enhancement, and filtered clips with a non-intrusive MOS estimator above 3.5. Nine native Luganda listeners gave the improved model a reported MOS of 3.55, compared with 2.5 for an existing model; six-speaker training outperformed one- and two-speaker variants in that study.

The 2025 open-access Data in Brief article gives a more concrete curated resource: it derives from Mozilla Common Voice, retains validated utterances from female speakers, uses manual intonation/pitch/rhythm selection, acoustic clustering with pitch and MFCC features, WebRTC VAD trimming, causal DEMUCS denoising, and WV-MOS filtering at predicted MOS >= 3.5. The final resource reports over 19 hours of Luganda from six female speakers, with paired transcriptions, and links the original data to Mendeley Data. The article is CC BY 4.0; the underlying Common Voice source and any derivative packaging must still be tracked separately.

## Recommended path

The strongest practical route is not to train directly on the entire noisy Common Voice release. Nastech should first evaluate the cited curated six-speaker Luganda resource and its preprocessing recipe, then use a compatible local TTS architecture for a controlled technical experiment. The dataset is approximately 19 hours, which is materially more useful for a small multi-speaker or speaker-selected fine-tune than the current single OpenBible preview, but it still requires model-specific licensing, code compatibility, CPU/RAM measurements, and native-speaker listening review.

The current Nastech core should remain under 1 GiB. The curated dataset, training checkpoints, enhancement models, and training dependencies should be treated as external research assets and not bundled into the compact runtime. Only a distilled or separately installed inference pack may be considered for a future release.

## Additional references

8. https://arxiv.org/html/2405.10211v1 — Full HTML for the 2024 Luganda TTS paper.
9. https://doi.org/10.1016/j.dib.2025.111915 — 2025 curated Luganda/Swahili TTS dataset article.
10. https://data.mendeley.com/datasets/nb8b25h9nj/3 — Original curated dataset linked by the 2025 article.

## Curated dataset record

The linked Mendeley record is **version 3**, published 27 May 2025, DOI `10.17632/nb8b25h9nj.3`. It states that the audio and transcripts come from Mozilla Common Voice Luganda v12.0 and contain six selected female speakers. The Luganda folder contains `wavs.zip` and `metadata.csv`; metadata has `filename` and `transcript` columns. The recordings were silence-trimmed, denoised with causal DEMUCS, and filtered with WV-MOS at predicted MOS >= 3.5. The Mendeley record identifies the dataset licence as **CC BY 4.0**, so Nastech must preserve attribution and the dataset’s terms if it downloads, transforms, trains on, or redistributes derived artifacts.

This curated dataset is a stronger candidate than downloading the full current Common Voice catalogue for the first experiment because its speaker selection and audio-quality preprocessing directly target the failure modes observed in the current OpenBible preview. It is still not automatically a production voice: the model architecture, training code, checkpoint licence, transcript normalization, and native-speaker review remain separate gates.

## Browser verification note

The Mendeley page rendered the dataset title, contributor list, DOI, CC BY 4.0 licence, and descriptive file layout. The browser view did not expose direct `wavs.zip` download URLs in the visible static content, and no download or sign-in action was performed. Direct file acquisition therefore remains pending URL/API inspection and checksum capture.

## Requested five-voice roster

The Nastech Luganda improvement target is five distinct speakers: `F1`, `F2`, and `F3` for three female voices, plus `M1` and `M2` for two male voices. These labels are speaker identities for model/data selection, not pitch-shifted renderings. Each identity must map to a real source speaker with explicit dataset metadata.

The target roster requires balanced speaker contribution, speaker-disjoint validation clips, transcript normalization that preserves Luganda orthography, and separate native-speaker review notes. A voice may not be promoted merely because its waveform is valid; the review must assess intelligibility, pronunciation, rhythm, tonal/prosodic naturalness, noise, and speaker consistency. If the curated Common Voice-derived resource contains six female speakers but no suitable male speakers, Nastech must report that limitation rather than fabricate the two male voices; a second lawful source or a future male-speaker collection would then be required.

## Gender coverage constraint

The curated 2025 TTS dataset cannot by itself satisfy the requested five-voice roster because it intentionally contains six selected female speakers per language. Broader Common Voice Luganda releases do include male contributors according to the Luganda corpus and radio-corpus literature, but the exact current five-speaker selection must be made from official per-speaker metadata rather than inferred from aggregate percentages or labels. The practical roster remains three female speakers plus two male speakers, with the curated female subset useful for quality benchmarking and the broader Common Voice release needed for male-speaker candidates.

The five identities should therefore be selected only after inspecting official Luganda metadata fields such as client/speaker identifier, gender declaration, clip validation status, transcript, and split membership. Common Voice gender fields are self-declared and may include unspecified values; Nastech must preserve that distinction and must not infer gender from audio.

## Five-voice experiment status

The public Common Voice v22 Luganda train metadata was downloaded separately from the compact Nastech runtime. It contains 70,? rows in the mirror’s train split and uses self-declared labels `female_feminine`, `male_masculine`, and unspecified. A deterministic majority-gender filter selected five real client IDs: three female candidates for F1/F2/F3 and two male candidates for M1/M2. Each candidate contributed 200 clips, for 1,000 total clips. The clips were extracted from the corresponding external Luganda tar shards and normalized to mono 22.05 kHz PCM WAV.

The data was presented to Coqui’s Common Voice formatter using a local `metadata.tsv` and `clips/` layout. The formatter resolved 900 train and 100 evaluation samples with exactly five speaker names: `MCV_F1`, `MCV_F2`, `MCV_F3`, `MCV_M1`, and `MCV_M2`; no audio files were missing.

A VITS model configuration was instantiated locally with five speaker embeddings and a local JSON mapping. The existing OpenBible Luganda model was confirmed to have only one speaker and was not relabeled as five voices. A bounded CPU smoke run using ten samples completed four optimization steps and produced a checkpoint plus one inference WAV per speaker. This proves the real data, speaker conditioning, training, checkpoint, and inference path, but it is **not evidence of production-quality Luganda**. Longer fine-tuning, pronunciation/transcript cleanup, objective audio checks, and native-speaker listening review are still required.

The five-speaker artifacts remain external research assets and are not part of the compact Nastech core budget or release package until the quality and licensing evidence gates are passed.

## One-epoch five-voice evidence

A bounded one-epoch CPU run completed 449 optimization steps over 900 training samples and evaluated 100 held-out samples. The model produced five speaker-conditioned outputs from `best_model_450.pth`. All outputs are mono 22.05 kHz PCM WAVs. Durations and deterministic measurements were: F1 7.6401 s, RMS −15.1877 dBFS, one clipped sample; F2 6.4327 s, RMS −14.0965 dBFS, one clipped sample; F3 5.4110 s, RMS −16.1601 dBFS, zero clipped samples; M1 8.4528 s, RMS −17.7759 dBFS, one clipped sample; M2 7.7562 s, RMS −18.0846 dBFS, one clipped sample. Peaks were within approximately 0.0003–0.0005 dB of full scale.

These outputs demonstrate that all five real speaker IDs are accepted by the local model and yield distinct speaker-conditioned files. They do not establish naturalness, pronunciation accuracy, or production readiness. The training log reported out-of-vocabulary punctuation and characters including apostrophe variants, quotation marks, ellipsis, `h`, and `x`; transcript normalization and vocabulary expansion are required before a longer quality run. The current release state must therefore remain a Luganda technical preview.
