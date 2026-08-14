"""NastechML parsing and validation.

NastechML keeps a stable application-facing syntax even when synthesis backends
use different prompt conventions.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import replace

from .types import AudioSpan, SpanKind, SpeechStyle


class NastechMarkupError(ValueError):
    """Raised when NastechML is invalid or requests unsupported document syntax."""


_ALLOWED_SOUNDS = {
    "laugh",
    "chuckle",
    "sigh",
    "cough",
    "sniffle",
    "groan",
    "yawn",
    "gasp",
    "cry",
}
_ALLOWED_EMOTIONS = {
    "angry",
    "sad",
    "happy",
    "excited",
    "fearful",
    "disgusted",
    "frustrated",
    "neutral",
    "calm",
}
_ALLOWED_RATES = {"slow", "normal", "fast"}
_ALLOWED_VOLUMES = {"soft", "normal", "loud"}


def _validate_english(value: str) -> None:
    if any(ord(character) > 127 for character in value):
        raise NastechMarkupError(
            "Nastech TTS 0.1 accepts English/ASCII text only. Non-ASCII input was found."
        )


def _append_text(spans: list[AudioSpan], text: str | None, voice: str, style: SpeechStyle) -> None:
    if text is None:
        return
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return
    _validate_english(normalized)
    spans.append(AudioSpan(kind=SpanKind.SPEECH, value=normalized, voice=voice, style=style))


def _parse_intensity(raw_value: str | None) -> float | None:
    if raw_value is None:
        return None
    try:
        intensity = float(raw_value)
    except ValueError as exc:
        raise NastechMarkupError("Emotion intensity must be a number between 0 and 1.") from exc
    if not 0.0 <= intensity <= 1.0:
        raise NastechMarkupError("Emotion intensity must be between 0 and 1.")
    return intensity


def _walk(
    element: ET.Element,
    voice: str,
    style: SpeechStyle,
    spans: list[AudioSpan],
) -> None:
    tag = element.tag
    if tag == "sound":
        if list(element) or (element.text or "").strip():
            raise NastechMarkupError("<sound> must be an empty element.")
        sound_type = element.attrib.get("type", "").lower()
        if sound_type not in _ALLOWED_SOUNDS:
            allowed = ", ".join(sorted(_ALLOWED_SOUNDS))
            raise NastechMarkupError(f"Unsupported sound '{sound_type}'. Allowed: {allowed}.")
        spans.append(AudioSpan(kind=SpanKind.SOUND, value=sound_type, voice=voice, style=style))
        return

    if tag == "pause":
        if list(element) or (element.text or "").strip():
            raise NastechMarkupError("<pause> must be an empty element.")
        try:
            milliseconds = int(element.attrib.get("ms", ""))
        except ValueError as exc:
            raise NastechMarkupError(
                "<pause ms=...> requires an integer number of milliseconds."
            ) from exc
        if not 0 <= milliseconds <= 10_000:
            raise NastechMarkupError("Pause duration must be from 0 to 10000 ms.")
        spans.append(AudioSpan(kind=SpanKind.PAUSE, value=milliseconds, voice=voice, style=style))
        return

    if tag not in {"speak", "emotion", "prosody"}:
        raise NastechMarkupError(f"Unsupported NastechML element <{tag}>.")

    local_voice = element.attrib.get("voice", voice)
    _validate_english(local_voice)
    local_style = style

    if tag == "emotion":
        emotion = element.attrib.get("name", "").lower()
        if emotion not in _ALLOWED_EMOTIONS:
            allowed = ", ".join(sorted(_ALLOWED_EMOTIONS))
            raise NastechMarkupError(f"Unsupported emotion '{emotion}'. Allowed: {allowed}.")
        local_style = replace(
            style,
            emotion=emotion,
            intensity=_parse_intensity(element.attrib.get("intensity")),
        )
    elif tag == "prosody":
        rate = element.attrib.get("rate", style.rate)
        volume = element.attrib.get("volume", style.volume)
        if rate is not None and rate not in _ALLOWED_RATES:
            raise NastechMarkupError("Prosody rate must be slow, normal, or fast.")
        if volume is not None and volume not in _ALLOWED_VOLUMES:
            raise NastechMarkupError("Prosody volume must be soft, normal, or loud.")
        local_style = replace(style, rate=rate, volume=volume)

    _append_text(spans, element.text, local_voice, local_style)
    for child in element:
        _walk(child, local_voice, local_style, spans)
        _append_text(spans, child.tail, local_voice, local_style)


def parse_nastechml(markup: str) -> tuple[str, list[AudioSpan]]:
    """Parse a NastechML document into a preferred voice and typed audio spans."""
    _validate_english(markup)
    try:
        root = ET.fromstring(markup.strip())
    except ET.ParseError as exc:
        raise NastechMarkupError(f"Invalid NastechML: {exc}") from exc
    if root.tag != "speak":
        raise NastechMarkupError("NastechML must have one <speak> root element.")

    voice = root.attrib.get("voice", "tara")
    _validate_english(voice)
    spans: list[AudioSpan] = []
    _walk(root, voice, SpeechStyle(), spans)
    if not spans:
        raise NastechMarkupError("NastechML did not contain any speech, sounds, or pauses.")
    return voice, spans
