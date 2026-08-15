"""Generate a real local 30-minute Nastech continuity test and preset auditions.

The generator renders each narrative chunk independently through the active local
runtime. It joins real PCM output up to the exact requested duration; it never
extends duration by looping, padding, time-stretching, or repeating a WAV.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import wave
from pathlib import Path
from typing import Any

from nastech_tts.audio_levels import validate_release_wav
from nastech_tts.cleanup import clean_wav
from nastech_tts.providers import require_active_provider
from nastech_tts.supertonic import SupertonicRuntime, compile_nastechml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "release" / "longform_continuity"
SAMPLE_RATE_HZ = 44100
SAMPLE_WIDTH_BYTES = 2
CHANNELS = 1
DEFAULT_TARGET_SECONDS = 30 * 60
AUDITION_VOICES = ("M1", "M3", "F1", "F3")


NARRATIVE_BEATS = (
    "At the beginning of the hour, the Nastech Agent opened the workshop before sunrise. "
    "It checked its instruments, named the evidence it needed, and set a patient pace for "
    "the work ahead. Every small signal was recorded, every uncertainty was spoken plainly, "
    "and every useful idea was given room to improve. The goal was not to sound impressive. "
    "The goal was to make a clear voice that could carry a careful story from one listener to "
    "another without losing its meaning.",
    "As the morning gathered light, the team examined a map of questions. Some questions were "
    "simple and some asked for more time, but none were ignored. The Nastech Agent described "
    "what it knew, what it still needed to test, and what could wait for a better answer. "
    "That discipline made the workshop calmer. Progress did not arrive as a sudden claim; it "
    "arrived as a sequence of small checks, honest notes, and voices returning to the same "
    "important idea with greater care.",
    "Later, a distant bell marked the change of task. The local machine kept speaking at an "
    "even pace while the team compared yesterday's measurements with the new ones. They found "
    "one rough edge in the signal, paused, and listened again. A useful system does not hide a "
    "rough edge. It identifies the edge, explains the next test, and makes space for a safer "
    "result. The story continued with confidence that came from evidence rather than noise.",
    "By midday, the workshop had become a place of steady collaboration. A researcher prepared "
    "the next passage, an engineer checked the audio level, and the Nastech Agent kept the "
    "narrative connected. The voice did not rush through a difficult sentence. It used a short "
    "pause, returned to the main thread, and continued. The group learned again that reliable "
    "speech is not only a sound; it is a promise to preserve attention, context, and intent.",
    "In the afternoon, the team considered the people who would hear the final voice. They did "
    "not assume that one style could represent every person or every region. Instead, they "
    "documented the voices they could verify and marked future profiles as work that required "
    "permission, evidence, and review. The Nastech Agent explained this boundary clearly. A "
    "careful release says what is available now and does not borrow an identity it has not earned.",
    "Toward evening, the long test continued through another chapter. Each sentence was rendered "
    "locally, measured, and added to the continuity record. The team watched the duration grow "
    "without adding silence or copying a previous clip. This was important because a long voice "
    "test should show real sustained work. If a system is intended to narrate a book, a lesson, "
    "or a guide, it must keep its footing across many ordinary sentences as well as dramatic ones.",
    "Night approached and the workshop lights became warmer. The Nastech Agent told the listeners "
    "that resilience is built from repeatable habits: verify the input, preserve the output, "
    "measure the result, and report the limit. The voice carried that message through a quiet "
    "section of the story. It remained understandable, neither pretending to be a different "
    "speaker nor claiming a feature outside the accepted contract. The team kept the record open "
    "for anyone who needed to inspect how the result had been made.",
    "At the close of the day, the final chapter returned to the first question: can a local voice "
    "continue with care for a long time? The answer was recorded in audio, not guessed from a "
    "plan. The Nastech Agent thanked the workshop for its patience and invited the next listener "
    "to begin with a small question of their own. The signal was steady, the evidence was clear, "
    "and the story ended ready for another careful day of discovery.",
)

AUDITION_TEXT = (
    "This is a verified Nastech Compact local preset-style audition. "
    "The voice is speaking English, locally, with a measured level and a clear release record."
)


class LongformGenerationError(RuntimeError):
    """Raised when a continuity artifact cannot meet the requested real-audio contract."""


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a real local Nastech long-form continuity test and voice auditions."
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--target-seconds", type=int, default=DEFAULT_TARGET_SECONDS)
    parser.add_argument("--voice", default="F1", help="Verified local long-form voice ID.")
    parser.add_argument("--max-chunks", type=int, default=96)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_pcm_frames(data: bytes) -> bytes:
    with wave.open(io.BytesIO(data), "rb") as reader:
        if (
            reader.getnchannels() != CHANNELS
            or reader.getsampwidth() != SAMPLE_WIDTH_BYTES
            or reader.getframerate() != SAMPLE_RATE_HZ
            or reader.getcomptype() != "NONE"
        ):
            raise LongformGenerationError(
                "Chunk did not meet the mono 16-bit PCM 44.1 kHz contract."
            )
        return reader.readframes(reader.getnframes())


def _render_cleaned(runtime: SupertonicRuntime, markup: str) -> tuple[bytes, dict[str, Any]]:
    compiled = compile_nastechml(markup, runtime.settings)
    audio = runtime.synthesize(compiled, use_cache=False)
    cleaned = clean_wav(audio.data)
    return cleaned.data, {"compiler_manifest": compiled.manifest, "cleanup": cleaned.report}


def _longform_markup(voice: str, chunk_index: int) -> str:
    beat = NARRATIVE_BEATS[chunk_index % len(NARRATIVE_BEATS)]
    marker = f"This is continuity segment {chunk_index + 1}."
    return f'<speak voice="{voice}">{marker} {beat}</speak>'


def _write_auditions(runtime: SupertonicRuntime, output_dir: Path) -> list[dict[str, Any]]:
    auditions: list[dict[str, Any]] = []
    for voice in AUDITION_VOICES:
        markup = f'<speak voice="{voice}">{AUDITION_TEXT}</speak>'
        data, evidence = _render_cleaned(runtime, markup)
        wav_path = output_dir / f"nastech-audition-{voice.lower()}.wav"
        markup_path = output_dir / f"nastech-audition-{voice.lower()}.xml"
        wav_path.write_bytes(data)
        markup_path.write_text(markup + "\n", encoding="utf-8")
        report = validate_release_wav(data)
        auditions.append(
            {
                "voice": voice,
                "wav": wav_path.name,
                "markup": markup_path.name,
                "sha256": _sha256_file(wav_path),
                "levels": report.as_dict(),
                **evidence,
            }
        )
        print(f"Audition {voice}: {report.duration_seconds:.2f}s")
    return auditions


def main() -> int:
    args = _arguments()
    if args.target_seconds < 60 or args.target_seconds > 7200:
        raise LongformGenerationError("target-seconds must be between 60 and 7200.")
    if args.max_chunks < 1 or args.max_chunks > 256:
        raise LongformGenerationError("max-chunks must be between 1 and 256.")
    output_dir = args.output_dir.resolve()
    if output_dir.exists() and any(output_dir.iterdir()) and not args.overwrite:
        raise FileExistsError(f"{output_dir} contains files; use --overwrite to replace them.")
    output_dir.mkdir(parents=True, exist_ok=True)

    provider = require_active_provider("nastech-native-onnx")
    runtime = SupertonicRuntime()
    auditions = _write_auditions(runtime, output_dir)
    target_frames = args.target_seconds * SAMPLE_RATE_HZ
    longform_path = output_dir / "nastech-continuity-30min.wav"
    source_path = output_dir / "nastech-continuity-30min.xml"
    chunk_evidence: list[dict[str, Any]] = []
    frame_count = 0

    with wave.open(str(longform_path), "wb") as writer:
        writer.setnchannels(CHANNELS)
        writer.setsampwidth(SAMPLE_WIDTH_BYTES)
        writer.setframerate(SAMPLE_RATE_HZ)
        for chunk_index in range(args.max_chunks):
            if frame_count >= target_frames:
                break
            markup = _longform_markup(args.voice, chunk_index)
            data, evidence = _render_cleaned(runtime, markup)
            frames = _read_pcm_frames(data)
            remaining_frames = target_frames - frame_count
            frames = frames[: remaining_frames * SAMPLE_WIDTH_BYTES]
            writer.writeframes(frames)
            rendered_frames = len(frames) // SAMPLE_WIDTH_BYTES
            frame_count += rendered_frames
            chunk_evidence.append(
                {
                    "index": chunk_index + 1,
                    "frames_written": rendered_frames,
                    "duration_seconds": round(rendered_frames / SAMPLE_RATE_HZ, 4),
                    **evidence,
                }
            )
            print(
                f"Continuity chunk {chunk_index + 1}: "
                f"{frame_count / SAMPLE_RATE_HZ:.2f}s of {args.target_seconds}s"
            )

    if frame_count < target_frames:
        raise LongformGenerationError(
            f"Rendered {frame_count / SAMPLE_RATE_HZ:.2f}s, below requested {args.target_seconds}s."
        )
    source_path.write_text(
        "\n".join(_longform_markup(args.voice, index) for index in range(len(chunk_evidence)))
        + "\n",
        encoding="utf-8",
    )
    report = validate_release_wav(
        longform_path.read_bytes(),
        minimum_duration_seconds=args.target_seconds,
        maximum_duration_seconds=args.target_seconds + 1,
    )
    manifest = {
        "schema_version": "1.0",
        "publisher": "Nastech Research",
        "service": "nastech-tts",
        "provider_mixer": "nastech",
        "provider": provider.as_dict(),
        "test": "real-local-continuity",
        "target_duration_seconds": args.target_seconds,
        "longform_voice": args.voice,
        "longform": {
            "wav": longform_path.name,
            "markup": source_path.name,
            "sha256": _sha256_file(longform_path),
            "levels": report.as_dict(),
            "chunks": chunk_evidence,
            "generation_method": (
                "real unique local synthesis chunks; joined and truncated only at target duration"
            ),
        },
        "auditions": auditions,
    }
    manifest_path = output_dir / "longform-continuity-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Long-form continuity: {report.duration_seconds:.2f}s")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
