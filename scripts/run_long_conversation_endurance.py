"""Render and measure a deterministic long local Nastech conversation endurance suite.

The suite concatenates bounded, cache-disabled English synthesis segments into an
exact-duration WAV. It reports observed elapsed time and quality gates for the
specific runner; it does not claim a universal long-conversation guarantee.
"""

from __future__ import annotations

import argparse
import io
import json
import resource
import sys
import time
import wave
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from nastech_tts.audio_levels import validate_release_wav  # noqa: E402
from nastech_tts.cleanup import clean_wav  # noqa: E402
from nastech_tts.supertonic import SupertonicRuntime, compile_nastechml  # noqa: E402

OUTPUT_RATE = 44_100
DEFAULT_DURATION_SECONDS = 7_200.0
DEFAULT_SEGMENT_SECONDS = 60.0

# A bounded turn bank with named voices, the ten local expression controls, and
# every sound cue. Repetition is intentional: it enables an exact-duration,
# reproducible endurance workload without pretending it is unscripted dialogue.
TURN_BANK = (
    (
        "siya",
        "neutral",
        "Nastech Research begins a careful local conversation check.",
        "throatclear",
    ),
    ("jafta", "calm", "I will listen, measure each response, and keep the session steady.", "sigh"),
    ("nasi", "happy", "The local voice is ready, and the dialogue remains clear.", "laugh"),
    ("adam", "excited", "Each completed turn gives us useful timing evidence.", "gasp"),
    ("della", "surprised", "A new result appears, so we verify it before we continue.", "chuckle"),
    ("shanice", "sad", "When a response is difficult, we record the limitation honestly.", "cry"),
    (
        "axam",
        "angry",
        "Errors are not hidden. They are investigated with controlled focus.",
        "cough",
    ),
    (
        "shakira",
        "frustrated",
        "A long conversation can be demanding, but bounded turns help.",
        "groan",
    ),
    (
        "shimah",
        "fearful",
        "If a warning appears, we stop safely and preserve the evidence.",
        "scream",
    ),
    (
        "alicia",
        "disgusted",
        "We reject unsafe audio and continue only after validation.",
        "sniffle",
    ),
    ("siya", "calm", "The session pauses briefly, then returns to a measured pace.", "yawn"),
)


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duration-seconds", type=float, default=DEFAULT_DURATION_SECONDS)
    parser.add_argument("--segment-seconds", type=float, default=DEFAULT_SEGMENT_SECONDS)
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "release" / "long_conversation_endurance"
    )
    parser.add_argument("--keep-full-wav", action="store_true")
    parser.add_argument(
        "--require-full-coverage",
        action="store_true",
        help="Fail unless every scripted voice, emotion, and sound cue rendered at least once.",
    )
    return parser.parse_args()


def _wav_parts(data: bytes) -> tuple[int, np.ndarray]:
    with wave.open(io.BytesIO(data), "rb") as handle:
        if handle.getnchannels() != 1 or handle.getsampwidth() != 2:
            raise RuntimeError("Local endurance segments must be mono 16-bit PCM WAV.")
        rate = handle.getframerate()
        samples = np.frombuffer(handle.readframes(handle.getnframes()), dtype="<i2").copy()
    return rate, samples


def _resample(samples: np.ndarray, source_rate: int) -> np.ndarray:
    if source_rate == OUTPUT_RATE:
        return samples
    target_length = max(1, round(len(samples) * OUTPUT_RATE / source_rate))
    source_positions = np.linspace(0.0, 1.0, num=len(samples), endpoint=False)
    target_positions = np.linspace(0.0, 1.0, num=target_length, endpoint=False)
    return np.rint(np.interp(target_positions, source_positions, samples)).astype(np.int16)


def _segment_markup(seed: int, turn_count: int) -> tuple[str, list[tuple[str, str, str, str]]]:
    turns = []
    selected_turns = [TURN_BANK[(seed + index) % len(TURN_BANK)] for index in range(turn_count)]
    for offset, (voice, emotion, text, sound) in enumerate(selected_turns):
        intensity = 0.52 + ((seed + offset) % 4) * 0.10
        turns.append(
            f'<emotion name="{emotion}" intensity="{intensity:.2f}">'
            f'<speak voice="{voice}">{text}</speak></emotion>'
            f'<sound type="{sound}" /><pause ms="280" />'
        )
    return f"<speak>{''.join(turns)}</speak>", selected_turns


def _resource_memory_mib() -> float:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # Linux reports KiB while macOS reports bytes. The endurance workflow is
    # Ubuntu today, but this preserves a portable recorded signal.
    return round(value / (1024 * 1024) if sys.platform == "darwin" else value / 1024, 2)


def _write_excerpt(source: Path, destination: Path, seconds: float = 60.0) -> None:
    with wave.open(str(source), "rb") as reader, wave.open(str(destination), "wb") as writer:
        writer.setparams(reader.getparams())
        writer.writeframes(reader.readframes(int(reader.getframerate() * seconds)))


def main() -> int:
    args = _args()
    if args.duration_seconds < 15.0:
        raise ValueError("--duration-seconds must be at least 15 seconds.")
    if not 10.0 <= args.segment_seconds <= 180.0:
        raise ValueError("--segment-seconds must be between 10 and 180.")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    full_wav = args.output_dir / "two-hour-local-conversation.wav"
    excerpt = args.output_dir / "two-hour-local-conversation-excerpt.wav"
    report_path = args.output_dir / "two-hour-local-conversation-report.json"
    target_frames = int(args.duration_seconds * OUTPUT_RATE)
    runtime = SupertonicRuntime()
    runtime.warmup()
    started = time.perf_counter()
    total_frames = 0
    segment_records: list[dict[str, Any]] = []
    next_seed = 0
    # A typical scripted turn is roughly six seconds after local rendering.
    # Constrain one inference request to a small cycle of turns, then repeat.
    turn_count = max(2, min(len(TURN_BANK), round(args.segment_seconds / 6.0)))

    with wave.open(str(full_wav), "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(OUTPUT_RATE)
        while total_frames < target_frames:
            markup, selected_turns = _segment_markup(next_seed, turn_count)
            segment_started = time.perf_counter()
            compiled = compile_nastechml(markup, runtime.settings)
            audio = runtime.synthesize(compiled, use_cache=False)
            cleaned = clean_wav(audio.data)
            source_rate, samples = _wav_parts(cleaned.data)
            samples = _resample(samples, source_rate)
            remaining = target_frames - total_frames
            emitted = samples[:remaining]
            writer.writeframes(emitted.tobytes())
            elapsed = time.perf_counter() - segment_started
            emitted_seconds = len(emitted) / OUTPUT_RATE
            total_frames += len(emitted)
            segment_records.append(
                {
                    "index": next_seed,
                    "elapsed_seconds": round(elapsed, 4),
                    "audio_seconds": round(emitted_seconds, 4),
                    "real_time_factor": round(elapsed / emitted_seconds, 4),
                    "frames": int(len(emitted)),
                    "runtime_peak_rss_mib": _resource_memory_mib(),
                    "cleanup": cleaned.report,
                    "turns": [
                        {"voice": voice, "emotion": emotion, "sound": sound}
                        for voice, emotion, _text, sound in selected_turns
                    ],
                }
            )
            next_seed += 1

    elapsed_total = time.perf_counter() - started
    quality = validate_release_wav(
        full_wav.read_bytes(), maximum_duration_seconds=args.duration_seconds + 2.0
    ).as_dict()
    if quality["duration_seconds"] < args.duration_seconds * 0.999:
        raise RuntimeError("Assembled conversation did not reach the requested duration.")
    if quality["clipped_samples"] != 0:
        raise RuntimeError("Assembled conversation contains clipped samples.")
    _write_excerpt(full_wav, excerpt)
    rendered_voices = sorted(
        {turn["voice"] for segment in segment_records for turn in segment["turns"]}
    )
    rendered_emotions = sorted(
        {turn["emotion"] for segment in segment_records for turn in segment["turns"]}
    )
    rendered_sounds = sorted(
        {turn["sound"] for segment in segment_records for turn in segment["turns"]}
    )
    required_voices = sorted({turn[0] for turn in TURN_BANK})
    required_emotions = sorted({turn[1] for turn in TURN_BANK})
    required_sounds = sorted({turn[3] for turn in TURN_BANK})
    coverage = {
        "rendered_voice_profiles": rendered_voices,
        "rendered_emotion_controls": rendered_emotions,
        "rendered_sound_cues": rendered_sounds,
        "missing_voice_profiles": sorted(set(required_voices).difference(rendered_voices)),
        "missing_emotion_controls": sorted(set(required_emotions).difference(rendered_emotions)),
        "missing_sound_cues": sorted(set(required_sounds).difference(rendered_sounds)),
    }
    if args.require_full_coverage and any(
        coverage[key]
        for key in ("missing_voice_profiles", "missing_emotion_controls", "missing_sound_cues")
    ):
        raise RuntimeError(f"Endurance coverage gate failed: {coverage}")
    report = {
        "schema_version": "1.0",
        "publisher": "Nastech Research",
        "suite": "two-hour-local-conversation-endurance",
        "status": "passed",
        "contract": {
            "requested_duration_seconds": args.duration_seconds,
            "segment_target_seconds": args.segment_seconds,
            "turn_bank_size": len(TURN_BANK),
            "turns_per_segment": turn_count,
            "voice_profiles": required_voices,
            "emotion_controls": required_emotions,
            "sound_cues": required_sounds,
            "cache_disabled_per_segment": True,
            "local_cleanup_per_segment": True,
        },
        "observed": {
            "elapsed_seconds": round(elapsed_total, 4),
            "elapsed_minutes": round(elapsed_total / 60.0, 4),
            "assembled_audio_seconds": quality["duration_seconds"],
            "overall_real_time_factor": round(elapsed_total / quality["duration_seconds"], 4),
            "segment_count": len(segment_records),
            "peak_observed_rss_mib": max(
                record["runtime_peak_rss_mib"] for record in segment_records
            ),
            "full_wav_bytes": full_wav.stat().st_size,
        },
        "quality": quality,
        "coverage": coverage,
        "outputs": {
            "analysis_report": report_path.name,
            "excerpt": excerpt.name,
            "full_wav_retained": args.keep_full_wav,
        },
        "segments": segment_records,
        "boundary": (
            "This report describes the documented input, runtime revision, dependencies, and "
            "runner for this execution. It is not a universal guarantee for all hardware, "
            "language packs, or future model revisions."
        ),
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not args.keep_full_wav:
        full_wav.unlink()
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
