"""Agent-facing expressive response vocabulary for local Nastech TTS.

Natural-language labels make an AI agent easier to instruct, while the renderer is
kept honest: every label resolves to one of the verified NastechML emotion and
sound controls rather than claiming a separately trained voice style.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .markup import _ALLOWED_EMOTIONS, _ALLOWED_RATES, _ALLOWED_SOUNDS, _ALLOWED_VOLUMES


@dataclass(frozen=True)
class EmotionRender:
    """A verified local control profile for an agent-facing emotion label."""

    core_emotion: str
    intensity: float
    rate: str
    volume: str

    def as_dict(self) -> dict[str, str | float]:
        """Return a serializable, explicit renderer setting record."""

        return {
            "core_emotion": self.core_emotion,
            "intensity": self.intensity,
            "rate": self.rate,
            "volume": self.volume,
        }


CORE_EMOTION_PROFILES: dict[str, EmotionRender] = {
    "neutral": EmotionRender("neutral", 0.50, "normal", "normal"),
    "calm": EmotionRender("calm", 0.45, "slow", "soft"),
    "happy": EmotionRender("happy", 0.62, "normal", "normal"),
    "excited": EmotionRender("excited", 0.78, "fast", "loud"),
    "surprised": EmotionRender("surprised", 0.72, "fast", "normal"),
    "sad": EmotionRender("sad", 0.74, "slow", "soft"),
    "angry": EmotionRender("angry", 0.82, "normal", "loud"),
    "frustrated": EmotionRender("frustrated", 0.76, "fast", "normal"),
    "fearful": EmotionRender("fearful", 0.78, "fast", "soft"),
    "disgusted": EmotionRender("disgusted", 0.70, "normal", "normal"),
}

# These alias labels are an agent-convenience taxonomy, not claims of distinct
# model heads. The mapping is deliberately exposed to the caller in each report.
EMOTION_ALIASES: dict[str, str] = {
    "serene": "calm",
    "peaceful": "calm",
    "gentle": "calm",
    "tender": "calm",
    "content": "calm",
    "contentment": "calm",
    "relieved": "calm",
    "relief": "calm",
    "joy": "happy",
    "joyful": "happy",
    "delight": "happy",
    "delighted": "happy",
    "amused": "happy",
    "amusement": "happy",
    "playful": "happy",
    "hopeful": "excited",
    "optimistic": "excited",
    "eager": "excited",
    "energetic": "excited",
    "elated": "excited",
    "triumphant": "excited",
    "triumph": "excited",
    "proud": "excited",
    "pride": "excited",
    "awe": "surprised",
    "awed": "surprised",
    "astonished": "surprised",
    "amazed": "surprised",
    "curious": "surprised",
    "interested": "surprised",
    "realization": "surprised",
    "confused": "surprised",
    "grief": "sad",
    "grieving": "sad",
    "mournful": "sad",
    "disappointed": "sad",
    "nostalgic": "sad",
    "regretful": "sad",
    "irritated": "angry",
    "annoyed": "angry",
    "rage": "angry",
    "furious": "angry",
    "contempt": "angry",
    "anxious": "fearful",
    "nervous": "fearful",
    "worried": "fearful",
    "alarmed": "fearful",
    "horrified": "fearful",
    "embarrassed": "frustrated",
    "ashamed": "frustrated",
    "guilty": "frustrated",
    "awkward": "frustrated",
    "repulsed": "disgusted",
    "revulsed": "disgusted",
}

SOUND_ALIASES: dict[str, str] = {
    "laughter": "laugh",
    "laughing": "laugh",
    "giggle": "chuckle",
    "giggling": "chuckle",
    "sob": "cry",
    "sobbing": "cry",
    "shriek": "scream",
    "shrieking": "scream",
    "exhale": "sigh",
    "exhaling": "sigh",
    "inhale": "gasp",
    "inhale_sharp": "gasp",
    "throat-clear": "throatclear",
    "throat_clear": "throatclear",
    "clear_throat": "throatclear",
}


class AgentExpressionError(ValueError):
    """Raised when an agent asks for an unavailable expression label."""


def _normalized(value: str) -> str:
    return value.strip().lower().replace(" ", "_")


def resolve_emotion(value: str | None) -> tuple[str, EmotionRender, bool]:
    """Resolve a core emotion or natural-language alias to a verified profile."""

    requested = _normalized(value or "neutral")
    core = EMOTION_ALIASES.get(requested, requested)
    if core not in CORE_EMOTION_PROFILES:
        allowed = ", ".join(available_emotions())
        raise AgentExpressionError(
            f"Unsupported agent emotion '{value}'. Available core emotions and aliases: {allowed}."
        )
    return requested, CORE_EMOTION_PROFILES[core], requested != core


def resolve_sound(value: str) -> tuple[str, str, bool]:
    """Resolve a core sound cue or natural-language cue alias."""

    requested = _normalized(value)
    core = SOUND_ALIASES.get(requested, requested)
    if core not in _ALLOWED_SOUNDS:
        allowed = ", ".join(available_sounds())
        raise AgentExpressionError(
            f"Unsupported agent sound '{value}'. Available sounds: {allowed}."
        )
    return requested, core, requested != core


def resolve_sounds(values: list[str] | tuple[str, ...] | None) -> list[dict[str, str | bool]]:
    """Normalize any number of agent-requested sound cues in their requested order."""

    resolved: list[dict[str, str | bool]] = []
    for value in values or []:
        requested, core, was_alias = resolve_sound(value)
        resolved.append({"requested": requested, "rendered": core, "alias_applied": was_alias})
    return resolved


def available_emotions() -> tuple[str, ...]:
    """Return stable core emotion identifiers followed by documented aliases."""

    return tuple(sorted({*CORE_EMOTION_PROFILES, *EMOTION_ALIASES}))


def available_sounds() -> tuple[str, ...]:
    """Return stable core sound identifiers followed by documented aliases."""

    return tuple(sorted({*_ALLOWED_SOUNDS, *SOUND_ALIASES}))


def agent_expression_capabilities() -> dict[str, Any]:
    """Describe the exact local expression contract for AI tools and CLI callers."""

    return {
        "contract": "nastech-agent-expression-v1",
        "rendering_boundary": (
            "Alias labels map to the documented ten local NastechML emotions and eleven local "
            "sound cues. They do not represent separately trained emotion models."
        ),
        "core_emotions": {
            name: profile.as_dict() for name, profile in sorted(CORE_EMOTION_PROFILES.items())
        },
        "emotion_aliases": dict(sorted(EMOTION_ALIASES.items())),
        "core_sounds": sorted(_ALLOWED_SOUNDS),
        "sound_aliases": dict(sorted(SOUND_ALIASES.items())),
        "rates": sorted(_ALLOWED_RATES),
        "volumes": sorted(_ALLOWED_VOLUMES),
        "maximum_sound_cues_per_agent_response": len(_ALLOWED_SOUNDS),
    }


def agent_markup(
    text: str,
    *,
    voice: str = "siya",
    emotion: str | None = None,
    intensity: float | None = None,
    rate: str | None = None,
    volume: str | None = None,
    sounds: list[str] | tuple[str, ...] | None = None,
) -> tuple[str, dict[str, Any]]:
    """Build a validated-style NastechML response and transparent resolution metadata."""

    from html import escape

    requested, profile, emotion_was_alias = resolve_emotion(emotion)
    effective_intensity = profile.intensity if intensity is None else intensity
    if not 0.0 <= effective_intensity <= 1.0:
        raise AgentExpressionError("Emotion intensity must be between 0 and 1.")
    effective_rate = profile.rate if rate is None else _normalized(rate)
    effective_volume = profile.volume if volume is None else _normalized(volume)
    if effective_rate not in _ALLOWED_RATES:
        raise AgentExpressionError(
            f"Unsupported rate '{rate}'. Allowed: {', '.join(sorted(_ALLOWED_RATES))}."
        )
    if effective_volume not in _ALLOWED_VOLUMES:
        raise AgentExpressionError(
            f"Unsupported volume '{volume}'. Allowed: {', '.join(sorted(_ALLOWED_VOLUMES))}."
        )
    rendered_sounds = resolve_sounds(sounds)
    cues = "".join(f'<sound type="{item["rendered"]}" />' for item in rendered_sounds)
    markup = (
        f'<speak voice="{escape(voice, quote=True)}"><prosody rate="{effective_rate}" '
        f'volume="{effective_volume}"><emotion name="{profile.core_emotion}" '
        f'intensity="{effective_intensity:.2f}">{escape(text)}</emotion>{cues}</prosody></speak>'
    )
    return markup, {
        "requested_emotion": requested,
        "rendered_emotion": profile.core_emotion,
        "emotion_alias_applied": emotion_was_alias,
        "intensity": effective_intensity,
        "rate": effective_rate,
        "volume": effective_volume,
        "sounds": rendered_sounds,
    }


assert set(CORE_EMOTION_PROFILES) == _ALLOWED_EMOTIONS
