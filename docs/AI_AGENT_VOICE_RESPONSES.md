# AI Agent Local Voice Responses

Nastech TTS exposes a **local command-line response contract** for AI agents and automation. An agent can inspect what is actually available, resolve natural language such as `joyful` or `awe` to a verified local rendering control, generate a WAV, and read a machine-readable JSON result. The response workflow keeps speech synthesis on the same device; it does not require a cloud proxy.

## Start with capability discovery

```bash
nastech-tts agent-capabilities
```

The command returns the core rendering controls, alias mapping, all sound cues, available rates and volumes, 40 English voice profiles, and the 61-language registry. An agent should inspect this record before requesting a response, rather than assuming a label is independently trained.

> **Rendering boundary.** The broader vocabulary is an agent-friendly mapping layer. It resolves to the verified ten local NastechML emotion controls and eleven sound cues. An alias is not a claim of a separately trained model head or a promise of identical perception across languages and speakers.

| Core local emotion | Example agent labels that resolve to it | Default rendering profile |
|---|---|---|
| `neutral` | neutral | normal rate, normal volume |
| `calm` | serene, peaceful, gentle, tender, content, relieved | slow rate, soft volume |
| `happy` | joy, joyful, delight, amused, playful | normal rate, normal volume |
| `excited` | hopeful, optimistic, eager, energetic, elated, triumphant, proud | fast rate, loud volume |
| `surprised` | awe, astonished, amazed, curious, interested, realization, confused | fast rate, normal volume |
| `sad` | grief, mournful, disappointed, nostalgic, regretful | slow rate, soft volume |
| `angry` | irritated, annoyed, rage, furious, contempt | normal rate, loud volume |
| `frustrated` | embarrassed, ashamed, guilty, awkward | fast rate, normal volume |
| `fearful` | anxious, nervous, worried, alarmed, horrified | fast rate, soft volume |
| `disgusted` | repulsed, revulsed | normal rate, normal volume |

The mapping is informed by research showing richer, gradient-like categorical structure in vocal expression and prosody rather than a claim that a short fixed list exhausts human emotion. A vocal-burst study reported at least 24 categories, while a cross-cultural speech-prosody study found at least 12 communicable categories and emphasized gradients between them. [1] [2]

## Generate one local AI voice response

```bash
nastech-tts agent-speak \
  "Nastech Research is ready. I am happy to help with a clear local voice response." \
  --voice siya \
  --emotion joyful \
  --sound laughter \
  --sound sigh \
  --output /tmp/agent-response.wav
```

The `agent-speak` command writes the WAV and compiled manifest, then prints JSON with the response type, local paths, duration, language, provider, the requested and rendered emotion, every requested and rendered sound cue, and the suggested next action `play_or_attach_local_wav`.

| Command | Use | Side effect |
|---|---|---|
| `agent-capabilities` | Discover the current local contract before generating | None |
| `agent-markup` | Resolve labels and inspect auditable NastechML | None unless `--output` is supplied |
| `agent-speak` | Generate one real local WAV response | Writes requested WAV and manifest; optionally writes a JSON report |

## Sound cues

The renderer supports **all eleven** local sound cues: `laugh`, `chuckle`, `sigh`, `cough`, `sniffle`, `groan`, `yawn`, `gasp`, `cry`, `scream`, and `throatclear`. Agent-friendly aliases are also accepted: `laughter → laugh`, `giggle → chuckle`, `sob → cry`, `shriek → scream`, `exhale → sigh`, `inhale → gasp`, and `throat-clear → throatclear`.

```bash
nastech-tts agent-markup \
  "That result is remarkable." \
  --emotion triumphant \
  --sound laughter \
  --sound throat-clear
```

This plan resolves `triumphant` to the local `excited` control, `laughter` to `laugh`, and `throat-clear` to `throatclear`; all three decisions appear explicitly in the JSON result.

## Local MCP use

Nastech Agent discovers the local bridge from `.nastech/config.yaml`. The installer now registers three tools: `nastech_tts_speak`, `nastech_tts_status`, and `nastech_tts_capabilities`. An AI should call `nastech_tts_capabilities` before choosing a nuanced emotion label. `nastech_tts_speak` accepts the same core controls and aliases, returns WAV content, and includes the resolved local expression record alongside it.

## References

[1] Cowen, A. S., Elfenbein, H. A., Laukka, P., & Keltner, D. (2019). [Mapping 24 emotions conveyed by brief human vocalization](https://pmc.ncbi.nlm.nih.gov/articles/PMC6586540/). *American Psychologist*, 74(6), 698–712.

[2] Cowen, A. S., et al. (2019). [The primacy of categories in the recognition of 12 emotions in speech prosody across two cultures](https://www.nature.com/articles/s41562-019-0533-6). *Nature Human Behaviour*, 3, 369–382.

[3] Cowen, A. S., & Keltner, D. (2017). [Self-report captures 27 distinct categories of emotion bridged by continuous gradients](https://www.pnas.org/doi/10.1073/pnas.1702247114). *Proceedings of the National Academy of Sciences*, 114(38), E7900–E7909.
