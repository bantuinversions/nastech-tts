import json
import sys
from types import SimpleNamespace

import pytest

from nastech_tts import cli
from nastech_tts.agent_response import (
    AgentExpressionError,
    agent_expression_capabilities,
    agent_markup,
    available_sounds,
    resolve_emotion,
)
from nastech_tts.supertonic import CompactSettings


class CliRuntime:
    def __init__(self) -> None:
        self.settings = CompactSettings(default_voice="F1")


def test_agent_aliases_map_to_transparent_verified_core_controls() -> None:
    requested, profile, was_alias = resolve_emotion("awe")
    markup, resolution = agent_markup(
        "That is remarkable.",
        voice="siya",
        emotion="joyful",
        sounds=["laughter", "shriek", "throat-clear"],
    )

    assert requested == "awe"
    assert profile.core_emotion == "surprised"
    assert was_alias is True
    assert 'name="happy"' in markup
    assert '<sound type="laugh" />' in markup
    assert '<sound type="scream" />' in markup
    assert '<sound type="throatclear" />' in markup
    assert resolution["emotion_alias_applied"] is True
    assert [item["rendered"] for item in resolution["sounds"]] == [
        "laugh",
        "scream",
        "throatclear",
    ]


def test_agent_expression_contract_lists_core_and_alias_controls() -> None:
    capability = agent_expression_capabilities()

    assert capability["contract"] == "nastech-agent-expression-v1"
    assert set(capability["core_emotions"]) == {
        "neutral",
        "calm",
        "happy",
        "excited",
        "surprised",
        "sad",
        "angry",
        "frustrated",
        "fearful",
        "disgusted",
    }
    assert capability["emotion_aliases"]["joyful"] == "happy"
    assert set(capability["core_sounds"]) <= set(available_sounds())
    assert capability["sound_aliases"]["laughter"] == "laugh"


def test_agent_markup_rejects_unknown_controls() -> None:
    with pytest.raises(AgentExpressionError, match="Unsupported agent emotion"):
        agent_markup("Hello", emotion="telepathic")
    with pytest.raises(AgentExpressionError, match="Unsupported agent sound"):
        agent_markup("Hello", sounds=["applause"])


def test_agent_capabilities_cli_emits_machine_readable_contract(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "SupertonicRuntime", CliRuntime)
    monkeypatch.setattr(sys, "argv", ["nastech-tts", "agent-capabilities"])

    assert cli.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["agent_expression"]["emotion_aliases"]["awe"] == "surprised"
    assert "laugh" in payload["agent_expression"]["core_sounds"]


def test_agent_markup_cli_emits_transparent_expression_report(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "SupertonicRuntime", CliRuntime)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "nastech-tts",
            "agent-markup",
            "The project is ready.",
            "--emotion",
            "triumphant",
            "--sound",
            "laughter",
            "--sound",
            "gasp",
        ],
    )

    assert cli.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["kind"] == "agent_voice_response_plan"
    assert payload["expression"]["rendered_emotion"] == "excited"
    assert [item["rendered"] for item in payload["expression"]["sounds"]] == ["laugh", "gasp"]


def test_agent_speak_cli_writes_wav_manifest_and_machine_report(
    monkeypatch, tmp_path, capsys
) -> None:
    output = tmp_path / "agent-response.wav"
    monkeypatch.setattr(cli, "SupertonicRuntime", CliRuntime)
    monkeypatch.setattr(
        cli,
        "synthesize_with_provider",
        lambda *_args, **_kwargs: SimpleNamespace(data=b"RIFFagentwav", duration_seconds=1.25),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "nastech-tts",
            "agent-speak",
            "I can respond with a local voice.",
            "--output",
            str(output),
            "--emotion",
            "relieved",
            "--sound",
            "sigh",
            "--sound",
            "laugh",
        ],
    )

    assert cli.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert output.read_bytes() == b"RIFFagentwav"
    assert output.with_suffix(".wav.manifest.json").exists()
    assert payload["kind"] == "agent_voice_response"
    assert payload["expression"]["rendered_emotion"] == "calm"
    assert payload["next_action"] == "play_or_attach_local_wav"
