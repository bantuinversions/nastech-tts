# Nastech TTS Cross-Platform Base-Timbre Benchmark

All runs use the same plain-English text, one warmed local runtime per runner, serial cache-disabled synthesis, three warm runs per timbre, CPU mode, and the same deterministic 44.1 kHz WAV quality controls.

## Platform summary

| Platform | Runner architecture | CPUs | Device | Mean warm s | Mean RTF | Fastest | Slowest | Sampled memory MiB | Process peak MiB | WAV gates |
|---|---|---:|---|---:|---:|---|---|---:|---:|---|
| Linux 6.17.0-1022-azure | x86_64 | 4 | cpu | 2.3538 | 0.3115 | M3 (1.9504s) | M1 (2.7487s) | 641.0442 | 644.3024 | True |
| Darwin 25.5.0 | arm64 | 3 | cpu | 1.7944 | 0.2375 | M3 (1.5650s) | F1 (2.0995s) | None | 818.0401 | True |
| Windows 2025Server | AMD64 | 4 | cpu | 2.8885 | 0.3825 | M3 (2.5309s) | M5 (3.5285s) | 564.8183 | 574.3066 | True |

## Per-timbre results

| Platform | Timbre | Warm mean s | Warm median s | Mean RTF | Audio s | RMS dBFS | Peak dBFS | Clip | Hz |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Linux | F1 | 2.3874 | 2.3825 | 0.3011 | 7.9284 | -26.6003 | -9.9314 | 0 | 44100 |
| Linux | F2 | 2.5582 | 2.2391 | 0.3438 | 7.4405 | -26.7804 | -8.4026 | 0 | 44100 |
| Linux | F3 | 2.4153 | 2.4204 | 0.2954 | 8.1753 | -26.7485 | -8.4726 | 0 | 44100 |
| Linux | F4 | 2.1354 | 2.1201 | 0.3139 | 6.8030 | -25.9283 | -9.5921 | 0 | 44100 |
| Linux | F5 | 2.2329 | 2.2404 | 0.2906 | 7.6828 | -25.5233 | -10.4524 | 0 | 44100 |
| Linux | M1 | 2.7487 | 2.3850 | 0.3464 | 7.9342 | -26.6588 | -6.6064 | 0 | 44100 |
| Linux | M2 | 2.1961 | 2.1991 | 0.2827 | 7.7690 | -25.9661 | -4.2094 | 0 | 44100 |
| Linux | M3 | 1.9504 | 1.9569 | 0.2993 | 6.5158 | -25.8198 | -9.2834 | 0 | 44100 |
| Linux | M4 | 2.5391 | 2.2247 | 0.3422 | 7.4203 | -25.4638 | -9.9873 | 0 | 44100 |
| Linux | M5 | 2.3741 | 2.3564 | 0.2998 | 7.9180 | -26.0096 | -9.3827 | 0 | 44100 |
| Darwin | F1 | 2.0995 | 2.0330 | 0.2648 | 7.9284 | -26.7195 | -9.8034 | 0 | 44100 |
| Darwin | F2 | 1.7983 | 1.6750 | 0.2417 | 7.4405 | -26.863 | -8.8696 | 0 | 44100 |
| Darwin | F3 | 1.8963 | 1.8874 | 0.2319 | 8.1753 | -27.0207 | -7.9646 | 0 | 44100 |
| Darwin | F4 | 1.6468 | 1.6180 | 0.2421 | 6.8030 | -25.6002 | -8.3456 | 0 | 44100 |
| Darwin | F5 | 1.8565 | 1.8182 | 0.2417 | 7.6828 | -25.5238 | -9.9848 | 0 | 44100 |
| Darwin | M1 | 1.8406 | 1.8357 | 0.2320 | 7.9342 | -26.7858 | -4.6931 | 0 | 44100 |
| Darwin | M2 | 1.6977 | 1.6805 | 0.2185 | 7.7690 | -24.9637 | -2.6131 | 0 | 44100 |
| Darwin | M3 | 1.5650 | 1.4309 | 0.2402 | 6.5158 | -25.2803 | -8.3684 | 0 | 44100 |
| Darwin | M4 | 1.6916 | 1.6577 | 0.2280 | 7.4203 | -25.8573 | -10.0377 | 0 | 44100 |
| Darwin | M5 | 1.8516 | 1.8277 | 0.2339 | 7.9180 | -25.9595 | -10.1061 | 0 | 44100 |
| Windows | F1 | 2.8546 | 2.8312 | 0.3600 | 7.9284 | -26.0079 | -9.9139 | 0 | 44100 |
| Windows | F2 | 2.8594 | 2.9237 | 0.3843 | 7.4405 | -26.421 | -8.7092 | 0 | 44100 |
| Windows | F3 | 2.9101 | 2.8912 | 0.3560 | 8.1753 | -27.5544 | -8.6955 | 0 | 44100 |
| Windows | F4 | 2.6014 | 2.5885 | 0.3824 | 6.8030 | -25.5037 | -10.0554 | 0 | 44100 |
| Windows | F5 | 2.8870 | 2.8746 | 0.3758 | 7.6828 | -25.3603 | -10.6434 | 0 | 44100 |
| Windows | M1 | 2.8688 | 2.8336 | 0.3616 | 7.9342 | -26.8738 | -6.7534 | 0 | 44100 |
| Windows | M2 | 2.7053 | 2.7083 | 0.3482 | 7.7690 | -25.3004 | -4.4137 | 0 | 44100 |
| Windows | M3 | 2.5309 | 2.5388 | 0.3884 | 6.5158 | -25.2826 | -9.5411 | 0 | 44100 |
| Windows | M4 | 3.1388 | 3.0812 | 0.4230 | 7.4203 | -25.948 | -10.4993 | 0 | 44100 |
| Windows | M5 | 3.5285 | 3.4876 | 0.4456 | 7.9180 | -25.78 | -9.2626 | 0 | 44100 |

## Interpretation boundary

Performance is measured on hosted CI runners, so results are runner measurements rather than universal desktop guarantees. Native memory collection differs by operating system: Linux uses `/proc/self/status`, macOS uses `resource.getrusage`, and Windows uses `GetProcessMemoryInfo`. The memory-source field in each raw report must be retained when comparing platforms. WAV gates verify digital file integrity and level hygiene; they do not provide a subjective naturalness or linguistic-quality score.
