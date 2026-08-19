"""Validate the stable Nastech base-timbre benchmark report contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmark_base_timbres import BASE_TIMBRES


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--runs", type=int, required=True)
    return parser.parse_args()


def validate(payload: dict[str, object], runs: int) -> None:
    """Raise ``ValueError`` when a platform report is incomplete or fails audio gates."""

    voices = payload.get("voices")
    if not isinstance(voices, list) or len(voices) != len(BASE_TIMBRES):
        raise ValueError("Benchmark report must contain all ten base timbres.")
    if {item.get("voice") for item in voices} != set(BASE_TIMBRES):
        raise ValueError("Benchmark report has an unexpected base-timbre set.")
    for voice in voices:
        warm_runs = voice.get("warm_runs")
        if not isinstance(warm_runs, list) or len(warm_runs) != runs:
            raise ValueError(f"{voice.get('voice')} has an unexpected warm-run count.")
        for run in warm_runs:
            quality = run.get("audio_quality")
            if not isinstance(quality, dict):
                raise ValueError(f"{voice.get('voice')} has no audio quality report.")
            if quality.get("sample_rate_hz") != 44100:
                raise ValueError(f"{voice.get('voice')} did not produce 44.1 kHz output.")
            if quality.get("clipped_samples") != 0 or quality.get("rms_dbfs") is None:
                raise ValueError(f"{voice.get('voice')} failed the audio quality gate.")


def main() -> int:
    args = _args()
    if args.runs < 1 or args.runs > 20:
        raise SystemExit("--runs must be between 1 and 20.")
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    validate(payload, args.runs)
    print(f"Validated {len(BASE_TIMBRES)} timbres and {args.runs} warm runs each.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
