from __future__ import annotations

import importlib.util
from pathlib import Path

from nastech_tts.voices import (
    english_voice_inventory,
    english_voice_summary,
    resolve_english_voice_profile,
)

ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "scripts" / "test_all_registered_voices.py"


def _runner_module():
    spec = importlib.util.spec_from_file_location("story_runner", RUNNER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_english_emotion_rich_story_has_full_control_contract() -> None:
    runner = _runner_module()
    for emotion in (
        "calm",
        "happy",
        "surprised",
        "frustrated",
        "angry",
        "fearful",
        "disgusted",
        "sad",
    ):
        assert f'<emotion name="{emotion}"' in runner.ENGLISH_STORY
    for sound in (
        "laugh",
        "chuckle",
        "sigh",
        "cough",
        "sniffle",
        "groan",
        "yawn",
        "gasp",
        "cry",
        "scream",
        "throatclear",
    ):
        assert f'<sound type="{sound}"' in runner.ENGLISH_STORY
    assert "Nastech Research" in runner.ENGLISH_STORY


def test_every_verified_bantu_route_has_a_native_story_fixture() -> None:
    runner = _runner_module()
    matrix = runner._matrix()
    verified_bantu = {
        row["language"] for row in matrix if row["language"] != "en" and row["model_id"] is not None
    }
    assert verified_bantu <= set(runner.BANTU_STORIES)
    assert len(verified_bantu) == 11
    assert set(runner.BANTU_STORIES) - verified_bantu == {"nso", "ve"}
    for language, story in runner.BANTU_STORIES.items():
        assert "Nastech Research" in story
        assert len(story.split()) >= 35
        if language in {"nso", "ve"}:
            continue  # Native fixture retained, but no verified public local pack exists yet.
        assert language in verified_bantu


def test_english_profile_inventory_has_forty_selectable_styles() -> None:
    summary = english_voice_summary()
    profiles = english_voice_inventory()
    assert summary == {
        "selectable_profiles": 40,
        "verified_base_timbres": 10,
        "delivery_profiles": 30,
    }
    assert len(profiles) == summary["selectable_profiles"]
    assert {profile["base_voice"] for profile in profiles} == {
        "F1",
        "F2",
        "F3",
        "F4",
        "F5",
        "M1",
        "M2",
        "M3",
        "M4",
        "M5",
    }
    profile = resolve_english_voice_profile("en-f3-soft")
    assert profile is not None
    assert profile.base_voice == "F3"
    assert profile.kind == "delivery-profile"
