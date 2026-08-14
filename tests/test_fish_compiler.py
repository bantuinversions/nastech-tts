from nastech_tts.fish import compile_nastechml


def test_compiles_real_emotions_and_events() -> None:
    markup = """
    <speak voice="demo-voice">
      <emotion name="sad">The sky was empty.</emotion>
      <sound type="sigh" />
      <emotion name="happy">Then the lights returned.</emotion>
      <sound type="laugh" />
    </speak>
    """
    compiled = compile_nastechml(markup, output_format="wav")

    assert "[sad] The sky was empty." in compiled.provider_payload["text"]
    assert "[sigh]" in compiled.provider_payload["text"]
    assert "[delight] Then the lights returned." in compiled.provider_payload["text"]
    assert "[laughing]" in compiled.provider_payload["text"]
    assert compiled.provider_payload["reference_id"] == "demo-voice"
    assert compiled.manifest["warnings"] == []


def test_marks_release_dependent_cough_as_approximated() -> None:
    compiled = compile_nastechml('<speak>Hello <sound type="cough" /> there.</speak>')
    cough_decision = next(
        decision
        for decision in compiled.manifest["decisions"]
        if decision["requested_behavior"] == "cough"
    )

    assert "[cough]" in compiled.provider_payload["text"]
    assert cough_decision["fidelity"] == "approximated"
    assert compiled.manifest["warnings"]


def test_compiles_numeric_prosody_controls() -> None:
    compiled = compile_nastechml(
        '<speak><prosody rate="fast" volume="loud">Move now.</prosody></speak>'
    )

    assert compiled.provider_payload["prosody"]["speed"] == 1.18
    assert compiled.provider_payload["prosody"]["volume"] == 4.0
