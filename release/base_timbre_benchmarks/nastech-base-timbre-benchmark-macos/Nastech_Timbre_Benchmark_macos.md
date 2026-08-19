# Nastech TTS Base-Timbre Benchmark

## Measured host

| Field | Value |
|---|---|
| Operating system | Darwin 25.5.0 |
| Machine | arm64 |
| Python | 3.12.10 |
| Logical CPUs | 3 |
| Selected device | cpu |
| Memory observation | resource.getrusage (process peak; current RSS unavailable on this platform) |

## Results

| Timbre | First s | Warm mean s | Warm median s | Mean RTF | Audio s | Sampled RSS MiB | Process peak MiB | RMS dBFS | Peak dBFS | Clip | Hz | Quality gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| F1 | 3.4739 | 2.0995 | 2.0330 | 0.2648 | 7.9284 | None | 803.4167 | -26.7195 | -9.8034 | 0 | 44100 | pass |
| F2 | 1.7514 | 1.7983 | 1.6750 | 0.2417 | 7.4405 | None | 812.3907 | -26.863 | -8.8696 | 0 | 44100 | pass |
| F3 | 1.9281 | 1.8963 | 1.8874 | 0.2319 | 8.1753 | None | 818.5313 | -27.0207 | -7.9646 | 0 | 44100 | pass |
| F4 | 1.9604 | 1.6468 | 1.6180 | 0.2421 | 6.8030 | None | 820.625 | -25.6002 | -8.3456 | 0 | 44100 | pass |
| F5 | 1.7239 | 1.8565 | 1.8182 | 0.2417 | 7.6828 | None | 820.625 | -25.5238 | -9.9848 | 0 | 44100 | pass |
| M1 | 1.9007 | 1.8406 | 1.8357 | 0.2320 | 7.9342 | None | 820.625 | -26.7858 | -4.6931 | 0 | 44100 | pass |
| M2 | 2.0354 | 1.6977 | 1.6805 | 0.2185 | 7.7690 | None | 820.625 | -24.9637 | -2.6131 | 0 | 44100 | pass |
| M3 | 1.5301 | 1.5650 | 1.4309 | 0.2402 | 6.5158 | None | 820.625 | -25.2803 | -8.3684 | 0 | 44100 | pass |
| M4 | 1.7075 | 1.6916 | 1.6577 | 0.2280 | 7.4203 | None | 820.625 | -25.8573 | -10.0377 | 0 | 44100 | pass |
| M5 | 2.6723 | 1.8516 | 1.8277 | 0.2339 | 7.9180 | None | 822.3127 | -25.9595 | -10.1061 | 0 | 44100 | pass |

## Interpretation

The fastest warm measurement was **M3** at **1.5650 seconds**. The slowest was **F1** at **2.0995 seconds**. Every reported run used the same fixed text, one warmed local runtime, serial cache-disabled synthesis, and the same local CPU policy.

All deterministic audio gates passed.
The audio controls verify WAV format, duration, RMS level, peak level, DC behavior, and full-scale clipping. They do not measure subjective naturalness, language quality, or speaker identity.

> **Cross-platform comparison boundary:** Native memory signals use different operating-system interfaces. Compare absolute memory figures chiefly within the same runner class; the report preserves its source field so platform results are not treated as identical metrics.
