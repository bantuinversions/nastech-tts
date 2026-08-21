# Nastech Research Pages and Long-Conversation Operations

This guide explains how users, contributors, and maintainers use the Nastech Research documentation site, local speech tools, ordered voice previews, optional Bantu packs, AI-agent response commands, and long-conversation reliability evidence.

## Public documentation site

The public Pages address is <https://bantuinversions.github.io/nastech-tts/>. It is built from the repository `site/` directory through the **Publish Nastech Research Pages** workflow.

| Page area | What it provides |
|---|---|
| Start | Clone, desktop installer, and local browser-studio instructions. |
| Verified English voice previews | All 40 ordered English profiles with local WAV preview players. |
| Complete expressive test | A 55.93-second WAV requesting all ten local emotion controls and all eleven sound cues, accompanied by validation JSON. |
| Language coverage | The 61-target code-first catalog, including labels such as `lg - Luganda`, auditable lazy-pack availability, and planned-language boundaries. |
| AI agents | Capability discovery, expression planning, local response generation, and the local Nastech Agent bridge. |
| Reliability | The documented two-hour deterministic conversation contract and the meaning of its reported evidence. |
| Full instructions | Desktop, Python, browser, CLI, language-pack, agent, troubleshooting, and long-form operating guidance. |

The Pages workflow rebuilds `site/assets/languages.json` from the verified registry and regenerates all 40 local English preview WAVs before it publishes the static artifact. This prevents the public catalogue from depending on a stale manually copied preview set.

## Local user instructions

Use the desktop installer for the simplest setup.

```bash
git clone https://github.com/bantuinversions/nastech-tts.git
cd nastech-tts
./installer/install.sh -- platforms
```

Start the local studio and open the exact local URL.

```bash
nastech-tts serve
```

Open `http://127.0.0.1:8765/`, choose a voice and expression, then select **Generate & play**. The API and the browser console remain local; no cloud speech proxy is required for the core English runtime.

For source development, use a virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
make verify
```

## Ordered voice previews

The Pages preview order begins with the ten named local base profiles: Siya, Nasi, Jafta, Della, Axam, Alicia, Shanice, Adam, Shakira, and Shimah. It then lists the clear, soft, and dynamic delivery variants for F1 through M5.

```bash
python scripts/generate_pages_voice_previews.py --force
```

The generator writes `site/assets/voice-previews.json` and 40 WAVs under `site/assets/voice-previews/`. Every preview is checked for the expected WAV format and zero clipped samples. The profiles are delivery and base-timbre selections; they must not be described as separately trained speaker identities unless an independently verified model proves that claim.

## Bantu language use

Start with the catalog, then select and download one exact local pack only when the route is marked `adapter-available`.

```bash
nastech-tts languages
nastech-tts language-packs
nastech-tts language-preflight lg
nastech-tts download-language-pack lg
```

A code-first label makes the selected target clear: `lg - Luganda`, `sw - Kiswahili`, and `bem - Bemba` are examples. A language shown as `planned` remains visible for coverage planning but is not silently replaced with a different language.

## AI-agent response use

An agent should inspect the current local contract before generating speech.

```bash
nastech-tts agent-capabilities
nastech-tts agent-markup "That is remarkable." --emotion awe --sound laughter
nastech-tts agent-speak "I am ready to help." \
  --voice siya --emotion joyful --sound laughter --output response.wav
```

The result JSON names the requested and rendered emotion, all sound mappings, output path, local provider, language, duration, manifest, and suggested next action. The local bridge registers `nastech_tts_speak`, `nastech_tts_status`, and `nastech_tts_capabilities` under `.nastech/config.yaml` when the installer runs.

## Two-hour conversation endurance workflow

The scheduled **Two-hour local conversation endurance** workflow runs weekly at **01:23 UTC on Sunday**. It performs a deterministic two-hour English dialogue using bounded local inference segments with cache disabled for each segment.

| Measured item | Required evidence |
|---|---|
| Conversation duration | Exactly the requested assembled duration, normally 7,200 seconds. |
| Speed | Observed elapsed minutes and overall real-time factor. |
| Reliability | Segment count, per-segment timing, and peak observed process-memory signal. |
| Expressive coverage | All scripted voices, ten emotion controls, and eleven sound cues must render at least once. |
| Audio quality | Mono 16-bit PCM, 44.1 kHz, safe duration, no clipping, and quality levels. |
| Reproducibility | JSON analysis report, segment records, runner contract, and a short listening excerpt. |

The full two-hour WAV is deliberately deleted after validation to avoid storing a large binary in the repository or artifact. The workflow uploads only the JSON report and a listening excerpt. The report records how many minutes that specific runner required; it does not promise the same time, memory, or quality outcome for every computer, language pack, or future model revision.

A maintainer can run a shorter manual check locally before dispatching the full scheduled contract.

```bash
python scripts/run_long_conversation_endurance.py \
  --duration-seconds 70 \
  --segment-seconds 60 \
  --require-full-coverage \
  --output-dir /tmp/nastech-endurance-check
python scripts/summarize_long_conversation_endurance.py \
  /tmp/nastech-endurance-check/two-hour-local-conversation-report.json
```

## Maintainer release checklist

Run the complete verification suite before publishing source, pages, or installer updates.

```bash
make verify
python scripts/validate_project_contracts.py
```

The project contract validates the Pages homepage, complete instruction page, 40 preview WAV assets, 61-language catalog, Pages deployment workflow, weekly endurance schedule, daily CI, and daily language self-test schedule. Review every generated report for the documented environment boundary before presenting a benchmark or endurance outcome as evidence.
