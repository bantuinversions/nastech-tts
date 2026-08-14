"""Command-line interface for the single-model Nastech TTS product."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .evaluation import run_behavior_suite
from .service import NastechRenderError, NastechService
from .training import DatasetValidationError, validate_manifest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nastech-tts", description="Nastech English expressive TTS.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    render = subparsers.add_parser("render", help="Render a NastechML file to a WAV file.")
    render.add_argument("input", type=Path, help="Path to an input .xml NastechML document.")
    render.add_argument("--output", type=Path, required=True, help="Destination WAV path.")

    subparsers.add_parser("status", help="Show selected model and local runtime availability.")
    subparsers.add_parser("model", help="Show full selected-model provenance and capability metadata.")

    validate = subparsers.add_parser("validate-data", help="Validate a licensed Nastech training manifest.")
    validate.add_argument("manifest", type=Path, help="JSONL manifest to validate.")

    evaluate = subparsers.add_parser("evaluate", help="Run a Nastech behavior-fidelity suite.")
    evaluate.add_argument("suite", type=Path, help="JSON behavior-suite fixture.")

    serve = subparsers.add_parser("serve", help="Start the local Nastech HTTP API.")
    serve.add_argument("--host", default="127.0.0.1", help="API bind address.")
    serve.add_argument("--port", type=int, default=8765, help="API bind port.")
    return parser


def main() -> int:
    args = _parser().parse_args()
    service = NastechService()

    if args.command == "status":
        print(json.dumps(service.engine_status(), indent=2))
        return 0

    if args.command == "model":
        print(json.dumps(service.model.to_dict(), indent=2))
        return 0

    if args.command == "validate-data":
        try:
            summary = validate_manifest(args.manifest)
        except DatasetValidationError as exc:
            print(f"Nastech data validation failed: {exc}")
            return 2
        print(json.dumps(summary.to_dict(), indent=2))
        return 0

    if args.command == "evaluate":
        results = run_behavior_suite(args.suite)
        payload = {
            "total": len(results),
            "passed": sum(result.passed for result in results),
            "failed": sum(not result.passed for result in results),
            "results": [asdict(result) for result in results],
        }
        print(json.dumps(payload, indent=2))
        return 0 if payload["failed"] == 0 else 2

    if args.command == "serve":
        try:
            import uvicorn

            from .api import create_app
        except ImportError:
            print("Nastech API dependencies are missing. Install the project with the [api] extra.")
            return 2
        uvicorn.run(create_app(service), host=args.host, port=args.port)
        return 0

    if args.command == "render":
        try:
            markup = args.input.read_text(encoding="utf-8")
            result = service.render(markup, args.output)
        except (OSError, ValueError, NastechRenderError) as exc:
            print(f"Nastech TTS error: {exc}")
            return 2
        print(f"Audio: {result.audio_path}")
        print(f"Manifest: {result.manifest_path}")
        if result.manifest.warnings:
            print("Warnings:")
            for warning in result.manifest.warnings:
                print(f"- {warning}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
