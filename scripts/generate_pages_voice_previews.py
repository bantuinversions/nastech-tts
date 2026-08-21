"""Render verified local English voice previews for the Nastech Research Pages site.

The generated WAVs are deployment assets, not core runtime files. Each preview is
produced with the local Nastech ONNX runtime and receives a deterministic WAV
quality report before it is included in the published catalog.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from nastech_tts.audio_levels import validate_release_wav  # noqa: E402
from nastech_tts.supertonic import SupertonicRuntime, compile_nastechml  # noqa: E402
from nastech_tts.voices import english_voice_inventory  # noqa: E402

DEFAULT_OUTPUT_DIR = ROOT / "site" / "assets" / "voice-previews"
DEFAULT_CATALOG = ROOT / "site" / "assets" / "voice-previews.json"
PREVIEW_TEXT = "Welcome to Nastech Research. This is a verified local voice preview."


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument(
        "--limit", type=int, help="Render only the first N profiles for local checks."
    )
    parser.add_argument(
        "--force", action="store_true", help="Re-render previews that already exist."
    )
    return parser.parse_args()


def _record(profile: dict[str, Any], wav_name: str, quality: dict[str, Any]) -> dict[str, Any]:
    return {
        "profile_id": profile["profile_id"],
        "label": profile["label"],
        "base_voice": profile["base_voice"],
        "kind": profile["kind"],
        "default_speed": profile["default_speed"],
        "description": profile["description"],
        "preview": f"assets/voice-previews/{wav_name}",
        "quality": quality,
        "status": "verified-local-preview",
    }


def main() -> int:
    args = _args()
    profiles = english_voice_inventory()
    if args.limit is not None:
        if args.limit < 1:
            raise ValueError("--limit must be at least 1.")
        profiles = profiles[: args.limit]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    runtime = SupertonicRuntime()
    rows: list[dict[str, Any]] = []
    for profile in profiles:
        wav_name = f"{profile['profile_id']}.wav"
        destination = args.output_dir / wav_name
        if not destination.exists() or args.force:
            markup = f'<speak voice="{profile["profile_id"]}">{PREVIEW_TEXT}</speak>'
            compiled = compile_nastechml(markup, runtime.settings)
            destination.write_bytes(runtime.synthesize(compiled, use_cache=False).data)
        quality = validate_release_wav(destination.read_bytes()).as_dict()
        if quality["clipped_samples"] != 0:
            raise RuntimeError(f"Preview contains clipping: {destination}")
        rows.append(_record(profile, wav_name, quality))

    catalog = {
        "schema_version": "1.0",
        "publisher": "Nastech Research",
        "title": "Nastech TTS verified local voice previews",
        "preview_text": PREVIEW_TEXT,
        "voice_count": len(rows),
        "voices": rows,
        "boundary": (
            "These previews cover the forty verified local English profiles. Bantu packs remain "
            "on-demand and are listed separately to avoid publishing a voice sample for a pack "
            "that is not installed or human-reviewed."
        ),
    }
    args.catalog.parent.mkdir(parents=True, exist_ok=True)
    args.catalog.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "catalog": str(args.catalog), "voice_count": len(rows)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
