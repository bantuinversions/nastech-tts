from __future__ import annotations

from nastech_tts.supertonic import CompactSettings, compile_nastechml
from nastech_tts.voices import english_voice_inventory, english_voice_summary


def test_english_voice_profiles_are_truthfully_bounded() -> None:
    summary = english_voice_summary()
    profiles = english_voice_inventory()
    assert summary["selectable_profiles"] == 40
    assert summary["verified_base_timbres"] == 10
    assert summary["delivery_profiles"] == 30
    assert {profile["kind"] for profile in profiles} == {
        "named-base-profile",
        "delivery-profile",
    }
    named = {profile["label"]: profile["base_voice"] for profile in profiles}
    assert {
        name: named[name]
        for name in (
            "Siya",
            "Nasi",
            "Jafta",
            "Della",
            "Axam",
            "Alicia",
            "Shanice",
            "Adam",
            "Shakira",
            "Shimah",
        )
    } == {
        "Siya": "F1",
        "Nasi": "F2",
        "Jafta": "M1",
        "Della": "F3",
        "Axam": "M2",
        "Alicia": "F4",
        "Shanice": "F5",
        "Adam": "M3",
        "Shakira": "M4",
        "Shimah": "M5",
    }


def test_profile_alias_resolves_to_a_verified_base_timbre() -> None:
    compiled = compile_nastechml(
        '<speak voice="en-f3-soft">Nastech speaks locally.</speak>',
        CompactSettings(default_voice="F1"),
    )
    assert compiled.voice == "F3"
    assert compiled.manifest["requested_voice"] == "en-f3-soft"
    assert compiled.manifest["voice_profile"] == {
        "profile_id": "en-f3-soft",
        "base_voice": "F3",
        "kind": "delivery-profile",
        "default_speed": 0.9,
        "description": (
            "Slower, gentle delivery using verified Supertonic F3. "
            "This is a delivery profile, not a distinct trained speaker identity."
        ),
    }
    assert compiled.speed == 0.9
