"""Render one Nastech base-timbre benchmark JSON report as a detailed Markdown table."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def _mean(values: list[float | None]) -> float | None:
    real = [value for value in values if value is not None]
    return round(statistics.fmean(real), 4) if real else None


def _quality_status(quality: dict[str, object]) -> str:
    return (
        "pass" if quality["clipped_samples"] == 0 and quality["rms_dbfs"] is not None else "review"
    )


def main() -> int:
    args = _args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    host = payload["host"]
    rows = []
    for entry in payload["voices"]:
        warm_runs = entry["warm_runs"]
        quality = warm_runs[0]["audio_quality"]
        sampled_memory = _mean(
            [item["memory_during"]["peak_sampled_current_mib"] for item in warm_runs]
        )
        process_peak = _mean(
            [item["memory_during"]["peak_observed_process_mib"] for item in warm_runs]
        )
        rows.append(
            {
                "voice": entry["voice"],
                "first": entry["first_synthesis_seconds"],
                "mean": entry["warm_summary"]["mean_elapsed_seconds"],
                "median": entry["warm_summary"]["median_elapsed_seconds"],
                "rtf": entry["warm_summary"]["mean_real_time_factor"],
                "audio": entry["warm_summary"]["mean_audio_seconds"],
                "sampled_memory": sampled_memory,
                "process_peak": process_peak,
                "rms": quality["rms_dbfs"],
                "peak": quality["peak_dbfs"],
                "clipped": quality["clipped_samples"],
                "rate": quality["sample_rate_hz"],
                "status": _quality_status(quality),
            }
        )
    fastest = min(rows, key=lambda row: row["mean"])
    slowest = max(rows, key=lambda row: row["mean"])
    all_audio_passed = all(row["status"] == "pass" for row in rows)
    lines = [
        "# Nastech TTS Base-Timbre Benchmark",
        "",
        "## Measured host",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Operating system | {host['system']} {host['release']} |",
        f"| Machine | {host['machine']} |",
        f"| Python | {host['python']} |",
        f"| Logical CPUs | {host['logical_cpus']} |",
        f"| Selected device | {host['hardware_plan']['device']} |",
        f"| Memory observation | {host['initial_memory']['source']} |",
        "",
        "## Results",
        "",
        "| Timbre | First s | Warm mean s | Warm median s | Mean RTF | Audio s | "
        "Sampled RSS MiB | Process peak MiB | RMS dBFS | Peak dBFS | Clip | Hz | Quality gate |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            (
                "| {voice} | {first:.4f} | {mean:.4f} | {median:.4f} | "
                "{rtf:.4f} | {audio:.4f} | {sampled_memory} | {process_peak} | "
                "{rms} | {peak} | {clipped} | {rate} | {status} |"
            ).format(**row)
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"The fastest warm measurement was **{fastest['voice']}** at "
            f"**{fastest['mean']:.4f} seconds**. The slowest was **{slowest['voice']}** at "
            f"**{slowest['mean']:.4f} seconds**. Every reported run used the same fixed text, "
            "one warmed local runtime, serial cache-disabled synthesis, and the same local "
            "CPU policy.",
            "",
            "All deterministic audio gates passed."
            if all_audio_passed
            else "One or more audio gates need review.",
            "The audio controls verify WAV format, duration, RMS level, peak level, "
            "DC behavior, and full-scale clipping. They do not measure subjective "
            "naturalness, language quality, or speaker identity.",
            "",
            "> **Cross-platform comparison boundary:** Native memory signals use different "
            "operating-system interfaces. Compare absolute memory figures chiefly within the same "
            "runner class; the report preserves its source field so platform results "
            "are not treated as identical metrics.",
            "",
        ]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
