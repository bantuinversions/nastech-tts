import pytest

from nastech_tts.markup import NastechMarkupError, parse_nastechml
from nastech_tts.types import SpanKind


@pytest.mark.parametrize(
    "sound",
    ["chuckle", "cough", "cry", "gasp", "groan", "laugh", "sigh", "sniffle", "yawn"],
)
def test_every_supported_sound_parses_as_a_sound_span(sound: str) -> None:
    voice, spans = parse_nastechml(f'<speak voice="F2"><sound type="{sound}" /></speak>')

    assert voice == "F2"
    assert len(spans) == 1
    assert spans[0].kind == SpanKind.SOUND
    assert spans[0].value == sound
    assert spans[0].voice == "F2"


@pytest.mark.parametrize(
    "emotion",
    [
        "angry",
        "calm",
        "disgusted",
        "excited",
        "fearful",
        "frustrated",
        "happy",
        "neutral",
        "sad",
    ],
)
def test_every_supported_emotion_is_inherited_by_its_speech_span(emotion: str) -> None:
    _, spans = parse_nastechml(f'<speak><emotion name="{emotion}">A short line.</emotion></speak>')

    assert len(spans) == 1
    assert spans[0].kind == SpanKind.SPEECH
    assert spans[0].style.emotion == emotion
    assert spans[0].value == "A short line."


@pytest.mark.parametrize(
    ("rate", "volume"),
    [("slow", "soft"), ("normal", "normal"), ("fast", "loud")],
)
def test_valid_prosody_controls_are_retained(rate: str, volume: str) -> None:
    _, spans = parse_nastechml(
        f'<speak><prosody rate="{rate}" volume="{volume}">Clear speech.</prosody></speak>'
    )

    assert spans[0].style.rate == rate
    assert spans[0].style.volume == volume


@pytest.mark.parametrize(
    "markup",
    [
        "<emotion name='sad'>Wrong root.</emotion>",
        "<speak>   </speak>",
        "<speak><emotion name='sad'>Unclosed.</speak>",
        "<speak><unknown>Unsupported.</unknown></speak>",
        "<speak><sound type='laugh'>text</sound></speak>",
        "<speak><pause ms='not-a-number' /></speak>",
        "<speak><pause ms='10001' /></speak>",
    ],
)
def test_invalid_document_shapes_are_rejected(markup: str) -> None:
    with pytest.raises(NastechMarkupError):
        parse_nastechml(markup)
