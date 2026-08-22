# Nastech TTS

[![CI](https://github.com/bantuinversions/nastech-tts/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/bantuinversions/nastech-tts/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache--2.0-4D8CC9)](LICENSE)
[![Provider mixer](https://img.shields.io/badge/providers-60%20catalog-0B7A75)](docs/PROVIDER_CATALOG_50.md)

**Nastech TTS** is Nastech Research's local-first expressive text-to-speech platform. It provides a compact English local runtime, 40 selectable English voice profiles, auditable emotional and sound-cue controls, a browser Voice Studio, an AI-agent CLI and MCP bridge, optional native vocal events, and a 61-target Bantu-language registry.

> **Local-first contract:** English synthesis runs on the device. Optional language and vocal-event model packs are explicit on-demand downloads; no cloud speech proxy is used by the normal local workflow. The verified compact Nastech Voice Core environment remains below the **1 GiB** deployment cap. Run `make budget` on the target host for its current measurement.

| You want to… | Start here |
|---|---|
| Hear a voice quickly | [First local WAV](#first-local-wav) |
| Use laughter, sadness, anger, and all expressive controls | [Emotions, sounds, and NastechML](#emotions-sounds-and-nastechml) |
| Make an AI agent speak | [AI-agent CLI and MCP](#ai-agent-cli-and-mcp) |
| Use Luganda or another Bantu target | [Bantu languages and lazy packs](#bantu-languages-and-lazy-packs) |
| Keep CPU free and speed up repeats with RAM | [CPU and RAM performance profiles](#cpu-and-ram-performance-profiles) |
| Use the browser interface | [Voice Studio and documentation site](#voice-studio-and-documentation-site) |
| Run tests, benchmarks, or long-conversation checks | [Quality, benchmarks, and reliability](#quality-benchmarks-and-reliability) |

## Contents

- [What is included](#what-is-included)
- [Installation](#installation)
- [First local WAV](#first-local-wav)
- [English voices](#english-voices)
- [Emotions, sounds, and NastechML](#emotions-sounds-and-nastechml)
- [Core CLI](#core-cli)
- [AI-agent CLI and MCP](#ai-agent-cli-and-mcp)
- [Local HTTP API](#local-http-api)
- [Bantu languages and lazy packs](#bantu-languages-and-lazy-packs)
- [Optional Nastech Vocal Events Pack](#optional-nastech-vocal-events-pack)
- [CPU and RAM performance profiles](#cpu-and-ram-performance-profiles)
- [Voice Studio and documentation site](#voice-studio-and-documentation-site)
- [Quality, benchmarks, and reliability](#quality-benchmarks-and-reliability)
- [Troubleshooting](#troubleshooting)

## What is included

| Capability | Included behavior | Important boundary |
|---|---|---|
| Local English synthesis | Nastech Voice Core renders 44.1 kHz local WAV audio with 10 verified base timbres. | English is the currently verified compact local language. |
| English profile selection | 40 selectable profiles: 10 named Nastech profiles plus 30 delivery profiles. | Delivery profiles change presentation around a verified base timbre; they are not separately trained speaker identities. |
| Expressive markup | 10 core emotions, 11 sound cues, pauses, rate, and volume in NastechML. | A tag is an auditable requested local control, not a promise of a separately trained emotion model. |
| Native vocal events | An optional local pack can generate accepted native events such as laughter from an authorized reference WAV. | It is externalized, English-only, and never loaded by the compact core at startup. |
| Bantu registry | 61 code-first language targets, including 35 audited lazy local routes and 25 planned targets. | A target is not called quality-verified until its stated evidence and native-speaker review gate are met. |
| Browser Voice Studio | Local page with voices, controls, history, exports, themes, batching, and accessibility tools. | It is served locally at `127.0.0.1`; it is not a cloud proxy. |
| AI-agent support | Local CLI commands, documented aliases, and MCP tools returning local WAV output plus decisions. | Agents should inspect capabilities before selecting nuanced labels. |
| Performance controls | Protected CPU-core policies, serial interactive rendering, warm-up, and a bounded in-RAM WAV cache. | A sub-millisecond cache hit is not new model synthesis. |

## Installation

### Requirements

Install **Python 3.10 or later** and Git. Nastech TTS is designed to run locally on CPU first and automatically reports the available ONNX execution providers. GPU providers are never claimed as active merely because they are installed.

### Desktop installer bundle

Download the bundle for Linux, macOS, or Windows from [GitHub Releases](https://github.com/bantuinversions/nastech-tts/releases). Extract it and run the matching command.

| Platform | Hardware diagnostic | Start the local service |
|---|---|---|
| Linux or macOS | `./installer/install.sh --diagnostics` | `./installer/install.sh -- serve --host 127.0.0.1 --port 8765` |
| Windows PowerShell | `.\installer\install.ps1 --diagnostics` | `.\installer\install.ps1 -- serve --host 127.0.0.1 --port 8765` |

The installer creates an isolated environment, checks CPU/GPU/RAM, writes a safe local profile, and can register the Nastech Agent MCP bridge. Use `--repair` to refresh dependencies or `--reset-environment` to recreate the environment. See [installer details](docs/INSTALLER.md).

### Install from source

On Linux or macOS:

```bash
git clone https://github.com/bantuinversions/nastech-tts.git
cd nastech-tts
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

On Windows PowerShell:

```powershell
git clone https://github.com/bantuinversions/nastech-tts.git
cd nastech-tts
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -e '.[dev]'
```

Run a local installation check:

```bash
nastech-tts status
nastech-tts platforms
nastech-tts voices
nastech-tts languages
python scripts/validate_language_self_test.py
```

The language self-check validates the committed **61-target registry**, **35 audited lazy routes**, **11 approved native-story CI routes**, and code-first labels such as `lg - Luganda`.

## First local WAV

Create a small NastechML file and synthesize it locally.

```bash
cat > hello.xml <<'XML'
<speak voice="siya">
  <emotion name="happy" intensity="0.70">Welcome to Nastech TTS.</emotion>
</speak>
XML

nastech-tts validate hello.xml
nastech-tts synthesize hello.xml --output hello.wav --clean
```

The command writes `hello.wav`, a compiled manifest beside it, and—when `--clean` is supplied—a conservative local PCM cleanup report. Open the WAV in any media player.

To start the local HTTP service and Voice Studio:

```bash
nastech-tts serve --host 127.0.0.1 --port 8765
```

Then open <http://127.0.0.1:8765/>.

## English voices

Run `nastech-tts voices` for the complete machine-readable inventory. Ten named profiles map to the verified Nastech Voice Core base timbres.

| Named profile | Base timbre | Named profile | Base timbre |
|---|---:|---|---:|
| `siya` | F1 | `nasi` | F2 |
| `jafta` | M1 | `della` | F3 |
| `axam` | M2 | `alicia` | F4 |
| `shanice` | F5 | `adam` | M3 |
| `shakira` | M4 | `shimah` | M5 |

Each base timbre also has three delivery profiles. These make the total profile count **40**.

| Base timbre | Clear | Soft | Dynamic |
|---|---|---|---|
| F1 | `en-f1-clear` | `en-f1-soft` | `en-f1-dynamic` |
| F2 | `en-f2-clear` | `en-f2-soft` | `en-f2-dynamic` |
| F3 | `en-f3-clear` | `en-f3-soft` | `en-f3-dynamic` |
| F4 | `en-f4-clear` | `en-f4-soft` | `en-f4-dynamic` |
| F5 | `en-f5-clear` | `en-f5-soft` | `en-f5-dynamic` |
| M1 | `en-m1-clear` | `en-m1-soft` | `en-m1-dynamic` |
| M2 | `en-m2-clear` | `en-m2-soft` | `en-m2-dynamic` |
| M3 | `en-m3-clear` | `en-m3-soft` | `en-m3-dynamic` |
| M4 | `en-m4-clear` | `en-m4-soft` | `en-m4-dynamic` |
| M5 | `en-m5-clear` | `en-m5-soft` | `en-m5-dynamic` |

Use a voice in NastechML with `voice="siya"`, `voice="F1"`, or any profile ID from the table.

```xml
<speak voice="della">This uses the Della named profile.</speak>
<speak voice="en-m4-soft">This uses the M4 soft delivery profile.</speak>
```

## Emotions, sounds, and NastechML

NastechML is the portable local markup format. It accepts `<speak>`, `<emotion>`, `<sound>`, `<pause>`, and `<prosody>`.

### Core emotions

Use the following exact emotion names in `<emotion name="…">`.

| Emotion | Typical default delivery | Example |
|---|---|---|
| `neutral` | Normal rate and volume | `<emotion name="neutral">Hello.</emotion>` |
| `happy` | Positive, normal delivery | `<emotion name="happy">We did it.</emotion>` |
| `sad` | Soft, slower delivery | `<emotion name="sad">I will miss you.</emotion>` |
| `angry` | Louder, firm delivery | `<emotion name="angry">Please stop now.</emotion>` |
| `calm` | Soft, slower delivery | `<emotion name="calm">Take a breath.</emotion>` |
| `excited` | Faster, energetic delivery | `<emotion name="excited">This is wonderful.</emotion>` |
| `fearful` | Fast, soft delivery | `<emotion name="fearful">Did you hear that?</emotion>` |
| `frustrated` | Fast, normal delivery | `<emotion name="frustrated">This is not working.</emotion>` |
| `disgusted` | Normal, emphatic delivery | `<emotion name="disgusted">That is unpleasant.</emotion>` |
| `surprised` | Fast, responsive delivery | `<emotion name="surprised">I did not expect that.</emotion>` |

Add `intensity` from `0` to `1` when needed:

```xml
<speak voice="jafta">
  <emotion name="angry" intensity="0.82">I need an answer now.</emotion>
</speak>
```

### Sound cues

Use empty `<sound>` elements for all eleven local sound cues.

| Sound cue | Markup | Useful aliases for agents |
|---|---|---|
| Laugh | `<sound type="laugh" />` | `laughter`, `laughing` |
| Chuckle | `<sound type="chuckle" />` | `giggle`, `giggling` |
| Sigh | `<sound type="sigh" />` | `exhale`, `exhaling` |
| Cough | `<sound type="cough" />` | — |
| Sniffle | `<sound type="sniffle" />` | — |
| Groan | `<sound type="groan" />` | — |
| Yawn | `<sound type="yawn" />` | — |
| Gasp | `<sound type="gasp" />` | `inhale`, `inhale_sharp` |
| Cry | `<sound type="cry" />` | `sob`, `sobbing` |
| Scream | `<sound type="scream" />` | `shriek`, `shrieking` |
| Throat clear | `<sound type="throatclear" />` | `clear_throat`, `throat-clear` |

### Pauses, rate, and volume

| Control | Values | Example |
|---|---|---|
| Pause | Integer milliseconds | `<pause ms="450" />` |
| Rate | `slow`, `normal`, `fast` | `<prosody rate="slow">Speak slowly.</prosody>` |
| Volume | `soft`, `normal`, `loud` | `<prosody volume="soft">A quiet line.</prosody>` |
| Combined prosody | Rate plus volume | `<prosody rate="fast" volume="loud">A strong line.</prosody>` |

### Complete expressive example

```xml
<speak voice="shakira">
  <emotion name="happy" intensity="0.74">We finished the project.</emotion>
  <sound type="laugh" />
  <pause ms="350" />
  <prosody rate="slow" volume="soft">
    <emotion name="calm" intensity="0.55">Now let us review the result carefully.</emotion>
  </prosody>
  <sound type="sigh" />
</speak>
```

Validate before generating:

```bash
nastech-tts validate expressive.xml
nastech-tts compile expressive.xml
nastech-tts synthesize expressive.xml --output expressive.wav --manifest expressive.manifest.json --clean
```

> **Expressive boundary:** NastechML records what you requested and the applied local mapping. Core expression controls are not represented as separate trained voice models. Inspect the generated manifest when you need an auditable record.

## Core CLI

| Command | Purpose |
|---|---|
| `nastech-tts status` | Show runtime, CPU policy, local model cache, RAM WAV cache, and metrics. |
| `nastech-tts warmup` | Load local sessions and run a short local warm-up synthesis. |
| `nastech-tts clear-cache` | Clear the in-memory WAV response cache without unloading model sessions. |
| `nastech-tts voices` | List all 40 English profiles and their verified base timbres. |
| `nastech-tts languages` | List all 61 language targets and their evidence state. |
| `nastech-tts validate FILE.xml` | Check NastechML without model loading or synthesis. |
| `nastech-tts compile FILE.xml` | Create a provider-ready local expression plan and manifest. |
| `nastech-tts synthesize FILE.xml --output FILE.wav` | Generate a local WAV through the active provider. |
| `nastech-tts clean INPUT.wav --output CLEAN.wav` | Apply deterministic local PCM hygiene to a mono 16-bit WAV. |
| `nastech-tts benchmark FILE.xml --runs 5` | Measure fresh cache-disabled local inference and exact RAM-cache hits separately. |
| `nastech-tts providers` | List the Nastech provider catalog and activation states. |
| `nastech-tts platforms` | Report installed ONNX providers and platform evidence. |
| `nastech-tts serve` | Start the local FastAPI gateway and Voice Studio. |

### Mixed voices in one document

Use `nastech-tts synthesize` for normal one-voice documents. The API can render mixed NastechML spans through its mixed voice mode; each span remains a local synthesis segment and is concatenated into PCM audio. Use this capability for dialogue only when the small overhead of per-span rendering is acceptable.

## AI-agent CLI and MCP

### Discover the contract first

An AI agent should inspect the exact local contract before selecting aliases or generating speech.

```bash
nastech-tts agent-capabilities
nastech-tts agent-tools
```

`agent-capabilities` returns the 10 core emotions, 11 core sound cues, aliases, selectable voice profile counts, and language registry state. Examples of documented alias resolution include `joyful → happy`, `awe → surprised`, `triumphant → excited`, `relieved → calm`, `anxious → fearful`, `laughter → laugh`, and `sob → cry`.

### Plan a response without generating audio

```bash
nastech-tts agent-markup "That discovery is remarkable." \
  --voice shakira \
  --emotion awe \
  --sound laughter \
  --rate fast \
  --output agent-plan.json
```

This resolves the requested aliases and writes the exact NastechML, the applied core controls, warnings, and the intended local delivery route.

### Generate an agent voice response

```bash
nastech-tts agent-speak "We are ready to begin." \
  --voice siya \
  --emotion joyful \
  --sound laugh \
  --sound sigh \
  --intensity 0.72 \
  --rate normal \
  --volume normal \
  --output agent-response.wav \
  --manifest agent-response.manifest.json \
  --report agent-response.report.json \
  --clean
```

The command creates a local WAV and structured report. Use one `--sound` option per cue, up to the documented maximum of 11 cues. Accepted rate values are `slow`, `normal`, and `fast`; volume values are `soft`, `normal`, and `loud`.

### Nastech Agent MCP bridge

The installer detects `$NASTECH_HOME` (default `~/.nastech`) and safely registers the local standard-input/output bridge in `~/.nastech/config.yaml`. It preserves existing MCP servers.

```bash
# Install or repair Nastech TTS and register the local bridge.
./installer/install.sh -- platforms

# The bridge can also be run directly when an MCP host launches it.
nastech-tts mcp-server
```

The local bridge exposes these tools:

| MCP tool | Use |
|---|---|
| `nastech_tts_capabilities` | Get the local voice, emotion, sound, alias, and language contract. |
| `nastech_tts_status` | Inspect local runtime, model cache, CPU policy, and RAM response cache. |
| `nastech_tts_speak` | Render a local WAV from text plus a voice, emotion, sounds, and local delivery controls. |

No speech text is forwarded to a cloud proxy by the local bridge. See [AI-agent voice responses](docs/AI_AGENT_VOICE_RESPONSES.md) for the full agent schema and examples.

## Local HTTP API

Set a local bearer token before serving non-health endpoints:

```bash
export NASTECH_API_KEY='choose-a-local-secret'
export NASTECH_WARMUP_ON_START=1
nastech-tts serve --host 127.0.0.1 --port 8765
```

### Main endpoints

| Endpoint | Purpose |
|---|---|
| `GET /v1/health` | Health check. |
| `GET /v1/voices` | 40 English voice profiles. |
| `GET /v1/capabilities` | Local capabilities and expression contract. |
| `GET /v1/languages` | 61-target Bantu-language inventory. |
| `POST /v1/languages/preflight` | Zero-side-effect language provider and evidence plan. |
| `GET /v1/languages/packs` | Lazy language-pack status. |
| `POST /v1/languages/packs/download` | Explicit download of one requested language pack. |
| `GET /v1/providers` | Provider catalog and activation state. |
| `GET /v1/platforms` | Hardware and ONNX execution-provider inventory. |
| `GET /v1/runtime/diagnostics` | Runtime, CPU, model cache, and RAM-cache diagnostics. |
| `POST /v1/runtime/warmup` | Warm local sessions and base voice state. |
| `POST /v1/runtime/cache/clear` | Clear the bounded RAM WAV cache. |
| `POST /v1/agent/plan` | Auditable agent delivery plan. |
| `POST /v1/agent/compile` | Compile NastechML without rendering audio. |
| `POST /v1/agent/speech` | Completed local WAV response. |
| `POST /v1/agent/speech/stream` | Completed WAV delivered in bounded chunks after local synthesis. |
| `POST /v1/audio/clean` | Deterministic local PCM cleanup. |
| `POST /v1/audio/speech` | OpenAI-compatible local plain-text synthesis request. |

Example: create an auditable local agent plan.

```bash
curl --request POST http://127.0.0.1:8765/v1/agent/plan \
  --header 'content-type: application/json' \
  --header "authorization: Bearer $NASTECH_API_KEY" \
  --data @- <<'JSON'
{
  "markup": "<speak voice=\"siya\"><emotion name=\"sad\">The lantern went dark.</emotion><sound type=\"sigh\" /></speak>",
  "objective": "Prepare an auditable local narration.",
  "delivery": "chunked-wav",
  "cleanup": true
}
JSON
```

> **Streaming boundary:** `/v1/agent/speech/stream` generates the completed local WAV first and then sends it in caller-bounded chunks. It reduces client buffering requirements but does not provide incremental ONNX time-to-first-audio.

The complete schema is [docs/openapi.json](docs/openapi.json).

## Bantu languages and lazy packs

Nastech TTS uses code-first language labels such as `lg - Luganda`. Inspect the registry first, then download only the exact supported local pack you need.

```bash
nastech-tts languages
nastech-tts language-packs
nastech-tts download-language-pack lg    # lg - Luganda
nastech-tts download-language-pack sw    # sw - Kiswahili
nastech-tts download-language-pack bem   # bem - Bemba
```

| Evidence state | Meaning | What to do |
|---|---|---|
| `verified-local` | A local route has the project’s stated release evidence. | Use it normally, while respecting the documented language scope. |
| `adapter-available` | An explicit lazy local route is mapped. | Download only the selected pack, then obtain native-speaker review before making quality claims. |
| `planned` | The language is intentionally listed but no verified local checkpoint is mapped. | Do not substitute another voice or claim support. |

The registry currently lists 61 targets, including `lg - Luganda`, `sw - Kiswahili`, `rw - Kinyarwanda`, `bem - Bemba`, `ts - Xitsonga`, `sn - Shona`, and `ny - Chichewa / Nyanja`. It also lists targets such as `zu - isiZulu`, `xh - isiXhosa`, `tn - Setswana`, and `ve - Tshivenda` honestly as planned where no verified local checkpoint is mapped.

A lazy-downloadable route is outside the compact core and does not itself establish dialect coverage, native-speaker quality, or commercial deployment rights. Read [Bantu language coverage](docs/BANTU_LANGUAGE_COVERAGE.md) and [Bantu local models](docs/BANTU_LOCAL_MODELS.md) before distribution.

## Optional Nastech Vocal Events Pack

The compact Nastech Voice Core handles all 11 sound cues as documented expression controls. The optional **Nastech Vocal Events Pack** provides an external local route for more natural accepted event sounds. It is not installed, downloaded, or loaded during normal startup.

```bash
python -m pip install -e '.[vocal-events]'
nastech-tts vocal-events
```

Render a native local laughter event from an **authorized** reference WAV that is at least 10 seconds long:

```bash
nastech-tts vocal-event laugh \
  --reference-audio authorized-reference.wav \
  --confirm-reference-authorized \
  --output laugh.wav \
  --manifest laugh.manifest.json \
  --report laugh.report.json \
  --clean
```

| Sound route | Status |
|---|---|
| `laugh`, `chuckle`, `cough`, `sigh`, `gasp`, `sniffle`, `groan`, `throatclear` | Eligible for the optional native-event route after a successful local accepted render. |
| `cry`, `scream`, `yawn` | Explicit Nastech Voice Core expression fallback unless a separately approved native local route is installed and accepted. |

The pack uses local storage outside the compact core. Set `NASTECH_VOCAL_EVENTS_CACHE=/path/to/cache` to choose its local model-cache location. Use only voices and reference audio you are authorized to use. See the [non-verbal vocalization research record](docs/research_nonverbal_vocalization_options.md).

## CPU and RAM performance profiles

Nastech TTS protects host responsiveness by default. On a multi-core machine it reserves one logical CPU for the operating system, serializes interactive model rendering, and stores exact repeated WAVs in a bounded RAM LRU cache.

### Recommended interactive configuration

```bash
export NASTECH_CPU_PROFILE=latency
export NASTECH_RESERVED_CORES=1
nastech-tts serve
```

| Profile | Inference-thread policy | RAM WAV cache | Best use |
|---|---|---:|---|
| `balanced` | Up to 4 protected cores, serial rendering | 32 entries / 128 MiB | Default local use. |
| `latency` | Up to 4 protected cores, serial rendering | 64 entries / 256 MiB | Interactive assistant and Voice Studio use. |
| `memory` | Up to 2 protected cores, serial rendering | 96 entries / 384 MiB | Repeated short replies where RAM caching is more important than cold throughput. |
| `throughput` | Up to 3 protected cores, up to 2 queued renders | 16 entries / 64 MiB | Explicit multi-request workloads. |
| `auto` | Runtime chooses ONNX threads, serial rendering | 32 entries / 128 MiB | Advanced deployment experimentation. |

Use `NASTECH_ALLOW_ALL_CORES=1` only on a dedicated host when you deliberately want to remove the default reserve. `NASTECH_INTRA_OP_THREADS`, `NASTECH_INTER_OP_THREADS`, `NASTECH_MAX_PARALLEL_SYNTHESIS`, `NASTECH_AUDIO_CACHE_ENTRIES`, and `NASTECH_AUDIO_CACHE_MIB` provide explicit overrides.

Benchmark both fresh and repeated requests:

```bash
nastech-tts benchmark examples/compact_agent_story.xml --runs 5
```

The report always separates **cache-disabled full local synthesis** from an **exact repeat-request RAM-cache hit**. The latter can be far below one millisecond because it returns previously rendered WAV bytes; it is not new speech generation.

## Voice Studio and documentation site

Start the local service and browse to <http://127.0.0.1:8765/>. The **Nastech Research Voice Studio** includes local voice selection, emotion and sound controls, rate controls, templates, exports, history, batch support, themes, keyboard accessibility, and playback.

The published documentation site at [bantuinversions.github.io/nastech-tts](https://bantuinversions.github.io/nastech-tts/) provides all ordered voice previews, the all-effects demonstration, the language table, installation notes, AI-agent examples, and endurance evidence. See [Voice Studio features](docs/VOICE_STUDIO_FEATURES.md) and [GitHub Pages and endurance operations](docs/GITHUB_PAGES_AND_ENDURANCE.md).

## Quality, benchmarks, and reliability

### Validate your markup and WAVs

```bash
nastech-tts validate expressive.xml
nastech-tts synthesize expressive.xml --output expressive.wav --clean --clean-report expressive.cleanup.json
nastech-tts clean expressive.wav --output expressive.cleaned.wav --report clean.json
```

Cleanup is deterministic local PCM hygiene: DC-offset removal, near-silence gating, clipping protection, and short edge fades. It is not voice conversion, a learned denoiser, or a speaker-identity transformation.

### Run project verification

```bash
make verify
make budget
```

`make verify` runs formatting, linting, deterministic tests, package build, contract validation, and the compact-budget check. The GitHub Actions workflow runs ongoing quality checks, English emotion-rich stories, approved Bantu native-language story coverage, Pages preview validation, and the scheduled two-hour local conversation endurance workflow.

### Long-form and endurance checks

Create the 30-minute local continuity artifact:

```bash
python scripts/generate_longform_continuity_test.py \
  --target-seconds 1800 \
  --output-dir release/longform_continuity \
  --max-chunks 96
```

The weekly endurance workflow renders bounded expressive conversation segments, cleans PCM per segment, measures timing and memory, validates the full emotion/sound/voice coverage gate, and rejects clipping. Read [long-conversation operations](docs/GITHUB_PAGES_AND_ENDURANCE.md).

## Troubleshooting

| Symptom | Check | Resolution |
|---|---|---|
| `Nastech Voice Core is unavailable` | `nastech-tts status` | Activate the project environment, then install the declared local dependencies or run the installer with `--repair`. |
| First request is slow | `nastech-tts warmup` | Model loading and voice-style preparation occur on first use. Run warm-up when the service starts. |
| CPU seems busy | `nastech-tts status` | Use `NASTECH_CPU_PROFILE=latency` or `memory`; reserve one or more logical CPUs with `NASTECH_RESERVED_CORES`. Keep `NASTECH_MAX_PARALLEL_SYNTHESIS=1` for interactive use. |
| Repeat response is not fast | `nastech-tts status` | RAM caching applies only to exact text, voice, speed, and step matches. Increase the bounded cache deliberately or inspect the cache key inputs. |
| A Bantu route does not download | `nastech-tts language-preflight CODE` | Confirm that the code is `adapter-available`, read its licence/evidence notice, then explicitly request its pack. |
| A planned Bantu target is selected | `nastech-tts languages` | Choose an available mapped route or wait for a verified local checkpoint; do not substitute another language silently. |
| A vocal event cannot render natively | `nastech-tts vocal-events` | Install the optional pack, provide an authorized 10+ second WAV reference, and use an accepted event route. Other cues remain honest expression fallbacks. |
| Voice Studio does not open | `nastech-tts serve --host 127.0.0.1 --port 8765` | Keep the service process running, then open `http://127.0.0.1:8765/`. |
| Agent alias is not recognized | `nastech-tts agent-capabilities` | Use a core emotion or sound cue, or select one of the documented aliases returned by the command. |

## Security, ownership, and support boundaries

Nastech TTS is presented as a **Nastech Research** local product. Keep API bearer tokens private and bind the service to `127.0.0.1` unless you have deliberately designed secure network access. Do not use a voice reference without authorization. Read `LICENSE`, `NOTICE.md`, model-pack notices, and the route-specific Bantu evidence records before redistribution.

## Further documentation

| Document | Use it for |
|---|---|
| [Installer guide](docs/INSTALLER.md) | Cross-platform installer behavior and repair options. |
| [AI-agent voice guide](docs/AI_AGENT_VOICE_RESPONSES.md) | Alias taxonomy, structured agent output, and MCP integration. |
| [Voice inventory](docs/VOICE_INVENTORY.md) | Voice-profile details and verified timbre evidence. |
| [Voice Studio feature guide](docs/VOICE_STUDIO_FEATURES.md) | Browser controls and local user workflow. |
| [Bantu language coverage](docs/BANTU_LANGUAGE_COVERAGE.md) | Language states, evidence gates, and native-speaker review boundary. |
| [Provider architecture](docs/PROVIDER_ARCHITECTURE.md) | Provider selection, activation, and local/network policy. |
| [Vocal-event research](docs/research_nonverbal_vocalization_options.md) | Native event research, model boundaries, and approved routes. |
| [Pages and endurance operations](docs/GITHUB_PAGES_AND_ENDURANCE.md) | Preview publication, CI evidence, and two-hour conversation workflow. |

---

Copyright © Nastech Research. Nastech TTS is designed for transparent, local, auditable voice generation.
