"""Build the code-first language data consumed by the Nastech Research Pages site."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "release" / "nastech-bantu-language-voice-registry.json"
OUTPUT = ROOT / "site" / "assets" / "languages.json"

REGIONS = {
    "en": "Global",
    "lg": "East Africa",
    "nyn": "East Africa",
    "ach": "East Africa",
    "teo": "East Africa",
    "sw": "East Africa",
    "rw": "Great Lakes",
    "rn": "Great Lakes",
    "ki": "East Africa",
    "bem": "Southern Africa",
    "sn": "Southern Africa",
    "ny": "Southern Africa",
}


def main() -> int:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = []
    for item in source:
        code = item["language"]
        rows.append(
            {
                "code": code,
                "label": item["label"],
                "display_label": item["display_label"],
                "iso639_3": item["iso639_3"],
                "region": REGIONS.get(code, "East, Central, or Southern Africa"),
                "state": item["registry_status"],
                "pack_state": item["pack_state"],
                "story_available": item["story_available"],
            }
        )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps({"languages": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": "passed", "output": str(OUTPUT), "language_count": len(rows)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
