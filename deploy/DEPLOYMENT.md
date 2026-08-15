# Nastech Compact Deployment

Nastech Compact is a **single local service**. It contains the Nastech agent API and uses Supertonic 3 ONNX assets on the same CPU host. It has no cloud TTS dependency and needs no GPU.

## Size Contract

The target maximum full deployment budget is **1 GiB**. The verified release measurement is **676.42 MiB**, consisting of 384.83 MiB of real Supertonic assets, 289.15 MiB of runtime and quality-tool dependencies, and 2.44 MiB of Nastech release assets. This leaves 347.58 MiB of headroom. Run the budget check after every dependency or model update.

```bash
python scripts/check_compact_budget.py \
  --runtime /path/to/.venv \
  --model-cache ~/.cache/supertonic3 \
  --release . \
  --limit-mib 1024
```

Generated WAV files are runtime data; keep them in a mounted output directory or object storage rather than in a model image.

## Python Deployment

```bash
python -m venv .venv
source .venv/bin/activate
pip install 'nastech-tts[dev]'

export NASTECH_API_KEY='choose-a-secret'
export NASTECH_CPU_PROFILE=balanced
export NASTECH_WARMUP_ON_START=1

nastech-tts status
nastech-tts serve --host 127.0.0.1 --port 8765
```

`balanced` is the safe default. Use `latency` for one active dedicated interactive request, or `throughput` for two bounded concurrent synthesis jobs when the host has capacity. Configure exact ONNX thread counts through `NASTECH_INTRA_OP_THREADS` and `NASTECH_INTER_OP_THREADS` only after benchmarking the target server.

| Environment variable | Default | Deployment purpose |
|---|---:|---|
| `NASTECH_CPU_PROFILE` | `balanced` | Selects the CPU scheduling policy |
| `NASTECH_MAX_PARALLEL_SYNTHESIS` | Profile value | Bounds active CPU synthesis work |
| `NASTECH_QUEUE_TIMEOUT_SECONDS` | `120` | Bounds queueing time during overload |
| `NASTECH_AUDIO_CACHE_MIB` | `32` | Bounds RAM used by recent response caching |
| `NASTECH_WARMUP_ON_START` | `0` | Runs a short local synthesis before accepting traffic when truthy |

If startup warm-up is not enabled, call the authenticated `POST /v1/runtime/warmup` endpoint before routing production traffic. Inspect `GET /v1/runtime/diagnostics` to confirm the selected profile, effective threads, model cache, response cache, queue metrics, and synthesis health.

## Benchmark Before Production

The model and CPU allocator are host dependent. Use a local cache-bypassing benchmark before choosing overrides:

```bash
# Measure single-request latency.
NASTECH_CPU_PROFILE=balanced \
  nastech-tts benchmark examples/compact_agent_story.xml --runs 3

# Verify bounded two-request throughput.
NASTECH_CPU_PROFILE=throughput \
  nastech-tts benchmark examples/compact_agent_story.xml --runs 4 --concurrency 2
```

The benchmark reports elapsed time, audio duration, real-time factor, wall-clock throughput, and the effective CPU policy. It deliberately bypasses the response cache for each measured synthesis.

## Docker Deployment

The Dockerfile pre-downloads the real Supertonic assets, selects the balanced CPU profile, and enables startup warm-up. Build and run it locally:

```bash
docker build -t nastech-compact:0.8.0 .
docker images nastech-compact:0.8.0

docker run --rm -p 8765:8765 \
  -e NASTECH_API_KEY='choose-a-secret' \
  nastech-compact:0.8.0
```

Override the CPU profile or cap the container’s CPU allocation explicitly when required by the host policy. If Docker CPU limits are used, set matching Nastech thread values rather than assuming host-wide logical CPU detection reflects the container’s quota.

```bash
docker run --rm -p 8765:8765 --cpus=4 \
  -e NASTECH_API_KEY='choose-a-secret' \
  -e NASTECH_CPU_PROFILE=balanced \
  -e NASTECH_INTRA_OP_THREADS=4 \
  -e NASTECH_INTER_OP_THREADS=1 \
  nastech-compact:0.8.0
```

## Agent Authentication

Set `NASTECH_API_KEY` outside source control. Protected endpoints require:

```text
Authorization: Bearer <NASTECH_API_KEY>
```

Put any Internet-facing deployment behind TLS and a reverse proxy. If a local device is the deployment target, bind to loopback by default and explicitly opt in to a network interface only when needed.

## Persistent-Service Boundary

The current sandbox can build and test the compact system but hibernates when inactive. For a persistent API, deploy the same package or Docker image to a persistent CPU server. No GPU system is required for the selected Supertonic runtime.
