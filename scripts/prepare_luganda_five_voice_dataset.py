"""Prepare a five-speaker Luganda Common Voice experiment outside the compact runtime."""

from __future__ import annotations

import argparse
import csv
import subprocess
import tarfile
from collections import Counter, defaultdict
from pathlib import Path

csv.field_size_limit(10_000_000)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--archive-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--clips-per-voice", type=int, default=200)
    return parser.parse_args()


def select_speakers(rows: list[dict[str, str]]) -> list[tuple[str, str, list[dict[str, str]]]]:
    by_client: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_client[row["client_id"]].append(row)
    candidates: dict[str, list[tuple[int, int, str, list[dict[str, str]]]]] = {
        "female_feminine": [],
        "male_masculine": [],
    }
    for client, items in by_client.items():
        counts = Counter((item.get("gender") or "unspecified").lower() for item in items)
        majority, majority_count = counts.most_common(1)[0]
        if majority in candidates and majority_count / len(items) >= 0.8:
            candidates[majority].append((majority_count, len(items), client, items))
    for values in candidates.values():
        values.sort(reverse=True)
    selected: list[tuple[str, str, list[dict[str, str]]]] = []
    for voice_id, gender, rank in (
        ("F1", "female_feminine", 0),
        ("F2", "female_feminine", 1),
        ("F3", "female_feminine", 2),
        ("M1", "male_masculine", 0),
        ("M2", "male_masculine", 1),
    ):
        _, _, client, items = candidates[gender][rank]
        items = sorted(
            items,
            key=lambda item: (
                -int(item.get("up_votes") or 0),
                int(item.get("down_votes") or 0),
                item["path"],
            ),
        )
        selected.append((voice_id, client, items))
    return selected


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with args.metadata.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    selected = select_speakers(rows)
    manifest = args.output_dir / "manifest.tsv"
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["voice_id", "client_id", "gender", "age", "source_path", "transcript"])
        for voice_id, client, items in selected:
            for item in items[: args.clips_per_voice]:
                writer.writerow(
                    [
                        voice_id,
                        client,
                        item.get("gender", ""),
                        item.get("age", ""),
                        item["path"],
                        item["sentence"],
                    ]
                )

    selected_names = {
        Path(item["path"]).name
        for _, _, items in selected
        for item in items[: args.clips_per_voice]
    }
    members: dict[str, tuple[Path, str]] = {}
    for archive in sorted(args.archive_dir.glob("*.tar")):
        with tarfile.open(archive) as handle:
            for member in handle:
                if Path(member.name).name in selected_names:
                    members[Path(member.name).name] = (archive, member.name)
    missing = sorted(selected_names - members.keys())
    if missing:
        raise RuntimeError(
            f"Missing {len(missing)} selected clips from archives; first: {missing[0]}"
        )

    jobs: dict[Path, list[tuple[str, str, str]]] = defaultdict(list)
    for voice_id, _, items in selected:
        for item in items[: args.clips_per_voice]:
            name = Path(item["path"]).name
            archive, member_name = members[name]
            jobs[archive].append((voice_id, name, member_name))
    for archive, archive_jobs in jobs.items():
        with tarfile.open(archive) as handle:
            for voice_id, name, member_name in archive_jobs:
                voice_dir = args.output_dir / voice_id
                voice_dir.mkdir(parents=True, exist_ok=True)
                raw = voice_dir / name
                wav = voice_dir / f"{Path(name).stem}.wav"
                if not raw.exists():
                    extracted = handle.extractfile(member_name)
                    if extracted is None:
                        raise RuntimeError(f"Could not read archive member {member_name}")
                    raw.write_bytes(extracted.read())
                subprocess.run(
                    [
                        "ffmpeg",
                        "-hide_banner",
                        "-loglevel",
                        "error",
                        "-y",
                        "-i",
                        str(raw),
                        "-ac",
                        "1",
                        "-ar",
                        "22050",
                        "-c:a",
                        "pcm_s16le",
                        str(wav),
                    ],
                    check=True,
                )
    print(
        f"Prepared {len(selected) * args.clips_per_voice} clips across F1/F2/F3/M1/M2 "
        f"at {args.output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
