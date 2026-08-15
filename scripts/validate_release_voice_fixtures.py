"""Validate Nastech release voice fixtures without loading the TTS model."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from nastech_tts.audio_levels import validate_release_wav

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE_DIR = ROOT / "release" / "voice_fixtures"


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Nastech release voice WAV fixtures.")
    parser.add_argument(
        "--fixture-dir",
        type=Path,
        default=DEFAULT_FIXTURE_DIR,
        help="Directory containing release-fixtures.json and generated WAVs.",
    )
    parser.add_argument("--report", type=Path, help="Optional JSON verification report path.")
    return parser.parse_args()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_manifest(path: Path) -> dict[str, Any]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Unable to read fixture manifest: {exc}") from exc
    if manifest.get("schema_version") != "1.0":
        raise ValueError("Fixture manifest has an unsupported schema version.")
    if manifest.get("publisher") != "Nastech Research":
        raise ValueError("Fixture manifest publisher must be Nastech Research.")
    if manifest.get("provider_mixer") != "nastech":
        raise ValueError("Fixture manifest must identify the Nastech provider mixer.")
    provider = manifest.get("provider", {})
    if provider.get("id") != "nastech-native-onnx":
        raise ValueError("Fixture manifest must identify the verified local Nastech provider.")
    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list) or len(fixtures) < 3:
        raise ValueError("Fixture manifest must declare at least three release WAVs.")
    return manifest


def main() -> int:
    args = _arguments()
    fixture_dir = args.fixture_dir.resolve()
    manifest = _load_manifest(fixture_dir / "release-fixtures.json")
    results: list[dict[str, Any]] = []
    for fixture in manifest["fixtures"]:
        wav_name = fixture.get("wav")
        if not isinstance(wav_name, str) or Path(wav_name).name != wav_name:
            raise ValueError("Fixture WAV name must be a simple relative filename.")
        wav_path = fixture_dir / wav_name
        data = wav_path.read_bytes()
        if fixture.get("sha256") != _sha256(data):
            raise ValueError(f"Fixture checksum mismatch: {wav_name}")
        report = validate_release_wav(data)
        expected = fixture.get("levels", {})
        if expected.get("sample_rate_hz") != report.sample_rate_hz:
            raise ValueError(f"Fixture sample-rate manifest mismatch: {wav_name}")
        results.append({"id": fixture.get("id"), "wav": wav_name, "levels": report.as_dict()})

    verification = {
        "status": "passed",
        "publisher": "Nastech Research",
        "fixture_count": len(results),
        "fixtures": results,
    }
    rendered = json.dumps(verification, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
