"""Render the validated Nastech English and Bantu voice inventories as Markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--english", type=Path, required=True)
    parser.add_argument("--bantu", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tests", type=int, required=True)
    parser.add_argument("--budget-mib", type=float, required=True)
    return parser.parse_args()


def main() -> int:
    args = _args()
    english = json.loads(args.english.read_text(encoding="utf-8"))
    bantu = json.loads(args.bantu.read_text(encoding="utf-8"))
    summary = english["summary"]
    lines = [
        "# Nastech TTS Voice Inventory",
        "",
        "This inventory was generated after local deterministic verification. English has "
        f"**{summary['selectable_profiles']} selectable local profiles** over "
        f"**{summary['verified_base_timbres']} verified Supertonic base timbres**. The "
        "delivery profiles are not represented as separately trained speaker identities.",
        "",
        "| Local verification | Result |",
        "|---|---:|",
        f"| Deterministic tests | {args.tests} passed |",
        f"| Compact core budget | {args.budget_mib:.2f} MiB |",
        f"| Bantu registry targets | {len(bantu)} |",
        "| Verified Bantu story routes | "
        f"{sum(1 for row in bantu if row['story_available']) - 1} |",
        "",
        "## English named profiles and delivery styles",
        "",
        "| Selector | Display name | Base timbre | Kind | Default speed | Description |",
        "|---|---|---|---|---:|---|",
    ]
    for profile in english["profiles"]:
        lines.append(
            (
                "| {profile_id} | {label} | {base_voice} | {kind} | "
                "{default_speed:.2f} | {description} |"
            ).format(**profile)
        )
    lines.extend(
        [
            "",
            "## Bantu language registry",
            "",
            "| Selection label | Registry state | Model-pack state | "
            "Verified local model | Native story test |",
            "|---|---|---|---|---|",
        ]
    )
    for row in bantu:
        lines.append(
            ("| {display_label} | {registry_status} | {pack_state} | {model} | {story} |").format(
                display_label=f"{row['language']} - {row['label']}",
                registry_status=row["registry_status"],
                pack_state=row["pack_state"],
                model=row["model_id"] or "No verified pack",
                story="Yes" if row["story_available"] else "No",
            )
        )
    lines.extend(
        [
            "",
            "> **Evidence boundary:** A `lazy-downloadable` MMS route is a local technical "
            "route, not a verified naturalness or pure-language claim. Five-minute native-story CI "
            "is only retained where an approved story fixture exists. Every other regional target "
            "remains `planned` or `no-verified-pack` until an exact checkpoint and native-language "
            "review are available; Nastech never substitutes a different language.",
            "",
        ]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
