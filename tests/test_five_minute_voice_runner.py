from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "test_all_registered_voices.py"


def test_voice_matrix_covers_english_and_verified_bantu_targets() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--list-json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    rows = json.loads(result.stdout)
    assert len(rows) == 23
    assert {row["language"] for row in rows if row["story_available"]} == {
        "en",
        "lg",
        "nyn",
        "ach",
        "teo",
        "sw",
        "rw",
        "rn",
        "ki",
        "nso",
        "ve",
        "ts",
        "sn",
        "ny",
    }


def test_english_story_declares_all_expressive_sound_cues() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    for sound in ("laugh", "chuckle", "sigh", "cough", "sniffle", "groan", "yawn", "gasp", "cry"):
        assert f'type="{sound}"' in source
    for emotion in ("calm", "frustrated", "angry", "fearful", "disgusted", "sad"):
        assert emotion in source.lower()


def test_unverified_language_is_not_silently_substituted(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--language",
            "zu",
            "--duration-seconds",
            "1",
            "--output-dir",
            str(tmp_path),
            "--report",
            str(tmp_path / "report.json"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "no verified local model pack" in result.stderr.lower()
