# Nastech TTS Base-Timbre Benchmark

## Measured host

| Field | Value |
|---|---|
| Operating system | Linux 6.17.0-1022-azure |
| Machine | x86_64 |
| Python | 3.12.13 |
| Logical CPUs | 4 |
| Selected device | cpu |
| Memory observation | /proc/self/status (VmRSS/VmHWM) |

## Results

| Timbre | First s | Warm mean s | Warm median s | Mean RTF | Audio s | Sampled RSS MiB | Process peak MiB | RMS dBFS | Peak dBFS | Clip | Hz | Quality gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| F1 | 2.5043 | 2.3874 | 2.3825 | 0.3011 | 7.9284 | 635.237 | 638.9853 | -26.6003 | -9.9314 | 0 | 44100 | pass |
| F2 | 2.4561 | 2.5582 | 2.2391 | 0.3438 | 7.4405 | 637.9587 | 643.0793 | -26.7804 | -8.4026 | 0 | 44100 | pass |
| F3 | 2.4836 | 2.4153 | 2.4204 | 0.2954 | 8.1753 | 639.866 | 644.811 | -26.7485 | -8.4726 | 0 | 44100 | pass |
| F4 | 2.2275 | 2.1354 | 2.1201 | 0.3139 | 6.8030 | 640.1977 | 645.164 | -25.9283 | -9.5921 | 0 | 44100 | pass |
| F5 | 2.3305 | 2.2329 | 2.2404 | 0.2906 | 7.6828 | 639.9127 | 645.164 | -25.5233 | -10.4524 | 0 | 44100 | pass |
| M1 | 2.4547 | 2.7487 | 2.3850 | 0.3464 | 7.9342 | 641.8347 | 645.164 | -26.6588 | -6.6064 | 0 | 44100 | pass |
| M2 | 2.3827 | 2.1961 | 2.1991 | 0.2827 | 7.7690 | 643.352 | 645.164 | -25.9661 | -4.2094 | 0 | 44100 | pass |
| M3 | 2.0329 | 1.9504 | 1.9569 | 0.2993 | 6.5158 | 643.965 | 645.164 | -25.8198 | -9.2834 | 0 | 44100 | pass |
| M4 | 2.3022 | 2.5391 | 2.2247 | 0.3422 | 7.4203 | 644.2367 | 645.164 | -25.4638 | -9.9873 | 0 | 44100 | pass |
| M5 | 2.4540 | 2.3741 | 2.3564 | 0.2998 | 7.9180 | 643.8813 | 645.164 | -26.0096 | -9.3827 | 0 | 44100 | pass |

## Interpretation

The fastest warm measurement was **M3** at **1.9504 seconds**. The slowest was **M1** at **2.7487 seconds**. Every reported run used the same fixed text, one warmed local runtime, serial cache-disabled synthesis, and the same local CPU policy.

All deterministic audio gates passed.
The audio controls verify WAV format, duration, RMS level, peak level, DC behavior, and full-scale clipping. They do not measure subjective naturalness, language quality, or speaker identity.

> **Cross-platform comparison boundary:** Native memory signals use different operating-system interfaces. Compare absolute memory figures chiefly within the same runner class; the report preserves its source field so platform results are not treated as identical metrics.
