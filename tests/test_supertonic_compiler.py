from nastech_tts.supertonic import CompactSettings, compile_nastechml


def _settings() -> CompactSettings:
    return CompactSettings(default_voice="F1", cache_dir=None)  # type: ignore[arg-type]


def test_compiles_documented_direct_expression_tags() -> None:
    markup = """
    <speak voice="M1">
      <emotion name="sad">The lantern went dark.</emotion>
      <sound type="sigh" />
      <sound type="laugh" />
    </speak>
    """
    compiled = compile_nastechml(markup, _settings())

    assert "<sad> The lantern went dark." in compiled.text
    assert "<sigh>" in compiled.text
    assert "<laugh>" in compiled.text
    assert compiled.voice == "M1"
    laugh = next(d for d in compiled.manifest["decisions"] if d["requested_behavior"] == "laugh")
    assert laugh["fidelity"] == "direct"


def test_compiles_upstream_surprise_and_nonverbal_tags() -> None:
    compiled = compile_nastechml(
        '<speak><emotion name="surprised">Really?</emotion>'
        '<sound type="scream" /><sound type="throatclear" /></speak>',
        _settings(),
    )

    assert "<surprise> Really?" in compiled.text
    assert "<scream>" in compiled.text
    assert "<throatclear>" in compiled.text
    direct = [
        decision
        for decision in compiled.manifest["decisions"]
        if decision["requested_behavior"] in {"surprised", "scream", "throatclear"}
    ]
    assert all(decision["fidelity"] == "direct" for decision in direct)


def test_marks_cough_and_named_emotion_as_release_dependent() -> None:
    compiled = compile_nastechml(
        '<speak><emotion name="angry">Stop.</emotion><sound type="cough" /></speak>',
        _settings(),
    )

    assert "<angry> Stop." in compiled.text
    assert "<cough>" in compiled.text
    assert compiled.manifest["warnings"]


def test_compiles_speed_from_nastechml_prosody() -> None:
    compiled = compile_nastechml(
        '<speak><prosody rate="fast">Run now.</prosody></speak>', _settings()
    )

    assert compiled.speed == 1.18
