# Nastech TTS Base-Timbre Benchmark

## Measured host

| Field | Value |
|---|---|
| Operating system | Windows 2025Server |
| Machine | AMD64 |
| Python | 3.12.10 |
| Logical CPUs | 4 |
| Selected device | cpu |
| Memory observation | Windows GetProcessMemoryInfo (working set) |

## Results

| Timbre | First s | Warm mean s | Warm median s | Mean RTF | Audio s | Sampled RSS MiB | Process peak MiB | RMS dBFS | Peak dBFS | Clip | Hz | Quality gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| F1 | 3.0995 | 2.8546 | 2.8312 | 0.3600 | 7.9284 | 552.996 | 561.1587 | -26.0079 | -9.9139 | 0 | 44100 | pass |
| F2 | 2.7875 | 2.8594 | 2.9237 | 0.3843 | 7.4405 | 556.5347 | 566.5347 | -26.421 | -8.7092 | 0 | 44100 | pass |
| F3 | 3.1094 | 2.9101 | 2.8912 | 0.3560 | 8.1753 | 559.4647 | 571.7083 | -27.5544 | -8.6955 | 0 | 44100 | pass |
| F4 | 2.8952 | 2.6014 | 2.5885 | 0.3824 | 6.8030 | 562.82 | 573.148 | -25.5037 | -10.0554 | 0 | 44100 | pass |
| F5 | 3.0354 | 2.8870 | 2.8746 | 0.3758 | 7.6828 | 565.9377 | 574.4323 | -25.3603 | -10.6434 | 0 | 44100 | pass |
| M1 | 3.1306 | 2.8688 | 2.8336 | 0.3616 | 7.9342 | 568.7137 | 576.7123 | -26.8738 | -6.7534 | 0 | 44100 | pass |
| M2 | 3.1022 | 2.7053 | 2.7083 | 0.3482 | 7.7690 | 571.897 | 578.296 | -25.3004 | -4.4137 | 0 | 44100 | pass |
| M3 | 2.6118 | 2.5309 | 2.5388 | 0.3884 | 6.5158 | 573.199 | 578.5 | -25.2826 | -9.5411 | 0 | 44100 | pass |
| M4 | 3.3877 | 3.1388 | 3.0812 | 0.4230 | 7.4203 | 574.4193 | 581.0287 | -25.948 | -10.4993 | 0 | 44100 | pass |
| M5 | 3.4607 | 3.5285 | 3.4876 | 0.4456 | 7.9180 | 562.2007 | 581.547 | -25.78 | -9.2626 | 0 | 44100 | pass |

## Interpretation

The fastest warm measurement was **M3** at **2.5309 seconds**. The slowest was **M5** at **3.5285 seconds**. Every reported run used the same fixed text, one warmed local runtime, serial cache-disabled synthesis, and the same local CPU policy.

All deterministic audio gates passed.
The audio controls verify WAV format, duration, RMS level, peak level, DC behavior, and full-scale clipping. They do not measure subjective naturalness, language quality, or speaker identity.

> **Cross-platform comparison boundary:** Native memory signals use different operating-system interfaces. Compare absolute memory figures chiefly within the same runner class; the report preserves its source field so platform results are not treated as identical metrics.
