"""Command-line interface for Nastech Compact local Supertonic TTS."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .markup import NastechMarkupError
from .supertonic import CompactRuntimeError, SupertonicRuntime, compile_nastechml


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nastech-tts", description="Nastech Compact local expressive TTS."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    compile_command = subparsers.add_parser(
        "compile", help="Compile NastechML into an auditable Supertonic prompt."
    )
    compile_command.add_argument("input", type=Path, help="Input NastechML document.")
    compile_command.add_argument("--output", type=Path, help="Optional JSON output path.")

    synthesize = subparsers.add_parser(
        "synthesize", help="Generate local WAV audio with Supertonic ONNX."
    )
    synthesize.add_argument("input", type=Path, help="Input NastechML document.")
    synthesize.add_argument("--output", type=Path, required=True, help="WAV destination path.")
    synthesize.add_argument("--manifest", type=Path, help="Optional manifest destination path.")

    subparsers.add_parser("status", help="Show local model cache, runtime, and budget status.")
    subparsers.add_parser("agent-tools", help="Print machine-readable agent tool descriptors.")

    serve = subparsers.add_parser("serve", help="Start the local Nastech agent API.")
    serve.add_argument("--host", default="127.0.0.1", help="API bind address.")
    serve.add_argument("--port", type=int, default=8765, help="API bind port.")
    return parser


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = _parser().parse_args()
    runtime = SupertonicRuntime()

    if args.command == "status":
        print(
            json.dumps({"service": "nastech-tts", "version": "0.4.0", **runtime.status()}, indent=2)
        )
        return 0

    if args.command == "serve":
        import uvicorn

        uvicorn.run("nastech_tts.api:app", host=args.host, port=args.port, reload=False)
        return 0

    if args.command == "agent-tools":
        from .api import AgentCompileRequest, AgentSpeechRequest

        print(
            json.dumps(
                {
                    "tools": [
                        {
                            "name": "nastech_compile_speech",
                            "input_schema": AgentCompileRequest.model_json_schema(),
                        },
                        {
                            "name": "nastech_generate_speech",
                            "input_schema": AgentSpeechRequest.model_json_schema(),
                        },
                    ]
                },
                indent=2,
            )
        )
        return 0

    try:
        markup = args.input.read_text(encoding="utf-8")
        compiled = compile_nastechml(markup, runtime.settings)
        if args.command == "compile":
            payload = {
                "request_id": compiled.request_id,
                "runtime": "supertonic-local",
                "text": compiled.text,
                "voice": compiled.voice,
                "steps": compiled.steps,
                "speed": compiled.speed,
                "manifest": compiled.manifest,
            }
            if args.output:
                _write_json(args.output, payload)
                print(args.output)
            else:
                print(json.dumps(payload, indent=2))
            return 0

        if args.command == "synthesize":
            audio = runtime.synthesize(compiled)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(audio.data)
            manifest_path = args.manifest or args.output.with_suffix(
                args.output.suffix + ".manifest.json"
            )
            _write_json(manifest_path, compiled.manifest)
            print(f"Audio: {args.output}")
            print(f"Manifest: {manifest_path}")
            print(f"Duration: {audio.duration_seconds:.2f}s")
            return 0
    except (OSError, ValueError, NastechMarkupError, CompactRuntimeError) as exc:
        print(f"Nastech error: {exc}")
        return 2

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
