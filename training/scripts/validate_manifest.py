#!/usr/bin/env python3
"""Validate a Nastech expressive-speech JSONL manifest before tokenization or training."""

from __future__ import annotations

import argparse
import json

from nastech_tts.training import DatasetValidationError, validate_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Nastech expressive-speech training records.")
    parser.add_argument("manifest", help="Path to a JSONL manifest of licensed audio records.")
    args = parser.parse_args()
    try:
        summary = validate_manifest(args.manifest)
    except DatasetValidationError as exc:
        print(f"Nastech data validation failed: {exc}")
        return 2
    print(json.dumps(summary.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
