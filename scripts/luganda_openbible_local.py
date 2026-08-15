"""Render reviewed OpenBible Luganda VITS speech in an isolated optional runtime.

This script deliberately lives outside the Nastech Compact core. It downloads the
public reviewed model only when the operator runs it, selects a named training-set
speaker, performs CPU-only local inference, and writes the provider-native WAV.
Nastech's guarded adapter normalizes the resulting WAV to its delivery contract.
"""

from __future__ import annotations

import argparse
from pathlib import Path

MODEL_ID = "multilingual-tts/VITS-OpenBible-Luganda"
MODEL_FILES = ("model_last.pth", "config.json", "speakers.pth")


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render local Luganda VITS audio.")
    parser.add_argument("--text", required=True)
    parser.add_argument("--out_path", required=True, type=Path)
    parser.add_argument("--speaker")
    parser.add_argument(
        "--list-speakers",
        action="store_true",
        help="Print available training-set speaker IDs and exit without loading model weights.",
    )
    parser.add_argument(
        "--model-cache",
        type=Path,
        default=Path.home() / ".cache" / "nastech-luganda-openbible",
    )
    return parser.parse_args()


def main() -> int:
    args = _arguments()
    try:
        import torch
        from huggingface_hub import hf_hub_download
        from TTS.tts.utils.speakers import SpeakerManager
        from TTS.utils.synthesizer import Synthesizer
    except ImportError as exc:
        raise RuntimeError(
            "Install the optional isolated coqui-tts runtime before running the Luganda wrapper."
        ) from exc

    args.model_cache.mkdir(parents=True, exist_ok=True)
    downloaded = {
        name: hf_hub_download(repo_id=MODEL_ID, filename=name, cache_dir=str(args.model_cache))
        for name in ("config.json", "speakers.pth")
    }
    speaker_manager = SpeakerManager(speaker_id_file_path=downloaded["speakers.pth"])
    speakers = sorted(speaker_manager.speaker_names)
    if args.list_speakers:
        print("\n".join(speakers))
        return 0
    if not args.speaker:
        raise ValueError("--speaker is required unless --list-speakers is used.")
    downloaded["model_last.pth"] = hf_hub_download(
        repo_id=MODEL_ID,
        filename="model_last.pth",
        cache_dir=str(args.model_cache),
    )
    synthesizer = Synthesizer(
        tts_checkpoint=downloaded["model_last.pth"],
        tts_config_path=downloaded["config.json"],
        tts_speakers_file=downloaded["speakers.pth"],
        use_cuda=False,
    )
    if synthesizer.tts_model.speaker_manager is None:
        synthesizer.tts_model.speaker_manager = SpeakerManager(
            speaker_id_file_path=downloaded["speakers.pth"]
        )
    if args.speaker not in speakers:
        available = ", ".join(speakers[:30])
        raise ValueError(
            f"Unknown Luganda training-set speaker '{args.speaker}'. Available: {available}"
        )
    if torch.cuda.is_available():
        raise RuntimeError("Luganda wrapper is configured for CPU-only Nastech validation.")
    waveform = synthesizer.tts(
        text=args.text,
        speaker_name=args.speaker,
        split_sentences=True,
    )
    args.out_path.parent.mkdir(parents=True, exist_ok=True)
    synthesizer.save_wav(wav=waveform, path=str(args.out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
