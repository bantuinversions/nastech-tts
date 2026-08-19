"""Validate Nastech's committed Bantu language inventory against the live registry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from nastech_tts.languages import LANGUAGE_REGISTRY, MMS_LAZY_CODES

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_STORY_LANGUAGES = {
    "en",
    "lg",
    "nyn",
    "ach",
    "teo",
    "sw",
    "rw",
    "rn",
    "ki",
    "ts",
    "sn",
    "ny",
}


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--matrix",
        type=Path,
        default=ROOT / "release" / "nastech-bantu-language-voice-registry.json",
        help="JSON matrix created by test_all_registered_voices.py --list-json.",
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=ROOT / "release" / "Nastech_TTS_All_Voices.md",
        help="Committed human-readable all-voices inventory.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Optional JSON result report for CI artifact collection.",
    )
    return parser.parse_args()


def validate(matrix: list[dict[str, Any]], inventory: str) -> dict[str, int]:
    """Return audited counts or raise ValueError when generated evidence is stale."""

    by_language = {str(row["language"]): row for row in matrix}
    if len(by_language) != len(matrix):
        raise ValueError("Language self-test matrix contains duplicate language codes.")
    if set(by_language) != set(LANGUAGE_REGISTRY):
        missing = sorted(set(LANGUAGE_REGISTRY) - set(by_language))
        unexpected = sorted(set(by_language) - set(LANGUAGE_REGISTRY))
        raise ValueError(
            f"Language self-test matrix mismatch; missing={missing}, unexpected={unexpected}."
        )
    for code, definition in LANGUAGE_REGISTRY.items():
        row = by_language[code]
        expected_display = definition.display_label
        if row.get("display_label") != expected_display:
            raise ValueError(f"Language '{code}' display label is not '{expected_display}'.")
        if not expected_display.startswith(f"{code} - "):
            raise ValueError(f"Language '{code}' does not use the code-first label convention.")
        has_model = row.get("model_id") is not None
        if has_model != (code in MMS_LAZY_CODES):
            raise ValueError(f"Language '{code}' has an inconsistent lazy-pack route.")
        if code in MMS_LAZY_CODES and row.get("pack_state") != "lazy-downloadable":
            raise ValueError(f"Language '{code}' should be lazy-downloadable.")
        if code not in MMS_LAZY_CODES and row.get("pack_state") != "no-verified-pack":
            raise ValueError(f"Language '{code}' should have no verified pack.")
        if expected_display not in inventory:
            raise ValueError(f"Committed all-voices inventory is missing '{expected_display}'.")

    story_languages = {code for code, row in by_language.items() if row.get("story_available")}
    if story_languages != EXPECTED_STORY_LANGUAGES:
        raise ValueError(f"Story suite mismatch: expected {sorted(EXPECTED_STORY_LANGUAGES)}.")
    expected_registry_line = f"| Bantu registry targets | {len(matrix)} |"
    expected_story_line = f"| Verified Bantu story routes | {len(story_languages) - 1} |"
    if expected_registry_line not in inventory or expected_story_line not in inventory:
        raise ValueError("Committed all-voices inventory has stale summary counts.")
    return {
        "registry_targets": len(matrix),
        "lazy_download_routes": len(MMS_LAZY_CODES),
        "native_story_routes": len(story_languages) - 1,
    }


def main() -> int:
    args = _args()
    matrix = json.loads(args.matrix.read_text(encoding="utf-8"))
    summary = validate(matrix, args.inventory.read_text(encoding="utf-8"))
    result = {"status": "passed", "publisher": "Nastech Research"} | summary
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
