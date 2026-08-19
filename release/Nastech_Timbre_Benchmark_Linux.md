# Nastech TTS Base-Timbre Benchmark

## Measured host

| Field | Value |
|---|---|
| Operating system | Linux 6.18.38+ |
| Machine | x86_64 |
| Python | 3.12.3 |
| Logical CPUs | 6 |
| Selected device | cpu |
| Memory observation | /proc/self/status (VmRSS/VmHWM) |

## Results

| Timbre | First s | Warm mean s | Warm median s | Mean RTF | Audio s | Sampled RSS MiB | Process peak MiB | RMS dBFS | Peak dBFS | Clip | Hz | Quality gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| F1 | 1.5580 | 1.4584 | 1.4448 | 0.1840 | 7.9284 | 520.5537 | 524.947 | -26.1006 | -8.8205 | 0 | 44100 | pass |
| F2 | 1.3485 | 1.6008 | 1.5928 | 0.2151 | 7.4405 | 522.9727 | 528.098 | -26.8321 | -6.9376 | 0 | 44100 | pass |
| F3 | 1.5048 | 1.4609 | 1.4430 | 0.1787 | 8.1753 | 525.1237 | 530.5003 | -26.5791 | -7.9368 | 0 | 44100 | pass |
| F4 | 1.2978 | 1.3385 | 1.2888 | 0.1968 | 6.8030 | 527.0077 | 530.805 | -25.542 | -10.4816 | 0 | 44100 | pass |
| F5 | 1.6294 | 1.3243 | 1.3195 | 0.1724 | 7.6828 | 528.6133 | 530.805 | -25.773 | -8.5029 | 0 | 44100 | pass |
| M1 | 1.4741 | 1.4093 | 1.3997 | 0.1776 | 7.9342 | 529.6863 | 530.8453 | -27.3101 | -7.5978 | 0 | 44100 | pass |
| M2 | 1.3468 | 1.3492 | 1.3871 | 0.1737 | 7.7690 | 530.8007 | 530.9723 | -25.414 | -3.7448 | 0 | 44100 | pass |
| M3 | 1.4578 | 1.3643 | 1.3183 | 0.2094 | 6.5158 | 531.207 | 531.207 | -25.6856 | -9.1752 | 0 | 44100 | pass |
| M4 | 1.3553 | 1.2845 | 1.2810 | 0.1731 | 7.4203 | 531.5923 | 531.5923 | -26.2255 | -10.4233 | 0 | 44100 | pass |
| M5 | 1.4513 | 1.4074 | 1.4038 | 0.1777 | 7.9180 | 531.302 | 531.802 | -25.4328 | -8.2931 | 0 | 44100 | pass |

## Interpretation

The fastest warm measurement was **M4** at **1.2845 seconds**. The slowest was **F2** at **1.6008 seconds**. Every reported run used the same fixed text, one warmed local runtime, serial cache-disabled synthesis, and the same local CPU policy.

All deterministic audio gates passed.
The audio controls verify WAV format, duration, RMS level, peak level, DC behavior, and full-scale clipping. They do not measure subjective naturalness, language quality, or speaker identity.

> **Cross-platform comparison boundary:** Native memory signals use different operating-system interfaces. Compare absolute memory figures chiefly within the same runner class; the report preserves its source field so platform results are not treated as identical metrics.
