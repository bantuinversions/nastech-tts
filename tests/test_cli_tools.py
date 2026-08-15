import json
import sys

from nastech_tts import cli
from nastech_tts.supertonic import CompactSettings


class CliRuntime:
    def __init__(self) -> None:
        self.settings = CompactSettings(default_voice="F1")

    def status(self):
        return {"provider": "supertonic-local", "loaded": False}

    def clear_audio_cache(self):
        return {"entries_cleared": 2, "bytes_cleared": 12}


def test_validate_command_writes_a_compilation_report(monkeypatch, tmp_path) -> None:
    source = tmp_path / "story.xml"
    report = tmp_path / "report.json"
    source.write_text("<speak>Hello local validation.</speak>", encoding="utf-8")
    monkeypatch.setattr(cli, "SupertonicRuntime", CliRuntime)
    monkeypatch.setattr(
        sys, "argv", ["nastech-tts", "validate", str(source), "--output", str(report)]
    )

    assert cli.main() == 0
    assert json.loads(report.read_text(encoding="utf-8"))["valid"] is True


def test_clear_cache_command_reports_cleared_values(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "SupertonicRuntime", CliRuntime)
    monkeypatch.setattr(sys, "argv", ["nastech-tts", "clear-cache"])

    assert cli.main() == 0
    assert json.loads(capsys.readouterr().out)["bytes_cleared"] == 12


def test_agent_tools_command_publishes_runtime_operations(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "SupertonicRuntime", CliRuntime)
    monkeypatch.setattr(sys, "argv", ["nastech-tts", "agent-tools"])

    assert cli.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert {tool["name"] for tool in payload["tools"]} >= {
        "nastech_compile_speech",
        "nastech_clear_runtime_cache",
    }


def test_plan_command_writes_a_local_agent_execution_plan(monkeypatch, tmp_path) -> None:
    source = tmp_path / "story.xml"
    report = tmp_path / "plan.json"
    source.write_text("<speak><sound type='laugh' /></speak>", encoding="utf-8")
    monkeypatch.setattr(cli, "SupertonicRuntime", CliRuntime)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "nastech-tts",
            "plan",
            str(source),
            "--delivery",
            "chunked-wav",
            "--output",
            str(report),
        ],
    )

    assert cli.main() == 0
    assert json.loads(report.read_text(encoding="utf-8"))["execution"]["delivery"] == "chunked-wav"


def test_clean_command_writes_cleaned_audio_and_report(monkeypatch, tmp_path) -> None:
    import struct
    import wave

    source = tmp_path / "input.wav"
    output = tmp_path / "output.wav"
    report = tmp_path / "cleanup.json"
    with wave.open(str(source), "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(44100)
        writer.writeframes(struct.pack("<4h", 500, 500, 500, 500))
    monkeypatch.setattr(cli, "SupertonicRuntime", CliRuntime)
    monkeypatch.setattr(
        sys,
        "argv",
        ["nastech-tts", "clean", str(source), "--output", str(output), "--report", str(report)],
    )

    assert cli.main() == 0
    assert output.read_bytes().startswith(b"RIFF")
    assert (
        json.loads(report.read_text(encoding="utf-8"))["processor"] == "nastech-local-pcm-cleanup"
    )


def test_platforms_command_reports_portability_profiles(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "SupertonicRuntime", CliRuntime)
    monkeypatch.setattr(sys, "argv", ["nastech-tts", "platforms"])

    assert cli.main() == 0
    assert any(
        profile["id"] == "python-cpu" for profile in json.loads(capsys.readouterr().out)["profiles"]
    )


def test_preflight_command_returns_cuda_validation_plan(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "SupertonicRuntime", CliRuntime)
    monkeypatch.setattr(sys, "argv", ["nastech-tts", "preflight", "python-cuda"])

    assert cli.main() == 0
    assert json.loads(capsys.readouterr().out)["target"]["status"] == "planned"
