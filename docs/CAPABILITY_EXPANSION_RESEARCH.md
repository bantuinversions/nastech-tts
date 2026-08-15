# Additional 500-Capability Research Basis

## Purpose

This research note supports the second 500-record Nastech roadmap expansion. The catalog is an **engineering and validation program**, not a claim that every record is implemented by Nastech Compact. Each record must remain labelled with an implementation, validation, consent, security, licensing, or research delivery class.

## Evidence Summary

| Source family | Verified capability concepts for the roadmap | Boundary applied to Nastech |
|---|---|---|
| OpenVoice | Voice tone-color cloning, style controls, emotion, accent, rhythm, pauses, intonation, and cross-lingual cloning are documented capability families. [1] | Nastech remains English-only and single-model-family; cloning and conversion records require explicit consent, abuse prevention, model/license review, and separate deployment sizing. |
| SpeechBrain | Speech recognition, enhancement, separation, speaker recognition, speech-to-speech translation, sound-event detection, beamforming, augmentation, feature extraction, and research recipes are documented speech/audio families. [2] | These are integrations or research tracks, not bundled Nastech Compact features; each would require model, runtime, quality, and budget validation. |
| ONNX Runtime Mobile | Android CPU, NNAPI, XNNPACK, iOS CoreML, model fit, memory, binary size, latency, power, operator compatibility, and custom-runtime sizing are documented mobile concerns. [3] | A provider listing never verifies Supertonic execution. Mobile profiles remain planned until target-device synthesis and evidence are committed. |
| W3C WAI text-to-speech guidance | Semantic structure, keyboard compatibility, text alternatives, language metadata, synchronized highlighting, and reader controls matter for accessible speech interfaces. [4] | Accessibility records must be tested with supported clients and proper structured inputs, not merely narrated text. |
| W3C WAI media description guidance | Audio description, timed text, VTT, audio-track mixing, ducking, description timing, and descriptive transcript workflows are concrete media-accessibility capability families. [5] | Any video/audio-description pipeline requires explicit media-input, timing, and player-support validation; it is not supplied by the current TTS runtime. |
| C2PA | Content Credentials are an open standard for recording media origin and edits. [6] | Provenance records are planned security work and do not imply cryptographic signatures are present in current WAV output. |
| NIST speech analytics | Systematic, targeted evaluation, speech activity detection, keyword search, segmentation, transcription, and disfluency evaluation are documented speech-evaluation categories. [7] | Evaluation records require disclosed datasets, metrics, protocol versioning, and reproducible results before quality claims. |

## Research-Driven Catalog Domains

The new 500 records are divided among 20 domains: expressive control; linguistic processing; speaking styles; speaker and identity governance; streaming and interaction; audio cleanup and restoration; accessibility and assistive delivery; multimedia description; agent orchestration; API and client contracts; security and consent; provenance and auditability; evaluation and measurement; data governance; training and adaptation; CPU performance; accelerators; mobile deployment; web and edge deployment; and operations and ecosystem stewardship.

## Decision Rule

> A catalog record becomes `implemented/core` only when the Nastech code, automated test evidence, documentation, package/budget measurement, and applicable target/platform proof are committed. Voice identity, training, and provenance work additionally require explicit consent, policy, or cryptographic validation as appropriate.

## References

[1] [OpenVoice repository and documented capability overview](https://github.com/myshell-ai/OpenVoice)

[2] [SpeechBrain project overview](https://speechbrain.github.io/)

[3] [ONNX Runtime mobile development guide](https://onnxruntime.ai/docs/tutorials/mobile/)

[4] [W3C WAI: Text to Speech](https://www.w3.org/WAI/perspective-videos/speech/)

[5] [W3C WAI: Description of Visual Information](https://www.w3.org/WAI/media/av/description/)

[6] [Coalition for Content Provenance and Authenticity](https://c2pa.org/)

[7] [NIST Speech Analytics](https://www.nist.gov/programs-projects/speech-analytics)
