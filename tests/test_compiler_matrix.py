from pathlib import Path

import pytest

from nastech_tts.supertonic import CompactSettings, compile_nastechml
from nastech_tts.types import Fidelity


def _settings() -> CompactSettings:
    return CompactSettings(default_voice="F4", cache_dir=Path("/tmp/nastech-test-cache"))


@pytest.mark.parametrize(
    "voice_markup",
    [
        "<speak>Hello.</speak>",
        '<speak voice="tara">Hello.</speak>',
        '<speak voice="default">Hello.</speak>',
        '<speak voice="nastech">Hello.</speak>',
    ],
)
def test_default_voice_aliases_route_to_configured_local_voice(voice_markup: str) -> None:
    compiled = compile_nastechml(voice_markup, _settings())

    assert compiled.voice == "F4"
    assert compiled.manifest["voice"] == "F4"


@pytest.mark.parametrize(
    ("sound", "expected_tag", "expected_fidelity"),
    [
        ("laugh", "<laugh>", Fidelity.DIRECT.value),
        ("sigh", "<sigh>", Fidelity.DIRECT.value),
        ("chuckle", "<laugh>", Fidelity.APPROXIMATED.value),
        ("sniffle", "<breath>", Fidelity.APPROXIMATED.value),
        ("cry", "<sad>", Fidelity.APPROXIMATED.value),
    ],
)
def test_sound_controls_compile_with_explicit_fidelity(
    sound: str, expected_tag: str, expected_fidelity: str
) -> None:
    compiled = compile_nastechml(f'<speak><sound type="{sound}" /></speak>', _settings())

    assert compiled.text == expected_tag
    assert compiled.manifest["decisions"][0]["fidelity"] == expected_fidelity


@pytest.mark.parametrize(
    ("emotion", "expected_tag", "expected_fidelity"),
    [
        ("calm", "<breath>", Fidelity.APPROXIMATED.value),
        ("happy", None, Fidelity.APPROXIMATED.value),
        ("disgusted", None, Fidelity.UNAVAILABLE.value),
    ],
)
def test_emotion_controls_preserve_honest_fidelity(
    emotion: str, expected_tag: str | None, expected_fidelity: str
) -> None:
    compiled = compile_nastechml(
        f'<speak><emotion name="{emotion}">A line.</emotion></speak>', _settings()
    )

    decision = compiled.manifest["decisions"][0]
    assert decision["fidelity"] == expected_fidelity
    assert decision["compiled_controls"] == ([expected_tag] if expected_tag else [])
