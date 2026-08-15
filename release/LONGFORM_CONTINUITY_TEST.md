# Nastech 30-Minute Local Continuity Test

## Release Evidence

This release test proves a real local **30-minute English continuity render** through the active `nastech-native-onnx` provider. The file was not extended with a loop, silence padding, time-stretching, or a repeated WAV. The generator rendered **53 unique NastechML narrative segments** locally, cleaned every segment with the deterministic PCM stage, joined the PCM frames, and truncated only the final rendered segment at the exact 1,800-second boundary.

> **Scope boundary:** This is a digital-audio continuity and stability test. Its successful completion verifies duration, WAV structure, sample rate, channels, clipping, RMS level, and DC offset. It does not by itself establish human linguistic quality, a regional accent, or a speaker-identity claim.

| Test field | Verified value |
|---|---:|
| Active provider | `nastech-native-onnx` local CPU provider |
| Long-form preset style | `F1` |
| Target duration | 1,800.00 seconds |
| Actual duration | **1,800.00 seconds (30 minutes)** |
| Rendered segments | 53 unique local synthesis segments |
| Format | Mono, 16-bit PCM WAV |
| Sample rate | 44,100 Hz |
| Frames | 79,380,000 |
| Peak level | -4.9288 dBFS |
| RMS level | -25.3603 dBFS |
| DC offset | -0.5743 PCM |
| Digital full-scale clipping | 0 samples |
| SHA-256 | `14deb50c8005ada0b5b2503441fd5ba700330a765dfc330edf39bedc3187a0ee` |

The resulting `nastech-continuity-30min.wav` is approximately 152 MiB and is intentionally published as a **draft-release asset**, not committed to Git history. The source NastechML, detailed per-segment compiler/cleanup evidence, per-voice auditions, and a machine-readable manifest accompany it in the release artifact set.

## Preset-Style Auditions

Four short real local auditions use distinct verified preset style IDs. The IDs are speaker-style labels only; they are not advertised as regional, national, ethnic, or dialect labels.

| Preset-style ID | Measured duration | Sample rate | Clipping | Release result |
|---|---:|---:|---:|---|
| `M1` | 11.08 seconds | 44,100 Hz | 0 samples | Passed |
| `M3` | 9.13 seconds | 44,100 Hz | 0 samples | Passed |
| `F1` | 11.08 seconds | 44,100 Hz | 0 samples | Passed |
| `F3` | 11.42 seconds | 44,100 Hz | 0 samples | Passed |

The detailed file-level values, checksums, compiler manifests, and cleanup reports are stored in `longform-continuity-manifest.json`. The product’s full verified-preset and regional-profile claim boundary is described in [VOICE_INVENTORY.md](../docs/VOICE_INVENTORY.md).

## Reproduction

```bash
source /home/ubuntu/nastech-compact-venv/bin/activate
cd /home/ubuntu/nastech-tts
python scripts/generate_longform_continuity_test.py \
  --target-seconds 1800 \
  --output-dir release/longform_continuity \
  --max-chunks 96
```

The command creates four auditions and the exact-length continuity WAV, then applies deterministic release-level gates before writing `longform-continuity-manifest.json`.
