# Expressive TTS research notes

## Sources reviewed

1. Nastech Voice Core official site: https://github.com/bantuinversions/nastech-tts
2. Microsoft Research EmoCtrl-TTS: https://www.microsoft.com/en-us/research/project/emoctrl-tts/
3. Resemble AI Chatterbox repository: https://github.com/resemble-ai/Chatterbox
4. StyleTTS 2 paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC11759097/

## Findings

Nastech Voice Core is the current Nastech core: an open-weight, 99M-parameter, CPU-capable ONNX model with 31-language support. The official site advertises emotion presets and hundreds of preset voices, but the local Python quickstart documents language and voice selection rather than a complete public text-tag vocabulary. Nastech must therefore distinguish model-supported controls from locally verified controls.

Microsoft's EmoCtrl-TTS research demonstrates that time-varying emotional states and non-verbal vocalizations, specifically laughter and crying, can be conditioned in a research model. The project is not publicly released for product integration, so it is research evidence rather than an installable Nastech dependency.

Chatterbox is MIT-licensed code and documents native English paralinguistic tags including [cough], [laugh], and [chuckle] for Turbo/Nano. Its multilingual model supports 23 languages, including Kiswahili, but the model is substantially larger than the Nastech compact budget and should be treated as an optional provider, not bundled into the core. Its documented controls include exaggeration and CFG-style parameters, not a universal list of named emotions.

StyleTTS 2 is an open research system whose style encoder and diffusion-based latent style sampling can express varied prosody and emotion through reference style, but it does not establish a universal markup vocabulary. It is not suitable for direct compact-core inclusion without a separate runtime, model, licensing, and acceptance review.

## Implementation implication

The Nastech markup vocabulary can expose a broad semantic catalog, but every item needs a fidelity state: direct, approximated, unavailable, or provider-dependent. Adding a tag parser entry alone must not claim that the local Nastech Voice Core model produces a specific human behavior. Release tests should verify parsing, routing, and audio hygiene; human/native-speaker review is still required for perceptual emotion claims.

## References

[1]: https://github.com/bantuinversions/nastech-tts "Nastech Voice Core official site"
[2]: https://www.microsoft.com/en-us/research/project/emoctrl-tts/ "Microsoft Research EmoCtrl-TTS"
[3]: https://github.com/resemble-ai/Chatterbox "Resemble AI Chatterbox repository"
[4]: https://pmc.ncbi.nlm.nih.gov/articles/PMC11759097/ "StyleTTS 2 paper"

Saved on 2026-08-18.

## Research update: accessible open-source candidates

A follow-up audit should distinguish four layers: semantic markup, acoustic model control, non-verbal-event generation, and a local acceptance test. Open-source systems commonly document only one or two layers. Chatterbox Turbo/Nano provide the clearest documented tag surface for English paralinguistic events, while EmoCtrl-TTS provides research evidence for richer time-varying emotion but is not a public product dependency. Nastech Voice Core provides the compact local multilingual base, but its public page does not define a complete, stable markup grammar for every emotion or sound.

Nastech should therefore add a provider-neutral expressive catalog and compile each requested feature into a truthful behavior record. For the verified compact local route, direct controls remain the documented Nastech Voice Core tags and tested mappings; broader emotions and sounds may be represented as approximations, rejected as unavailable, or delegated to an explicitly installed optional provider.
