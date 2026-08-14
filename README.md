# Nastech Compact TTS

**Nastech Compact v0.5.0** is a real, local, English expressive TTS project built around **Supertonic 3**, a 99M-parameter ONNX model. It runs on CPU, makes no cloud synthesis call, requires no GPU, and exposes an auditable local agent API. [1] [2]

> **Size commitment:** the verified full deployment is **647.51 MiB**, including **384.83 MiB** of real Supertonic model assets, the isolated Python runtime, dependencies, and release assets. It remains below the user-set **1 GiB maximum** with **376.49 MiB** of headroom.

| Capability | Nastech Compact v0.5.0 status |
|---|---|
| Real local synthesis | Working through the official Supertonic ONNX runtime |
| CPU-only operation | Optimized ONNX thread policy; no provider account, GPU, or cloud request is required |
| Agent calls | Nastech compile and speech endpoints plus an OpenAI-compatible alias |
| Direct documented expression events | `<laugh>` and `<sigh>` |
| Additional native-tag requests | `<sad>`, `<angry>`, `<surprise>`, `<cough>`, and `<yawn>` are retained as release-dependent controls |
| Operational controls | Warm-up, CPU profiles, bounded synthesis queue, bounded WAV cache, and diagnostics |
| Output | 44.1 kHz WAV |
| Deployment budget | 1 GiB maximum; automated budget check included |

## Architecture

```text
Agent / workflow
      |
      | NastechML or REST JSON
      v
Nastech Compact API
  - validates English expressive markup
  - compiles local Supertonic expression tags
  - applies bounded CPU scheduling
  - creates a request manifest
      |
      v
Supertonic 3 ONNX runtime (local CPU)
  - ORT_ENABLE_ALL graph optimization
  - configurable intra/inter-op thread pools
      |
      v
44.1 kHz WAV bytes
```

The model downloads into the local Supertonic cache on first use. Nastech does not distribute upstream model weights in its source package.

## Installation

```bash
cd nastech-tts
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

The first synthesis automatically downloads the upstream model assets. Inspect the active CPU profile, model cache, cache usage, and runtime metrics before serving traffic:

```bash
nastech-tts status
```

## CPU Optimizer

Nastech passes explicit ONNX Runtime thread controls to Supertonic, whose loader enables `ORT_ENABLE_ALL` graph optimization and sequential execution for its dependent model stages. [2] The default `balanced` policy is deliberately conservative: it limits CPU oversubscription, serializes model work, and keeps capacity available for the API process.

| Profile | Local policy | Recommended use |
|---|---|---|
| `balanced` | Up to 4 intra-op threads, 1 inter-op thread, 1 active synthesis | Default for a small CPU server or interactive agent |
| `latency` | All detected logical CPUs, 1 inter-op thread, 1 active synthesis | Lowest single-request latency on a dedicated machine |
| `throughput` | Conservative per-request threads and 2 active syntheses | Multiple independent client requests on a machine with available CPU capacity |
| `auto` | Lets ONNX Runtime choose thread counts, 1 active synthesis | Comparison or host-specific experimentation |

Use an environment profile before starting the service. On a six-logical-CPU test machine, the verified `balanced` profile produced the included 12.04-second expressive story in **2.16 seconds mean synthesis time** after warm-up, a **0.180 real-time factor**. The `latency` profile measured **2.13 seconds mean synthesis time** on the same story. Results are host- and workload-specific; benchmark your deployment before selecting a production profile.

```bash
export NASTECH_CPU_PROFILE=balanced
export NASTECH_WARMUP_ON_START=1
export NASTECH_API_KEY='choose-a-local-secret'
nastech-tts serve --host 127.0.0.1 --port 8765
```

Every policy can be overridden explicitly without modifying code.

| Environment variable | Default | Purpose |
|---|---:|---|
| `NASTECH_CPU_PROFILE` | `balanced` | Selects `balanced`, `latency`, `throughput`, or `auto` |
| `NASTECH_INTRA_OP_THREADS` | Profile value | ONNX Runtime intra-operation worker count; overrides `NASTECH_CPU_THREADS` |
| `NASTECH_INTER_OP_THREADS` | Profile value | ONNX Runtime inter-operation worker count |
| `NASTECH_MAX_PARALLEL_SYNTHESIS` | Profile value | Maximum active CPU synthesis jobs; further jobs wait in a bounded queue |
| `NASTECH_QUEUE_TIMEOUT_SECONDS` | `120` | Maximum queue wait before returning a service-unavailable error |
| `NASTECH_AUDIO_CACHE_ENTRIES` | `8` | Maximum recent WAV responses retained in memory |
| `NASTECH_AUDIO_CACHE_MIB` | `32` | Maximum in-memory WAV-cache size |
| `NASTECH_WARMUP_ON_START` | `0` | Set to `1`, `true`, or `yes` to preload the model and run a short local synthesis at API startup |

Benchmark the actual target host after model download. Measurement runs bypass the WAV cache so they report real ONNX work rather than cache hits.

```bash
# Single-request latency benchmark.
NASTECH_CPU_PROFILE=balanced \
  nastech-tts benchmark examples/compact_agent_story.xml --runs 3

# Bounded two-request throughput verification.
NASTECH_CPU_PROFILE=throughput \
  nastech-tts benchmark examples/compact_agent_story.xml --runs 4 --concurrency 2
```

## Real Local Synthesis

```bash
nastech-tts synthesize examples/compact_agent_story.xml --output output/story.wav
```

This creates both `output/story.wav` and an auditable `output/story.wav.manifest.json`. The example performs real local CPU inference using the cached Supertonic model.

Use `nastech-tts warmup` to load the model, voice vector, and generate a brief local WAV before handling production traffic.

## Agent API

Start a local API server:

```bash
export NASTECH_API_KEY='choose-a-local-secret'
nastech-tts serve --host 127.0.0.1 --port 8765
```

An agent should compile intent first. This does not synthesize audio and lets the agent inspect every requested tag:

```bash
curl --request POST http://127.0.0.1:8765/v1/agent/compile \
  --header 'content-type: application/json' \
  --header 'authorization: Bearer choose-a-local-secret' \
  --data @- <<'JSON'
{
  "markup": "<speak voice=\"F1\"><emotion name=\"sad\">The lantern went dark.</emotion><sound type=\"sigh\"/><emotion name=\"happy\">Then sunrise filled the room.</emotion><sound type=\"laugh\"/></speak>"
}
JSON
```

The compact compiler returns local Supertonic prompt text such as:

```text
<sad> The lantern went dark. <sigh> Then sunrise filled the room. <laugh>
```

Generate audio by sending the same payload to `POST /v1/agent/speech`. The response is WAV bytes with `X-Nastech-Request-Id`, `X-Nastech-Runtime`, and `X-Nastech-Duration-Seconds` headers.

The authenticated operational endpoints are `GET /v1/runtime/diagnostics`, which returns the chosen CPU policy, cache statistics, and runtime metrics, and `POST /v1/runtime/warmup`, which loads the local model and performs a short real synthesis. Existing agent clients can call the OpenAI-compatible `POST /v1/audio/speech` endpoint:

```bash
curl --request POST http://127.0.0.1:8765/v1/audio/speech \
  --header 'content-type: application/json' \
  --data '{"model":"nastech-compact-en-v1","input":"Hello from Nastech.","voice":"F1"}' \
  --output hello.wav
```

The complete tool descriptor is at [agent_tools/nastech_tts_tool.json](agent_tools/nastech_tts_tool.json), and the generated OpenAPI contract is at [docs/openapi.json](docs/openapi.json).

## NastechML

```xml
<speak voice="F1">
  <emotion name="sad">The rain would not stop.</emotion>
  <sound type="sigh" />
  <pause ms="300" />
  <emotion name="angry">I will not surrender to the storm.</emotion>
  <sound type="cough" />
  <emotion name="happy">At dawn, the lantern shone again.</emotion>
  <sound type="laugh" />
</speak>
```

Nastech always reports whether a requested control is documented direct, release-dependent, or unavailable. Do not market a named emotion as deterministic until the pinned model build has passed a listening acceptance test for that control.

## License and Model Notice

Nastech source is Apache-2.0. Supertonic code is MIT licensed, and Supertonic 3 model weights use the OpenRAIL-M license. Nastech does not relabel the upstream model as its own or bundle the weights. Review [NOTICE.md](NOTICE.md) and the upstream model terms before distribution. [2] [3]

## References

[1] [Supertonic official repository](https://github.com/supertone-inc/supertonic)

[2] [Supertonic Python SDK and local server documentation](https://github.com/supertone-inc/supertonic-py)

[3] [Supertonic 3 model card](https://huggingface.co/Supertone/supertonic-3)
