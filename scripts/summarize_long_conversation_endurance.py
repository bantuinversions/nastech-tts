"""Print a concise machine-readable summary of a Nastech endurance report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    return parser.parse_args()


def main() -> int:
    report = json.loads(_args().report.read_text(encoding="utf-8"))
    observed = report["observed"]
    quality = report["quality"]
    coverage = report["coverage"]
    summary = {
        "status": report["status"],
        "requested_audio_seconds": report["contract"]["requested_duration_seconds"],
        "observed_audio_seconds": observed["assembled_audio_seconds"],
        "elapsed_minutes": observed["elapsed_minutes"],
        "overall_real_time_factor": observed["overall_real_time_factor"],
        "segments": observed["segment_count"],
        "peak_observed_rss_mib": observed["peak_observed_rss_mib"],
        "clipped_samples": quality["clipped_samples"],
        "missing_voice_profiles": coverage["missing_voice_profiles"],
        "missing_emotion_controls": coverage["missing_emotion_controls"],
        "missing_sound_cues": coverage["missing_sound_cues"],
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
