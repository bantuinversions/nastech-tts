#!/usr/bin/env python3
"""Run the Nastech behavior fidelity suite without downloading model weights."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from nastech_tts.evaluation import run_behavior_suite


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a Nastech behavior fidelity suite.")
    parser.add_argument("suite", help="Path to a behavior-suite JSON file.")
    args = parser.parse_args()
    results = run_behavior_suite(args.suite)
    payload = {
        "total": len(results),
        "passed": sum(result.passed for result in results),
        "failed": sum(not result.passed for result in results),
        "results": [asdict(result) for result in results],
    }
    print(json.dumps(payload, indent=2))
    return 0 if payload["failed"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
