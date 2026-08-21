import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _workflow_triggers(path: Path) -> dict:
    workflow = yaml.safe_load(path.read_text(encoding="utf-8"))
    return workflow.get("on", workflow.get(True, {}))


def test_pages_site_has_complete_branded_documentation_and_preview_assets() -> None:
    site = ROOT / "site"
    homepage = (site / "index.html").read_text(encoding="utf-8")
    instructions = (site / "instructions.html").read_text(encoding="utf-8")
    previews = json.loads((site / "assets" / "voice-previews.json").read_text(encoding="utf-8"))
    languages = json.loads((site / "assets" / "languages.json").read_text(encoding="utf-8"))

    assert "Nastech Research" in homepage
    assert "Verified English voice previews" in homepage
    assert "Two hours, measured" in homepage
    assert "Nastech TTS instructions for every local user" in instructions
    assert previews["voice_count"] == 40
    assert [voice["profile_id"] for voice in previews["voices"][:10]] == [
        "siya",
        "nasi",
        "jafta",
        "della",
        "axam",
        "alicia",
        "shanice",
        "adam",
        "shakira",
        "shimah",
    ]
    assert len(list((site / "assets" / "voice-previews").glob("*.wav"))) == 40
    assert (site / "assets" / "expressive-all-effects-demo.wav").is_file()
    expressive = json.loads(
        (site / "assets" / "expressive-all-effects-demo.validation.json").read_text(
            encoding="utf-8"
        )
    )
    assert expressive["coverage"]["requested_emotion_count"] == 10
    assert expressive["coverage"]["requested_sound_count"] == 11
    assert expressive["audio"]["levels"]["clipped_samples"] == 0
    assert all(voice["quality"]["clipped_samples"] == 0 for voice in previews["voices"])
    assert len(languages["languages"]) == 61
    assert (
        next(item for item in languages["languages"] if item["code"] == "lg")["display_label"]
        == "lg - Luganda"
    )


def test_pages_and_two_hour_endurance_workflows_publish_and_measure() -> None:
    pages = _workflow_triggers(ROOT / ".github" / "workflows" / "pages.yml")
    endurance = _workflow_triggers(ROOT / ".github" / "workflows" / "two-hour-endurance.yml")
    endurance_source = (ROOT / "scripts" / "run_long_conversation_endurance.py").read_text(
        encoding="utf-8"
    )

    assert "workflow_dispatch" in pages
    assert pages["push"]["branches"] == ["main"]
    assert any(item["cron"] == "23 1 * * 0" for item in endurance["schedule"])
    assert "--require-full-coverage" in (
        ROOT / ".github" / "workflows" / "two-hour-endurance.yml"
    ).read_text(encoding="utf-8")
    assert "DEFAULT_DURATION_SECONDS = 7_200.0" in endurance_source
    assert "cache_disabled_per_segment" in endurance_source
    assert "overall_real_time_factor" in endurance_source
    assert "missing_sound_cues" in endurance_source
