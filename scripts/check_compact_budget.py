"""Check whether a Nastech Compact deployment stays within its configured size budget."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def directory_bytes(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(entry.stat().st_size for entry in path.rglob("*") if entry.is_file())


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the Nastech Compact deployment budget.")
    parser.add_argument(
        "--runtime", type=Path, required=True, help="Python virtual environment path."
    )
    parser.add_argument(
        "--model-cache", type=Path, required=True, help="Supertonic model cache path."
    )
    parser.add_argument("--release", type=Path, help="Optional Nastech source/release directory.")
    parser.add_argument(
        "--limit-mib", type=float, default=1024.0, help="Maximum allowed size in MiB."
    )
    args = parser.parse_args()

    parts = {
        "python_runtime": directory_bytes(args.runtime),
        "model_assets": directory_bytes(args.model_cache),
        "release_assets": directory_bytes(args.release) if args.release else 0,
    }
    total = sum(parts.values())
    payload = {
        "limit_mib": args.limit_mib,
        "parts_bytes": parts,
        "parts_mib": {name: round(size / 1024 / 1024, 2) for name, size in parts.items()},
        "total_bytes": total,
        "total_mib": round(total / 1024 / 1024, 2),
        "remaining_mib": round(args.limit_mib - total / 1024 / 1024, 2),
        "passes": total <= args.limit_mib * 1024 * 1024,
    }
    print(json.dumps(payload, indent=2))
    return 0 if payload["passes"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
