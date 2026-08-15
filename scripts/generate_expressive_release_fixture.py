"""Generate and validate the documented real local expressive Nastech fixture."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from nastech_tts.audio_levels import validate_release_wav
from nastech_tts.cleanup import clean_wav
from nastech_tts.supertonic import SupertonicRuntime, compile_nastechml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "release" / "multilingual_fixtures" / "nastech-expressive-audition.xml"
DEFAULT_OUTPUT = ROOT / "release" / "multilingual_fixtures"


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate an expressive Nastech release fixture.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = _arguments()
    markup = args.source.read_text(encoding="utf-8")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / "nastech-expressive-audition.wav"
    manifest_path = args.output_dir / "nastech-expressive-audition.manifest.json"
    levels_path = args.output_dir / "nastech-expressive-audition.levels.json"
    if not args.overwrite and any(path.exists() for path in (output, manifest_path, levels_path)):
        raise FileExistsError("Expressive fixture exists; pass --overwrite to replace it.")

    runtime = SupertonicRuntime()
    compiled = compile_nastechml(markup, runtime.settings, language="en")
    audio = runtime.synthesize(compiled, use_cache=False)
    cleaned = clean_wav(audio.data)
    report = validate_release_wav(cleaned.data, maximum_duration_seconds=90.0)
    output.write_bytes(cleaned.data)
    _write_json(manifest_path, compiled.manifest)
    _write_json(
        levels_path,
        {
            "processor": cleaned.report["processor"],
            "cleanup": cleaned.report,
            "level_report": report.as_dict(),
            "source": str(args.source.relative_to(ROOT)),
            "output": str(output.relative_to(ROOT)),
        },
    )
    print(json.dumps({"output": str(output), "levels": report.as_dict()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
