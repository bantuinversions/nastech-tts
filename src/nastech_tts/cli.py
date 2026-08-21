"""Command-line interface for Nastech TTS and Nastech Voice Core."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from .agent_identity import (
    agent_identity,
    generate_nastech_story_markup,
    supported_story_emotions,
    supported_story_sounds,
    supported_story_themes,
)
from .agent_response import (
    AgentExpressionError,
    agent_expression_capabilities,
    agent_markup,
)
from .cleanup import VoiceCleanupError, clean_wav
from .cpu import CpuConfigurationError
from .languages import get_language, language_inventory
from .lazy_packs import download_language_pack, pack_inventory
from .markup import NastechMarkupError
from .platforms import PlatformPlanError, host_platform_report, platform_preflight
from .providers import (
    ProviderActivationError,
    provider_inventory,
    provider_preflight,
    synthesize_with_provider,
)
from .supertonic import CompactRuntimeError, SupertonicRuntime, compile_nastechml
from .vocal_events import (
    VocalEventError,
    render_vocal_event,
    supported_event_sounds,
)
from .vocal_events import (
    pack_status as vocal_events_pack_status,
)
from .voices import english_voice_inventory, english_voice_summary

VERSION = "0.12.2"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nastech-tts", description="Nastech TTS local expressive speech platform."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    compile_command = subparsers.add_parser(
        "compile", help="Compile NastechML for an active Nastech provider."
    )
    compile_command.add_argument("input", type=Path, help="Input NastechML document.")
    compile_command.add_argument("--output", type=Path, help="Optional JSON output path.")
    compile_command.add_argument("--provider", help="Nastech provider ID (default: active local).")
    compile_command.add_argument(
        "--language", default="en", help="Nastech language code (default: en)."
    )

    plan = subparsers.add_parser(
        "plan", help="Build an auditable local agent execution plan without generating audio."
    )
    plan.add_argument("input", type=Path, help="Input NastechML document.")
    plan.add_argument("--output", type=Path, help="Optional JSON plan output path.")
    plan.add_argument("--objective", default="Generate an auditable local expressive English WAV.")
    plan.add_argument("--delivery", choices=["wav", "chunked-wav"], default="wav")
    plan.add_argument("--voice", help="Optional active-provider voice override.")
    plan.add_argument("--provider", help="Nastech provider ID (default: active local).")
    plan.add_argument("--language", default="en", help="Nastech language code (default: en).")
    plan.add_argument(
        "--steps", type=int, choices=range(5, 13), help="Optional local step override."
    )
    plan.add_argument("--clean", action="store_true", help="Request local PCM cleanup in the plan.")

    story = subparsers.add_parser(
        "story", help="Compose a Nastech Agent English story and optionally synthesize it locally."
    )
    story.add_argument(
        "theme",
        nargs="?",
        choices=supported_story_themes(),
        default="innovation",
        help="Story theme (default: innovation).",
    )
    story.add_argument(
        "--emotion",
        choices=supported_story_emotions(),
        default="hopeful",
        help="Nastech Agent narrative emotion (default: hopeful).",
    )
    story.add_argument(
        "--sound",
        dest="sounds",
        action="append",
        choices=supported_story_sounds(),
        default=[],
        help="Optional expressive sound cue; may be provided up to three times.",
    )
    story.add_argument("--voice", help="Optional active-provider voice override.")
    story.add_argument("--provider", help="Nastech provider ID (default: active local).")
    story.add_argument(
        "--steps", type=int, choices=range(5, 13), help="Optional local step override."
    )
    story.add_argument("--markup-output", type=Path, help="Optional NastechML output path.")
    story.add_argument("--output", type=Path, help="Optional local WAV output path.")
    story.add_argument("--manifest", type=Path, help="Optional manifest path when rendering audio.")
    story.add_argument("--clean", action="store_true", help="Clean rendered WAV audio locally.")
    story.add_argument("--report", type=Path, help="Optional JSON story report path.")

    validate = subparsers.add_parser(
        "validate", help="Validate English NastechML without loading or synthesizing the model."
    )
    validate.add_argument("input", type=Path, help="Input NastechML document.")
    validate.add_argument("--output", type=Path, help="Optional JSON validation report path.")
    validate.add_argument("--language", default="en", help="Nastech language code (default: en).")

    synthesize = subparsers.add_parser(
        "synthesize", help="Generate local WAV audio through an active Nastech provider."
    )
    synthesize.add_argument("input", type=Path, help="Input NastechML document.")
    synthesize.add_argument("--output", type=Path, required=True, help="WAV destination path.")
    synthesize.add_argument("--manifest", type=Path, help="Optional manifest destination path.")
    synthesize.add_argument("--provider", help="Nastech provider ID (default: active local).")
    synthesize.add_argument("--language", default="en", help="Nastech language code (default: en).")
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

    subparsers.add_parser(
        "vocal-events",
        help="Inspect the optional local Nastech Vocal Events Pack without loading it.",
    )
    vocal_event = subparsers.add_parser(
        "vocal-event",
        help="Render one native local vocal event through the optional Nastech Vocal Events Pack.",
    )
    vocal_event.add_argument("sound", choices=supported_event_sounds(), help="Nastech sound cue.")
    vocal_event.add_argument(
        "--reference-audio",
        type=Path,
        required=True,
        help="Authorized 10+ second WAV reference for local event voice conditioning.",
    )
    vocal_event.add_argument(
        "--confirm-reference-authorized",
        action="store_true",
        help="Required confirmation that you have authorization to use the reference voice.",
    )
    vocal_event.add_argument(
        "--output", type=Path, required=True, help="Native-event WAV destination."
    )
    vocal_event.add_argument(
        "--manifest", type=Path, help="Optional native-event manifest destination."
    )
    vocal_event.add_argument("--report", type=Path, help="Optional JSON event report destination.")
    vocal_event.add_argument(
        "--clean", action="store_true", help="Apply conservative local WAV cleanup."
    )

    subparsers.add_parser("status", help="Show model, CPU policy, cache, and runtime status.")
    subparsers.add_parser(
        "warmup", help="Load ONNX sessions and generate a short local audio warm-up."
    )
    subparsers.add_parser(
        "clear-cache", help="Discard local WAV cache entries without unloading ONNX."
    )
    subparsers.add_parser("agent-tools", help="Print machine-readable agent tool descriptors.")
    subparsers.add_parser(
        "agent-capabilities",
        help="Print the local AI-agent voice, emotion, sound, and response contract as JSON.",
    )
    agent_markup = subparsers.add_parser(
        "agent-markup",
        help="Resolve natural-language emotion and sound labels into auditable NastechML JSON.",
    )
    agent_markup.add_argument("text", help="Text for the proposed local voice response.")
    agent_markup.add_argument("--voice", default="siya", help="Voice profile (default: siya).")
    agent_markup.add_argument(
        "--emotion", default="neutral", help="Core emotion or supported alias."
    )
    agent_markup.add_argument("--intensity", type=float, help="Emotion intensity from 0 to 1.")
    agent_markup.add_argument("--rate", help="Optional rate override: slow, normal, or fast.")
    agent_markup.add_argument("--volume", help="Optional volume override: soft, normal, or loud.")
    agent_markup.add_argument(
        "--sound",
        dest="sounds",
        action="append",
        default=[],
        help="Sound cue or alias; may be used multiple times.",
    )
    agent_markup.add_argument("--output", type=Path, help="Optional JSON response report path.")
    agent_speak = subparsers.add_parser(
        "agent-speak",
        help="Generate one auditable local AI voice-response WAV and structured JSON result.",
    )
    agent_speak.add_argument("text", help="Text for the local voice response.")
    agent_speak.add_argument("--output", type=Path, required=True, help="Destination WAV path.")
    agent_speak.add_argument(
        "--manifest", type=Path, help="Optional compiled-manifest destination."
    )
    agent_speak.add_argument(
        "--report", type=Path, help="Optional structured JSON response report path."
    )
    agent_speak.add_argument("--voice", default="siya", help="Voice profile (default: siya).")
    agent_speak.add_argument(
        "--language", default="en", help="Registered language code (default: en)."
    )
    agent_speak.add_argument("--provider", help="Optional provider ID override.")
    agent_speak.add_argument(
        "--emotion", default="neutral", help="Core emotion or supported alias."
    )
    agent_speak.add_argument("--intensity", type=float, help="Emotion intensity from 0 to 1.")
    agent_speak.add_argument("--rate", help="Optional rate override: slow, normal, or fast.")
    agent_speak.add_argument("--volume", help="Optional volume override: soft, normal, or loud.")
    agent_speak.add_argument(
        "--sound",
        dest="sounds",
        action="append",
        default=[],
        help="Sound cue or alias; may be used multiple times.",
    )
    agent_speak.add_argument(
        "--clean", action="store_true", help="Apply conservative local WAV cleanup."
    )
    subparsers.add_parser(
        "mcp-server", help="Run the local Nastech TTS MCP bridge over standard input/output."
    )
    subparsers.add_parser("providers", help="List all Nastech provider-mixer targets.")
    subparsers.add_parser("languages", help="List Bantu-language targets and evidence states.")
    subparsers.add_parser(
        "voices", help="List forty English local voice profiles and their verified base timbres."
    )
    subparsers.add_parser("language-packs", help="List lazy Bantu model-pack cache states.")
    download_pack = subparsers.add_parser(
        "download-language-pack", help="Download exactly one requested Bantu language pack."
    )
    download_pack.add_argument("language", help="Language code, for example sw or zu.")
    language_check = subparsers.add_parser(
        "language-preflight", help="Inspect language provider requirements without side effects."
    )
    language_check.add_argument("language", help="Nastech language code, for example lg or zu.")
    provider_check = subparsers.add_parser(
        "provider-preflight", help="Inspect a provider activation plan without side effects."
    )
    provider_check.add_argument("provider_id", help="Nastech provider ID, for example coqui-cli.")
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
        "runtime": "nastech-provider-mixer",
        "provider": compiled.manifest.get("provider"),
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
    if args.command == "mcp-server":
        from .agent_bridge import run_stdio

        return run_stdio()
    try:
        runtime = SupertonicRuntime()

        if args.command == "vocal-events":
            print(json.dumps(vocal_events_pack_status(), indent=2))
            return 0

        if args.command == "vocal-event":
            if not args.confirm_reference_authorized:
                raise VocalEventError(
                    "--confirm-reference-authorized is required before using a voice reference."
                )
            data, manifest = render_vocal_event(args.sound, args.reference_audio)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(data)
            if args.clean:
                cleaned = clean_wav(data)
                args.output.write_bytes(cleaned.data)
                manifest["cleanup"] = cleaned.report
            manifest_path = args.manifest or args.output.with_suffix(
                args.output.suffix + ".manifest.json"
            )
            _write_json(manifest_path, manifest)
            _print_or_write(
                {
                    "service": "nastech-tts",
                    "kind": "native_local_vocal_event",
                    "output_audio": str(args.output),
                    "output_manifest": str(manifest_path),
                    "sound": args.sound,
                    "render_route": manifest["render_route"],
                    "local_only": True,
                },
                args.report,
            )
            return 0

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

        if args.command == "providers":
            print(json.dumps(provider_inventory(), indent=2))
            return 0

        if args.command == "languages":
            print(json.dumps(language_inventory(), indent=2))
            return 0

        if args.command == "voices":
            print(
                json.dumps(
                    {
                        "language": "en",
                        "summary": english_voice_summary(),
                        "profiles": english_voice_inventory(),
                    },
                    indent=2,
                )
            )
            return 0

        if args.command == "language-packs":
            print(json.dumps(pack_inventory(), indent=2))
            return 0

        if args.command == "download-language-pack":
            print(json.dumps(download_language_pack(args.language), indent=2))
            return 0

        if args.command == "language-preflight":
            language = get_language(args.language)
            payload = {
                "language": language.as_dict(),
                "provider_preflights": [
                    provider_preflight(provider_id) for provider_id in language.provider_ids
                ],
                "network_request_made": False,
            }
            print(json.dumps(payload, indent=2))
            return 0

        if args.command == "provider-preflight":
            print(json.dumps(provider_preflight(args.provider_id), indent=2))
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

        if args.command == "agent-capabilities":
            print(
                json.dumps(
                    {
                        "service": "nastech-tts",
                        "version": VERSION,
                        "agent_expression": agent_expression_capabilities(),
                        "voices": english_voice_summary(),
                        "languages": language_inventory(),
                    },
                    indent=2,
                )
            )
            return 0

        if args.command == "agent-markup":
            markup, expression = agent_markup(
                args.text,
                voice=args.voice,
                emotion=args.emotion,
                intensity=args.intensity,
                rate=args.rate,
                volume=args.volume,
                sounds=args.sounds,
            )
            _print_or_write(
                {
                    "service": "nastech-tts",
                    "version": VERSION,
                    "kind": "agent_voice_response_plan",
                    "local_only": True,
                    "markup": markup,
                    "expression": expression,
                },
                args.output,
            )
            return 0

        if args.command == "agent-speak":
            markup, expression = agent_markup(
                args.text,
                voice=args.voice,
                emotion=args.emotion,
                intensity=args.intensity,
                rate=args.rate,
                volume=args.volume,
                sounds=args.sounds,
            )
            from .api import AgentCompileRequest, _compiled

            compiled = _compiled(
                AgentCompileRequest(
                    markup=markup,
                    voice=args.voice,
                    provider_id=args.provider,
                    language=args.language,
                ),
                runtime,
            )
            audio = synthesize_with_provider(
                args.provider,
                runtime,
                compiled,
                language=compiled.manifest["language"],
            )
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(audio.data)
            manifest_path = args.manifest or args.output.with_suffix(
                args.output.suffix + ".manifest.json"
            )
            _write_json(manifest_path, compiled.manifest)
            response: dict[str, Any] = {
                "service": "nastech-tts",
                "version": VERSION,
                "kind": "agent_voice_response",
                "local_only": True,
                "output_audio": str(args.output),
                "output_manifest": str(manifest_path),
                "mime_type": "audio/wav",
                "duration_seconds": round(audio.duration_seconds, 4),
                "language": compiled.manifest["language"],
                "provider": compiled.manifest["provider"],
                "expression": expression,
                "next_action": "play_or_attach_local_wav",
            }
            if args.clean:
                cleaned = clean_wav(audio.data)
                args.output.write_bytes(cleaned.data)
                response["cleanup"] = cleaned.report
            _print_or_write(response, args.report)
            return 0

        if args.command == "clean":
            cleaned = clean_wav(args.input.read_bytes())
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(cleaned.data)
            report = {"input": str(args.input), "output": str(args.output), **cleaned.report}
            _print_or_write(report, args.report)
            return 0

        if args.command == "story":
            markup = generate_nastech_story_markup(
                args.theme,
                emotion=args.emotion,
                sounds=args.sounds,
            )
            from .api import AgentCompileRequest, _compiled

            compiled = _compiled(
                AgentCompileRequest(
                    markup=markup,
                    voice=args.voice,
                    steps=args.steps,
                    provider_id=args.provider,
                    language="en",
                ),
                runtime,
            )
            report: dict[str, Any] = {
                "agent": agent_identity(),
                "story": {
                    "theme": args.theme,
                    "requested_emotion": args.emotion,
                    "sounds": args.sounds,
                    "markup": markup,
                    "rendered": bool(args.output),
                },
                **_compiled_payload(compiled),
            }
            if args.markup_output:
                args.markup_output.parent.mkdir(parents=True, exist_ok=True)
                args.markup_output.write_text(markup + "\n", encoding="utf-8")
                report["markup_output"] = str(args.markup_output)
            if args.output:
                audio = synthesize_with_provider(
                    args.provider,
                    runtime,
                    compiled,
                    language=compiled.manifest["language"],
                )
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_bytes(audio.data)
                manifest_path = args.manifest or args.output.with_suffix(
                    args.output.suffix + ".manifest.json"
                )
                _write_json(manifest_path, compiled.manifest)
                report["audio_output"] = str(args.output)
                report["manifest_output"] = str(manifest_path)
                report["duration_seconds"] = round(audio.duration_seconds, 4)
                if args.clean:
                    cleaned = clean_wav(audio.data)
                    args.output.write_bytes(cleaned.data)
                    report["cleanup"] = cleaned.report
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
                provider_id=args.provider,
                language=args.language,
            )
            _print_or_write(_agent_plan(request, _compiled(request, runtime)), args.output)
            return 0

        if args.command == "validate":
            language = get_language(args.language)
            compiled = compile_nastechml(markup, runtime.settings, language=language.code)
        else:
            from .api import AgentCompileRequest, _compiled

            compiled = _compiled(
                AgentCompileRequest(
                    markup=markup,
                    provider_id=args.provider,
                    language=args.language,
                ),
                runtime,
            )
        if args.command == "validate":
            payload = {
                "valid": True,
                "language": compiled.manifest["language"],
                "span_count": len(compiled.manifest["decisions"]),
                **_compiled_payload(compiled),
            }
            _print_or_write(payload, args.output)
            return 0

        if args.command == "compile":
            _print_or_write(_compiled_payload(compiled), args.output)
            return 0

        if args.command == "synthesize":
            audio = synthesize_with_provider(
                args.provider,
                runtime,
                compiled,
                language=compiled.manifest["language"],
            )
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
        ProviderActivationError,
        AgentExpressionError,
        VocalEventError,
    ) as exc:
        print(f"Nastech error: {exc}")
        return 2

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
