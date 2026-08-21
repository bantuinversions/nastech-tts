from __future__ import annotations

import json
import wave
from pathlib import Path

import numpy as np
import pytest

from nastech_tts.cli import main
from nastech_tts.supertonic import CompactSettings, compile_nastechml
from nastech_tts.vocal_events import (
    VocalEventError,
    event_route,
    pack_status,
    render_vocal_event,
    supported_event_sounds,
)


def _reference_wav(path: Path) -> Path:
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(24_000)
        wav_file.writeframes(np.zeros(2400, dtype="<i2").tobytes())
    return path


def test_vocal_event_contract_is_complete_and_truthful() -> None:
    status = pack_status()

    assert set(supported_event_sounds()) == {
        "chuckle",
        "cough",
        "cry",
        "gasp",
        "groan",
        "laugh",
        "scream",
        "sigh",
        "sniffle",
        "throatclear",
        "yawn",
    }
    assert status["startup_downloads"] == 0
    assert status["startup_loaded_models"] == 0
    assert event_route("laugh").event_tag == "[laugh]"
    assert event_route("cry").route == "core-expression-fallback"
    assert event_route("cry").event_tag is None


def test_compiler_records_optional_native_event_route() -> None:
    compiled = compile_nastechml(
        '<speak voice="Siya"><sound type="laugh" /><sound type="cry" /></speak>',
        CompactSettings(default_voice="F1"),
    )
    decisions = compiled.manifest["decisions"]

    assert decisions[0]["optional_vocal_event"]["event_tag"] == "[laugh]"
    assert decisions[0]["optional_vocal_event"]["route"] == "native-event-when-pack-installed"
    assert decisions[1]["optional_vocal_event"]["route"] == "core-expression-fallback"


def test_render_rejects_fallback_and_missing_reference(tmp_path: Path) -> None:
    with pytest.raises(VocalEventError, match="no validated native event route"):
        render_vocal_event("cry", tmp_path / "reference.wav")
    with pytest.raises(VocalEventError, match="not available"):
        render_vocal_event("laugh", tmp_path / "reference.wav")


def test_native_event_render_uses_local_model_contract(monkeypatch, tmp_path: Path) -> None:
    class FakeWaveform:
        def detach(self):
            return self

        def cpu(self):
            return self

        def numpy(self):
            return np.array([[0.0, 0.1, -0.1]], dtype=np.float32)

        def squeeze(self):
            return self.numpy().squeeze()

    class FakeModel:
        sr = 24_000

        def generate(self, text: str, audio_prompt_path: str):
            assert text == "A brief natural vocal reaction [laugh]"
            assert Path(audio_prompt_path).is_file()
            return FakeWaveform()

    monkeypatch.setattr("nastech_tts.vocal_events._device", lambda: "cpu")
    monkeypatch.setattr("nastech_tts.vocal_events._load_model", lambda _: FakeModel())
    data, manifest = render_vocal_event("laugh", _reference_wav(tmp_path / "reference.wav"))

    assert data.startswith(b"RIFF")
    assert manifest["render_route"] == "native-event"
    assert manifest["event_tag"] == "[laugh]"
    assert manifest["device"] == "cpu"


def test_cli_requires_reference_authorization(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "nastech-tts",
            "vocal-event",
            "laugh",
            "--reference-audio",
            str(_reference_wav(tmp_path / "reference.wav")),
            "--output",
            str(tmp_path / "event.wav"),
        ],
    )
    assert main() == 2


def test_cli_writes_native_event_artifacts(monkeypatch, tmp_path: Path) -> None:
    event = tmp_path / "event.wav"
    manifest = tmp_path / "event.manifest.json"
    report = tmp_path / "event.report.json"
    monkeypatch.setattr(
        "nastech_tts.cli.render_vocal_event",
        lambda sound, reference: (
            b"RIFFevent",
            {"render_route": "native-event", "sound": sound, "reference_audio": str(reference)},
        ),
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "nastech-tts",
            "vocal-event",
            "laugh",
            "--reference-audio",
            str(_reference_wav(tmp_path / "reference.wav")),
            "--confirm-reference-authorized",
            "--output",
            str(event),
            "--manifest",
            str(manifest),
            "--report",
            str(report),
        ],
    )

    assert main() == 0
    assert event.read_bytes() == b"RIFFevent"
    assert json.loads(manifest.read_text(encoding="utf-8"))["render_route"] == "native-event"
    assert json.loads(report.read_text(encoding="utf-8"))["sound"] == "laugh"
