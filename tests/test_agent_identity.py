import pytest

from nastech_tts.agent_identity import (
    agent_identity,
    generate_nastech_story_markup,
    supported_story_themes,
)
from nastech_tts.markup import parse_nastechml


def test_agent_identity_credits_nastech_research_without_claiming_repo_transfer() -> None:
    identity = agent_identity()

    assert identity["name"] == "Nastech Agent"
    assert identity["publisher"] == "Nastech Research"
    assert identity["repository_owner"] == "bantuinversions"
    assert identity["brand_mark"] == "assets/nastech-research-mark.png"


def test_story_markup_is_valid_english_nastechml_with_requested_expression() -> None:
    markup = generate_nastech_story_markup(
        "resilience",
        emotion="sad",
        sounds=["sigh", "laugh"],
    )
    voice, spans = parse_nastechml(markup)

    assert voice == "tara"
    assert "Nastech Agent returned" in markup
    assert '<emotion name="sad"' in markup
    assert '<sound type="sigh" />' in markup
    assert '<sound type="laugh" />' in markup
    assert len(spans) >= 5


def test_hopeful_story_maps_to_supported_excited_markup() -> None:
    markup = generate_nastech_story_markup("discovery")

    assert '<emotion name="excited"' in markup
    assert "Nastech Agent opened a map" in markup


@pytest.mark.parametrize("theme", ["", "unknown"])
def test_story_rejects_unknown_theme(theme: str) -> None:
    with pytest.raises(ValueError, match="Unsupported story theme"):
        generate_nastech_story_markup(theme)


def test_story_rejects_unknown_sound_cue() -> None:
    with pytest.raises(ValueError, match="Unsupported story sound"):
        generate_nastech_story_markup("innovation", sounds=["whistle"])


def test_story_theme_catalog_is_stable() -> None:
    assert supported_story_themes() == ("innovation", "discovery", "resilience")
