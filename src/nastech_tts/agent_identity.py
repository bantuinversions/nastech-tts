"""Nastech Agent identity and deterministic expressive story composition.

Nastech Agent is the local TTS orchestration identity published by Nastech
Research. Story composition is template-based and produces NastechML that can
be compiled and synthesized by an active local Nastech provider; it is not a
claim of a cloud language-model service or autonomous narration system.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from xml.sax.saxutils import escape

from .markup import _ALLOWED_EMOTIONS, _ALLOWED_SOUNDS, parse_nastechml

PUBLISHER = "Nastech Research"
AGENT_NAME = "Nastech Agent"
AGENT_SLUG = "nastech-agent"


@dataclass(frozen=True)
class StoryTemplate:
    """A named Nastech Agent story template with local, English-only text."""

    theme: str
    title: str
    opening: str
    turning_point: str
    closing: str


_STORY_TEMPLATES: dict[str, StoryTemplate] = {
    "innovation": StoryTemplate(
        theme="innovation",
        title="The Signal in the Workshop",
        opening="At Nastech Research, a quiet signal waited inside a small local machine.",
        turning_point=(
            "The Nastech Agent listened, tested one careful idea, and found a clearer path."
        ),
        closing="By morning, the signal had become a useful voice, made with patience and proof.",
    ),
    "discovery": StoryTemplate(
        theme="discovery",
        title="The Map of Small Wonders",
        opening="Nastech Agent opened a map where every question began as a small point of light.",
        turning_point=(
            "It followed the brightest clue, checked the evidence, and discovered a new route."
        ),
        closing="The team learned that discovery grows when curiosity is paired with care.",
    ),
    "resilience": StoryTemplate(
        theme="resilience",
        title="The Voice That Returned",
        opening="During a long night, a local voice faltered, then paused to gather strength.",
        turning_point=(
            "Nastech Agent returned to the work, measured each step, and tried again with courage."
        ),
        closing=(
            "At dawn, the voice returned steady, reminding everyone that progress can be rebuilt."
        ),
    ),
}


def agent_identity() -> dict[str, Any]:
    """Describe the product identity without implying repository transfer or AI claims."""
    return {
        "name": AGENT_NAME,
        "slug": AGENT_SLUG,
        "publisher": PUBLISHER,
        "repository_owner": "bantuinversions",
        "identity_role": "local expressive TTS planning and story composition",
        "runtime_boundary": (
            "Stories are deterministic English NastechML templates. Synthesis uses an active "
            "local Nastech provider and does not require a cloud language model."
        ),
        "supported_story_themes": list(_STORY_TEMPLATES),
        "brand_mark": "assets/nastech-research-mark.png",
    }


def supported_story_themes() -> tuple[str, ...]:
    """Return the stable, documented story-theme identifiers."""
    return tuple(_STORY_TEMPLATES)


def supported_story_emotions() -> tuple[str, ...]:
    """Return natural CLI/API story emotions mapped to supported NastechML."""
    return ("hopeful", *sorted(_ALLOWED_EMOTIONS))


def supported_story_sounds() -> tuple[str, ...]:
    """Return the sound cues permitted in generated Nastech Agent stories."""
    return tuple(sorted(_ALLOWED_SOUNDS))


def _validate_emotion(emotion: str) -> str:
    normalized = emotion.strip().lower()
    if normalized not in _ALLOWED_EMOTIONS:
        allowed = ", ".join(sorted(_ALLOWED_EMOTIONS))
        raise ValueError(f"Unsupported story emotion '{emotion}'. Allowed: {allowed}.")
    return normalized


def _validate_sounds(sounds: tuple[str, ...] | list[str] | None) -> tuple[str, ...]:
    if sounds is None:
        return ()
    normalized = tuple(sound.strip().lower() for sound in sounds)
    unknown = sorted(set(normalized) - _ALLOWED_SOUNDS)
    if unknown:
        allowed = ", ".join(sorted(_ALLOWED_SOUNDS))
        raise ValueError(f"Unsupported story sound '{unknown[0]}'. Allowed: {allowed}.")
    if len(normalized) > 3:
        raise ValueError("A Nastech Agent story accepts at most three sound cues.")
    return normalized


def generate_nastech_story_markup(
    theme: str = "innovation",
    *,
    emotion: str = "hopeful",
    sounds: tuple[str, ...] | list[str] | None = None,
) -> str:
    """Build and validate deterministic English NastechML for a branded short story.

    ``hopeful`` is treated as the supported ``excited`` rendering style to keep
    the external story vocabulary natural while preserving the published
    NastechML emotion contract.
    """
    normalized_theme = theme.strip().lower()
    if normalized_theme not in _STORY_TEMPLATES:
        allowed = ", ".join(supported_story_themes())
        raise ValueError(f"Unsupported story theme '{theme}'. Allowed: {allowed}.")
    normalized_emotion = (
        "excited" if emotion.strip().lower() == "hopeful" else _validate_emotion(emotion)
    )
    sound_cues = _validate_sounds(sounds)
    story = _STORY_TEMPLATES[normalized_theme]
    opening = escape(story.opening)
    turning_point = escape(story.turning_point)
    closing = escape(story.closing)
    cues = "".join(f'<sound type="{sound}" />' for sound in sound_cues)
    markup = (
        f'<speak><emotion name="{normalized_emotion}" intensity="0.68">{opening}</emotion>'
        f'<pause ms="450" />{cues}<emotion name="{normalized_emotion}" intensity="0.74">'
        f'{turning_point}</emotion><pause ms="500" /><emotion name="calm" intensity="0.58">'
        f"{closing}</emotion></speak>"
    )
    parse_nastechml(markup)
    return markup
