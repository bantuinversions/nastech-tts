"""Build a Coqui Common Voice-compatible layout from the Nastech five-voice subset."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepared", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = args.prepared / "manifest.tsv"
    clips = args.output / "clips"
    clips.mkdir(parents=True, exist_ok=True)
    with manifest.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    with (args.output / "metadata.tsv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["client_id", "path", "sentence", "gender", "age"])
        for row in rows:
            source = args.prepared / row["voice_id"] / f"{Path(row['source_path']).stem}.wav"
            target_name = f"{row['voice_id']}_{source.name}"
            target = clips / target_name
            if not target.exists():
                target.symlink_to(source.resolve())
            writer.writerow(
                [row["voice_id"], target_name, row["transcript"], row["gender"], row["age"]]
            )
    print(f"Built {len(rows)} Common Voice-style records at {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
