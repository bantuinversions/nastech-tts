"""Generate real local WAV fixtures for a Nastech Compact release.

This command is intentionally excluded from deterministic unit tests. It loads
the active local Nastech provider, writes short cleaned WAV fixtures, measures
their digital levels, and records checksums and source markup in a manifest for
tag-only release verification.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from nastech_tts.agent_identity import generate_nastech_story_markup
from nastech_tts.audio_levels import validate_release_wav
from nastech_tts.cleanup import clean_wav
from nastech_tts.providers import require_active_provider
from nastech_tts.supertonic import SupertonicRuntime, compile_nastechml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "release" / "voice_fixtures"


FIXTURES = (
    {
        "id": "nastech-agent-innovation",
        "description": "Nastech Agent innovation story with hopeful narrative delivery.",
        "markup": generate_nastech_story_markup("innovation", sounds=["laugh"]),
    },
    {
        "id": "nastech-agent-resilience",
        "description": "Nastech Agent resilience story with sad narrative delivery and a sigh.",
        "markup": generate_nastech_story_markup("resilience", emotion="sad", sounds=["sigh"]),
    },
    {
        "id": "expressive-laugh-cough",
        "description": "Short direct expressive check for laughter, coughing, anger, and recovery.",
        "markup": (
            '<speak><emotion name="happy" intensity="0.72">We found the signal.'
            '</emotion><sound type="laugh" /><pause ms="350" /><emotion name="angry" '
            'intensity="0.58">The storm will not stop our careful work.</emotion>'
            '<sound type="cough" /><emotion name="calm" intensity="0.55">'
            "We recover, verify, and continue.</emotion></speak>"
        ),
    },
)


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate real local Nastech release voice fixtures."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Directory for WAV files and release-fixtures.json.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing WAV fixtures and manifest.",
    )
    return parser.parse_args()


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    args = _arguments()
    output_dir = args.output_dir.resolve()
    manifest_path = output_dir / "release-fixtures.json"
    if output_dir.exists() and any(output_dir.iterdir()) and not args.overwrite:
        raise FileExistsError(
            f"{output_dir} already contains files; use --overwrite to replace them."
        )
    output_dir.mkdir(parents=True, exist_ok=True)

    provider = require_active_provider("nastech-native-onnx")
    runtime = SupertonicRuntime()
    fixture_rows: list[dict[str, Any]] = []
    for fixture in FIXTURES:
        compiled = compile_nastechml(fixture["markup"], runtime.settings)
        compiled.manifest["provider"] = provider.as_dict()
        compiled.manifest["provider_mixer"] = "nastech"
        audio = runtime.synthesize(compiled, use_cache=False)
        cleaned = clean_wav(audio.data)
        report = validate_release_wav(cleaned.data)
        wav_name = f"{fixture['id']}.wav"
        markup_name = f"{fixture['id']}.xml"
        wav_path = output_dir / wav_name
        markup_path = output_dir / markup_name
        wav_path.write_bytes(cleaned.data)
        markup_path.write_text(fixture["markup"] + "\n", encoding="utf-8")
        fixture_rows.append(
            {
                "id": fixture["id"],
                "description": fixture["description"],
                "wav": wav_name,
                "markup": markup_name,
                "sha256": _sha256(cleaned.data),
                "levels": report.as_dict(),
                "cleanup": cleaned.report,
                "compiler_manifest": compiled.manifest,
            }
        )
        print(f"Generated {wav_path.name}: {report.duration_seconds:.2f}s")

    manifest = {
        "schema_version": "1.0",
        "publisher": "Nastech Research",
        "service": "nastech-tts",
        "provider_mixer": "nastech",
        "provider": provider.as_dict(),
        "inference": "active-local-provider",
        "sample_rate_hz": 44100,
        "fixtures": fixture_rows,
    }
    _write_json(manifest_path, manifest)
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
