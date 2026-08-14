"""Command-line interface for Nastech Compact local Supertonic TTS."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from .cpu import CpuConfigurationError
from .markup import NastechMarkupError
from .supertonic import CompactRuntimeError, SupertonicRuntime, compile_nastechml

VERSION = "0.6.0"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nastech-tts", description="Nastech Compact local expressive CPU TTS."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    compile_command = subparsers.add_parser(
        "compile", help="Compile NastechML into an auditable Supertonic prompt."
    )
    compile_command.add_argument("input", type=Path, help="Input NastechML document.")
    compile_command.add_argument("--output", type=Path, help="Optional JSON output path.")

    validate = subparsers.add_parser(
        "validate", help="Validate English NastechML without loading or synthesizing the model."
    )
    validate.add_argument("input", type=Path, help="Input NastechML document.")
    validate.add_argument("--output", type=Path, help="Optional JSON validation report path.")

    synthesize = subparsers.add_parser(
        "synthesize", help="Generate local WAV audio with Supertonic ONNX."
    )
    synthesize.add_argument("input", type=Path, help="Input NastechML document.")
    synthesize.add_argument("--output", type=Path, required=True, help="WAV destination path.")
    synthesize.add_argument("--manifest", type=Path, help="Optional manifest destination path.")

    subparsers.add_parser("status", help="Show model, CPU policy, cache, and runtime status.")
    subparsers.add_parser(
        "warmup", help="Load ONNX sessions and generate a short local audio warm-up."
    )
    subparsers.add_parser(
        "clear-cache", help="Discard local WAV cache entries without unloading ONNX."
    )
    subparsers.add_parser("agent-tools", help="Print machine-readable agent tool descriptors.")

    benchmark = subparsers.add_parser(
        "benchmark", help="Measure warmed local ONNX synthesis with cache disabled per run."
    )
    benchmark.add_argument("input", type=Path, help="Input NastechML document.")
    benchmark.add_argument(
        "--runs", type=int, default=3, help="Measured runs after warm-up (default: 3)."
    )
    benchmark.add_argument(
        "--no-warmup", action="store_true", help="Include model-load cost in first run."
    )
    benchmark.add_argument(
        "--concurrency", type=int, default=1, help="Parallel requests to schedule (default: 1)."
    )
    benchmark.add_argument("--output", type=Path, help="Optional JSON report destination.")

    serve = subparsers.add_parser("serve", help="Start the local Nastech agent API.")
    serve.add_argument("--host", default="127.0.0.1", help="API bind address.")
    serve.add_argument("--port", type=int, default=8765, help="API bind port.")
    return parser


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _compiled_payload(compiled: Any) -> dict[str, Any]:
    return {
        "request_id": compiled.request_id,
        "runtime": "supertonic-local-onnx-cpu",
        "text": compiled.text,
        "voice": compiled.voice,
        "steps": compiled.steps,
        "speed": compiled.speed,
        "manifest": compiled.manifest,
    }


def _benchmark(
    runtime: SupertonicRuntime,
    markup: str,
    runs: int,
    warmup: bool,
    concurrency: int,
) -> dict[str, Any]:
    if runs < 1 or runs > 100:
        raise ValueError("--runs must be between 1 and 100.")
    if concurrency < 1 or concurrency > 16:
        raise ValueError("--concurrency must be between 1 and 16.")
    warmup_result = runtime.warmup() if warmup else None

    def measure() -> dict[str, float]:
        compiled = compile_nastechml(markup, runtime.settings)
        started = time.perf_counter()
        audio = runtime.synthesize(compiled, use_cache=False)
        elapsed = time.perf_counter() - started
        return {
            "elapsed_seconds": round(elapsed, 4),
            "audio_seconds": round(audio.duration_seconds, 4),
            "real_time_factor": round(elapsed / audio.duration_seconds, 4),
        }

    batch_started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        measurements = list(executor.map(lambda _: measure(), range(runs)))
    wall_clock_seconds = time.perf_counter() - batch_started
    elapsed = [measurement["elapsed_seconds"] for measurement in measurements]
    rtf = [measurement["real_time_factor"] for measurement in measurements]
    return {
        "service": "nastech-tts",
        "version": VERSION,
        "warmup": warmup_result,
        "runs": measurements,
        "summary": {
            "count": len(measurements),
            "requested_concurrency": concurrency,
            "wall_clock_seconds": round(wall_clock_seconds, 4),
            "requests_per_second": round(len(measurements) / wall_clock_seconds, 4),
            "mean_elapsed_seconds": round(statistics.fmean(elapsed), 4),
            "median_elapsed_seconds": round(statistics.median(elapsed), 4),
            "best_elapsed_seconds": round(min(elapsed), 4),
            "mean_real_time_factor": round(statistics.fmean(rtf), 4),
            "cpu": runtime.cpu.as_dict(),
        },
    }


def main() -> int:
    args = _parser().parse_args()
    try:
        runtime = SupertonicRuntime()

        if args.command == "status":
            payload = {"service": "nastech-tts", "version": VERSION, **runtime.status()}
            print(json.dumps(payload, indent=2))
            return 0

        if args.command == "serve":
            import uvicorn

            uvicorn.run("nastech_tts.api:app", host=args.host, port=args.port, reload=False)
            return 0

        if args.command == "warmup":
            print(json.dumps(runtime.warmup(), indent=2))
            return 0

        if args.command == "clear-cache":
            print(json.dumps({"status": "cleared", **runtime.clear_audio_cache()}, indent=2))
            return 0

        if args.command == "agent-tools":
            from .api import agent_tool_descriptors

            print(
                json.dumps(
                    {"tools": [item.model_dump() for item in agent_tool_descriptors()]}, indent=2
                )
            )
            return 0

        markup = args.input.read_text(encoding="utf-8")
        if args.command == "benchmark":
            report = _benchmark(
                runtime,
                markup,
                args.runs,
                warmup=not args.no_warmup,
                concurrency=args.concurrency,
            )
            if args.output:
                _write_json(args.output, report)
                print(args.output)
            else:
                print(json.dumps(report, indent=2))
            return 0

        compiled = compile_nastechml(markup, runtime.settings)
        if args.command == "validate":
            payload = {
                "valid": True,
                "language": "en",
                "span_count": len(compiled.manifest["decisions"]),
                **_compiled_payload(compiled),
            }
            if args.output:
                _write_json(args.output, payload)
                print(args.output)
            else:
                print(json.dumps(payload, indent=2))
            return 0

        if args.command == "compile":
            payload = _compiled_payload(compiled)
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
    except (
        CpuConfigurationError,
        OSError,
        ValueError,
        NastechMarkupError,
        CompactRuntimeError,
    ) as exc:
        print(f"Nastech error: {exc}")
        return 2

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
