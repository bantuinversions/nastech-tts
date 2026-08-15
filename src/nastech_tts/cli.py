"""Command-line interface for Nastech Compact local Supertonic TTS."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from .cleanup import VoiceCleanupError, clean_wav
from .cpu import CpuConfigurationError
from .markup import NastechMarkupError
from .platforms import PlatformPlanError, host_platform_report, platform_preflight
from .supertonic import CompactRuntimeError, SupertonicRuntime, compile_nastechml

VERSION = "0.8.0"


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

    plan = subparsers.add_parser(
        "plan", help="Build an auditable local agent execution plan without generating audio."
    )
    plan.add_argument("input", type=Path, help="Input NastechML document.")
    plan.add_argument("--output", type=Path, help="Optional JSON plan output path.")
    plan.add_argument("--objective", default="Generate an auditable local expressive English WAV.")
    plan.add_argument("--delivery", choices=["wav", "chunked-wav"], default="wav")
    plan.add_argument("--voice", help="Optional local Supertonic voice override.")
    plan.add_argument(
        "--steps", type=int, choices=range(5, 13), help="Optional local step override."
    )
    plan.add_argument("--clean", action="store_true", help="Request local PCM cleanup in the plan.")

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
    synthesize.add_argument(
        "--clean",
        action="store_true",
        help="Apply conservative local PCM WAV cleanup after synthesis.",
    )
    synthesize.add_argument(
        "--clean-report", type=Path, help="Optional JSON cleanup report destination."
    )

    clean = subparsers.add_parser(
        "clean", help="Clean an existing mono 16-bit PCM WAV without a model or cloud service."
    )
    clean.add_argument("input", type=Path, help="Input mono signed-16-bit PCM WAV.")
    clean.add_argument("--output", type=Path, required=True, help="Cleaned WAV destination path.")
    clean.add_argument("--report", type=Path, help="Optional JSON cleanup report destination.")

    subparsers.add_parser("status", help="Show model, CPU policy, cache, and runtime status.")
    subparsers.add_parser(
        "warmup", help="Load ONNX sessions and generate a short local audio warm-up."
    )
    subparsers.add_parser(
        "clear-cache", help="Discard local WAV cache entries without unloading ONNX."
    )
    subparsers.add_parser("agent-tools", help="Print machine-readable agent tool descriptors.")
    subparsers.add_parser("platforms", help="Report local ONNX providers and portability profiles.")
    preflight = subparsers.add_parser(
        "preflight", help="Plan CPU, GPU, Android, iOS, or browser target activation."
    )
    preflight.add_argument(
        "target", help="Platform target, for example python-cuda or android-nnapi."
    )

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


def _print_or_write(payload: dict[str, Any], output: Path | None) -> None:
    if output:
        _write_json(output, payload)
        print(output)
    else:
        print(json.dumps(payload, indent=2))


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

        if args.command == "platforms":
            print(json.dumps(host_platform_report(), indent=2))
            return 0

        if args.command == "preflight":
            print(json.dumps(platform_preflight(args.target), indent=2))
            return 0

        if args.command == "agent-tools":
            from .api import agent_tool_descriptors

            print(
                json.dumps(
                    {"tools": [item.model_dump() for item in agent_tool_descriptors()]}, indent=2
                )
            )
            return 0

        if args.command == "clean":
            cleaned = clean_wav(args.input.read_bytes())
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(cleaned.data)
            report = {"input": str(args.input), "output": str(args.output), **cleaned.report}
            _print_or_write(report, args.report)
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
            _print_or_write(report, args.output)
            return 0

        if args.command == "plan":
            from .api import AgentPlanRequest, _agent_plan, _compiled

            request = AgentPlanRequest(
                markup=markup,
                voice=args.voice,
                steps=args.steps,
                cleanup=args.clean,
                objective=args.objective,
                delivery=args.delivery,
            )
            _print_or_write(_agent_plan(request, _compiled(request, runtime)), args.output)
            return 0

        compiled = compile_nastechml(markup, runtime.settings)
        if args.command == "validate":
            payload = {
                "valid": True,
                "language": "en",
                "span_count": len(compiled.manifest["decisions"]),
                **_compiled_payload(compiled),
            }
            _print_or_write(payload, args.output)
            return 0

        if args.command == "compile":
            _print_or_write(_compiled_payload(compiled), args.output)
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
            if args.clean:
                cleaned = clean_wav(audio.data)
                args.output.write_bytes(cleaned.data)
                report_path = args.clean_report or args.output.with_suffix(
                    args.output.suffix + ".cleanup.json"
                )
                _write_json(report_path, cleaned.report)
                print(f"Cleanup report: {report_path}")
            return 0
    except (
        CpuConfigurationError,
        OSError,
        ValueError,
        NastechMarkupError,
        CompactRuntimeError,
        VoiceCleanupError,
        PlatformPlanError,
    ) as exc:
        print(f"Nastech error: {exc}")
        return 2

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
