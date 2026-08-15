"""NastechML parsing and language-aware validation.

NastechML keeps a stable application-facing syntax even when synthesis backends
use different prompt conventions. English remains ASCII-only in the default
Nastech core. A multilingual adapter must explicitly select a registered
non-English language before native-script or accented input is accepted.
"""

from __future__ import annotations

import re
import unicodedata
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


def _validate_text(value: str, language: str) -> None:
    """Preserve English-core ASCII gating while rejecting unsafe Unicode controls."""
    if language == "en" and any(ord(character) > 127 for character in value):
        raise NastechMarkupError(
            "Nastech English core accepts ASCII text only. Select a registered multilingual "
            "language provider before submitting non-ASCII input."
        )
    for character in value:
        if unicodedata.category(character) in {"Cc", "Cs"} and character not in "\n\r\t":
            raise NastechMarkupError("NastechML text contains an unsupported control character.")


def _append_text(
    spans: list[AudioSpan], text: str | None, voice: str, style: SpeechStyle, language: str
) -> None:
    if text is None:
        return
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return
    _validate_text(normalized, language)
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
    language: str,
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
    _validate_text(local_voice, "en")
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

    _append_text(spans, element.text, local_voice, local_style, language)
    for child in element:
        _walk(child, local_voice, local_style, spans, language)
        _append_text(spans, child.tail, local_voice, local_style, language)


def parse_nastechml(markup: str, *, language: str = "en") -> tuple[str, list[AudioSpan]]:
    """Parse a NastechML document into a preferred voice and typed audio spans."""
    normalized_language = language.strip().lower().replace("_", "-").split("-", maxsplit=1)[0]
    _validate_text(markup, normalized_language)
    try:
        root = ET.fromstring(markup.strip())
    except ET.ParseError as exc:
        raise NastechMarkupError(f"Invalid NastechML: {exc}") from exc
    if root.tag != "speak":
        raise NastechMarkupError("NastechML must have one <speak> root element.")

    voice = root.attrib.get("voice", "tara")
    _validate_text(voice, "en")
    spans: list[AudioSpan] = []
    _walk(root, voice, SpeechStyle(), spans, normalized_language)
    if not spans:
        raise NastechMarkupError("NastechML did not contain any speech, sounds, or pauses.")
    return voice, spans
