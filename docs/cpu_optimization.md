# Nastech Compact CPU Optimization Report

## Scope

Nastech Compact v0.5.0 runs **Supertonic 3** locally through ONNX Runtime on CPU. The optimizer layer preserves one model family and real local inference; it does not introduce a cloud proxy, GPU dependency, model merge, quantization substitute, or second fallback model. Supertonic’s loader exposes ONNX Runtime intra-operation and inter-operation thread controls and enables full graph optimization for its model sessions. [1]

## Implemented Controls

| Control | Implementation | Operational effect |
|---|---|---|
| CPU profiles | `balanced`, `latency`, `throughput`, and `auto` | Gives safe defaults for common server patterns while retaining host-specific overrides |
| ONNX thread tuning | `NASTECH_INTRA_OP_THREADS` and `NASTECH_INTER_OP_THREADS` | Passes explicit worker counts to local Supertonic ONNX sessions |
| Bounded scheduling | `NASTECH_MAX_PARALLEL_SYNTHESIS` plus `NASTECH_QUEUE_TIMEOUT_SECONDS` | Prevents unrestricted request-level CPU oversubscription |
| Response cache | Bounded LRU in-memory WAV cache | Reuses identical recent local responses without growing disk state |
| Warm-up | CLI, API endpoint, and optional startup lifecycle warm-up | Preloads sessions and a voice style before user traffic |
| Diagnostics | Authenticated runtime endpoint and expanded status command | Surfaces the active CPU policy, model/cache size, queue time, failures, and mean synthesis time |
| Reproducible benchmark | Cache-bypassing CLI with parallel workload option | Measures ONNX synthesis instead of a memory-cache hit |

The upstream model’s execution stage is sequential because its ONNX modules have dependent phases. Nastech therefore defaults to one active synthesis with a capped intra-operation worker count instead of attempting unsafe parallel execution inside a single request. [1]

## Verified Local Environment

| Resource | Verified value |
|---|---:|
| CPU | Intel Xeon, 6 logical CPUs |
| Available RAM | 23 GiB |
| Model assets | 384.83 MiB |
| Python runtime and dependencies | 260.68 MiB |
| Release assets | 2.00 MiB |
| Full measured deployment | **647.51 MiB** |
| Headroom below 1 GiB | **376.49 MiB** |

## Benchmark Evidence

The expressive test document was `examples/compact_agent_story.xml`, producing a 12.04-second 44.1 kHz WAV. Benchmarks were run after local warm-up. Every measured synthesis bypassed Nastech’s WAV response cache.

| Profile | Workload | Result |
|---|---|---|
| `balanced` | 3 sequential real syntheses | 2.1634 seconds mean synthesis time; 0.1796 mean real-time factor |
| `latency` | 3 sequential real syntheses | 2.1287 seconds mean synthesis time; 0.1767 mean real-time factor |
| `throughput` | 4 real syntheses scheduled by 2 clients | 5.2780 seconds wall-clock; 0.7579 requests/second; 2.6052 seconds mean per request |
| `balanced` API | Startup warm-up, diagnostics, then expressive API request | All endpoints returned HTTP 200; optimized agent synthesis produced a 251,948-byte WAV |

The difference between `balanced` and `latency` on this host is small. `balanced` remains the deployment default because it avoids consuming all detected logical CPUs and leaves room for the web server and surrounding workload. Select `latency` only after measuring the dedicated target machine.

## Operator Procedure

```bash
# Examine active policy before traffic.
nastech-tts status

# Preload ONNX sessions and default style.
nastech-tts warmup

# Benchmark one interactive synthesis at a time.
NASTECH_CPU_PROFILE=balanced \
  nastech-tts benchmark examples/compact_agent_story.xml --runs 3

# Verify safe two-client throughput.
NASTECH_CPU_PROFILE=throughput \
  nastech-tts benchmark examples/compact_agent_story.xml --runs 4 --concurrency 2
```

Use `GET /v1/runtime/diagnostics` during operation to confirm the effective policy. If deploying with a CPU quota, explicitly set the intra-operation and inter-operation thread counts to match the allocated quota, then repeat the benchmark.

## References

[1] [Supertonic Python SDK: ONNX Runtime threading and loader configuration](https://github.com/supertone-inc/supertonic-py)
