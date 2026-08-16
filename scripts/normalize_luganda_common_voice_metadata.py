from __future__ import annotations

import argparse
import csv
import unicodedata
from pathlib import Path

ALLOWED = set("abcdefgijklmnoprstuvwyzŋ!\"'(),-.:;? ")
REPLACEMENTS = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "—": "-", "…": " ", "`": "'"})


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).translate(REPLACEMENTS).lower()
    text = "".join(ch if ch in ALLOWED else " " for ch in text)
    return " ".join(text.split()).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with (
        args.input.open(encoding="utf-8", newline="") as src,
        args.output.open("w", encoding="utf-8", newline="") as dst,
    ):
        reader = csv.DictReader(src, delimiter="\t")
        writer = csv.DictWriter(dst, fieldnames=reader.fieldnames, delimiter="\t")
        writer.writeheader()
        kept = 0
        removed = 0
        changed = 0
        for row in reader:
            before = row["sentence"]
            row["sentence"] = normalize(before)
            if not row["sentence"]:
                removed += 1
                continue
            if row["sentence"] != before:
                changed += 1
            writer.writerow(row)
            kept += 1
    print(f"kept={kept} removed={removed} changed={changed} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
