"""Compare validated Nastech base-timbre benchmark reports from multiple platforms."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def _load_reports(root: Path) -> list[dict[str, Any]]:
    paths = sorted(
        path
        for path in root.glob("nastech-base-timbre-benchmark-*/*.json")
        if path.name.startswith("nastech-base-timbres-")
    )
    if len(paths) != 3:
        raise ValueError(f"Expected three platform reports under {root}, found {len(paths)}.")
    reports = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    systems = {report["host"]["system"] for report in reports}
    if systems != {"Linux", "Darwin", "Windows"}:
        raise ValueError(
            f"Expected Linux, Darwin, and Windows reports; received {sorted(systems)}."
        )
    return reports


def _mean_memory(entries: list[dict[str, Any]], key: str) -> float | None:
    values = [
        run["memory_during"][key]
        for entry in entries
        for run in entry["warm_runs"]
        if run["memory_during"][key] is not None
    ]
    return round(statistics.fmean(values), 4) if values else None


def _platform_summary(report: dict[str, Any]) -> dict[str, Any]:
    voices = report["voices"]
    warm = [entry["warm_summary"] for entry in voices]
    fastest = min(voices, key=lambda entry: entry["warm_summary"]["mean_elapsed_seconds"])
    slowest = max(voices, key=lambda entry: entry["warm_summary"]["mean_elapsed_seconds"])
    sample = voices[0]["warm_runs"][0]
    return {
        "system": report["host"]["system"],
        "release": report["host"]["release"],
        "machine": report["host"]["machine"],
        "cpus": report["host"]["logical_cpus"],
        "device": report["host"]["hardware_plan"]["device"],
        "mean_elapsed": round(statistics.fmean(item["mean_elapsed_seconds"] for item in warm), 4),
        "mean_rtf": round(statistics.fmean(item["mean_real_time_factor"] for item in warm), 4),
        "fastest": fastest["voice"],
        "fastest_seconds": fastest["warm_summary"]["mean_elapsed_seconds"],
        "slowest": slowest["voice"],
        "slowest_seconds": slowest["warm_summary"]["mean_elapsed_seconds"],
        "sampled_memory": _mean_memory(voices, "peak_sampled_current_mib"),
        "process_peak": _mean_memory(voices, "peak_observed_process_mib"),
        "memory_source": sample["memory_during"]["source"],
        "quality_pass": all(
            run["audio_quality"]["clipped_samples"] == 0
            and run["audio_quality"]["rms_dbfs"] is not None
            and run["audio_quality"]["sample_rate_hz"] == 44100
            for entry in voices
            for run in entry["warm_runs"]
        ),
    }


def _detail_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for entry in report["voices"]:
        quality = entry["warm_runs"][0]["audio_quality"]
        rows.append(
            {
                "system": report["host"]["system"],
                "voice": entry["voice"],
                "mean": entry["warm_summary"]["mean_elapsed_seconds"],
                "median": entry["warm_summary"]["median_elapsed_seconds"],
                "rtf": entry["warm_summary"]["mean_real_time_factor"],
                "audio": entry["warm_summary"]["mean_audio_seconds"],
                "rms": quality["rms_dbfs"],
                "peak": quality["peak_dbfs"],
                "clipped": quality["clipped_samples"],
                "rate": quality["sample_rate_hz"],
            }
        )
    return rows


def main() -> int:
    args = _args()
    reports = _load_reports(args.input_dir)
    summaries = [_platform_summary(report) for report in reports]
    details = [row for report in reports for row in _detail_rows(report)]
    lines = [
        "# Nastech TTS Cross-Platform Base-Timbre Benchmark",
        "",
        "All runs use the same plain-English text, one warmed local runtime per runner, "
        "serial cache-disabled synthesis, three warm runs per timbre, CPU mode, and the "
        "same deterministic 44.1 kHz WAV quality controls.",
        "",
        "## Platform summary",
        "",
        "| Platform | Runner architecture | CPUs | Device | Mean warm s | Mean RTF | Fastest | "
        "Slowest | Sampled memory MiB | Process peak MiB | WAV gates |",
        "|---|---|---:|---|---:|---:|---|---|---:|---:|---|",
    ]
    for row in summaries:
        lines.append(
            "| {system} {release} | {machine} | {cpus} | {device} | {mean_elapsed:.4f} | "
            "{mean_rtf:.4f} | {fastest} ({fastest_seconds:.4f}s) | "
            "{slowest} ({slowest_seconds:.4f}s) | {sampled_memory} | {process_peak} | "
            "{quality_pass} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Per-timbre results",
            "",
            "| Platform | Timbre | Warm mean s | Warm median s | Mean RTF | Audio s | RMS dBFS | "
            "Peak dBFS | Clip | Hz |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in details:
        lines.append(
            "| {system} | {voice} | {mean:.4f} | {median:.4f} | {rtf:.4f} | {audio:.4f} | "
            "{rms} | {peak} | {clipped} | {rate} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "Performance is measured on hosted CI runners, so results are runner measurements "
            "rather than universal desktop guarantees. Native memory collection differs by "
            "operating system: Linux uses `/proc/self/status`, macOS uses `resource.getrusage`, "
            "and Windows uses `GetProcessMemoryInfo`. The memory-source field in each raw report "
            "must be retained when comparing platforms. WAV gates verify digital file integrity "
            "and level hygiene; they do not provide a subjective naturalness or linguistic-quality "
            "score.",
            "",
        ]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
