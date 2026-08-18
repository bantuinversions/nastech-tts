from __future__ import annotations

import io

import numpy as np
import soundfile as sf

from nastech_tts.supertonic import CompactAudio, CompactSettings, SupertonicRuntime


def _fixture_audio(amplitude: int = 10_000) -> CompactAudio:
    buffer = io.BytesIO()
    sf.write(
        buffer,
        np.full(4410, amplitude, dtype=np.int16),
        44100,
        format="WAV",
        subtype="PCM_16",
    )
    return CompactAudio(data=buffer.getvalue(), content_type="audio/wav", duration_seconds=0.1)


def test_mixed_voice_preserves_voice_emotion_sound_and_volume(monkeypatch) -> None:
    runtime = SupertonicRuntime(settings=CompactSettings(default_voice="F1"))
    monkeypatch.setattr(runtime, "synthesize", lambda compiled, use_cache=False: _fixture_audio())
    markup = """
    <speak voice="F1">
      <prosody volume="soft"><emotion name="calm">Welcome softly.</emotion></prosody>
      <emotion name="angry" intensity="0.9"><speak voice="M2">Stop now!</speak></emotion>
      <sound type="laugh" />
      <speak voice="F3"><sound type="sigh" /></speak>
    </speak>
    """

    audio, manifest = runtime.synthesize_mixed(markup)

    assert audio.sample_rate == 44100
    assert manifest["voice_mode"] == "mixed"
    assert [segment["voice"] for segment in manifest["segments"]] == ["F1", "M2", "F1", "F3"]
    assert manifest["segments"][0]["volume"] == "soft"
    assert manifest["segments"][1]["emotion"] == "angry"
    assert manifest["segments"][2]["sound"] == "laugh"
    assert manifest["segments"][3]["sound"] == "sigh"
    assert audio.duration_seconds == 0.4


def test_mixed_voice_accepts_explicit_rate_and_loud_volume(monkeypatch) -> None:
    runtime = SupertonicRuntime(settings=CompactSettings(default_voice="F1"))
    monkeypatch.setattr(runtime, "synthesize", lambda compiled, use_cache=False: _fixture_audio())

    audio, manifest = runtime.synthesize_mixed(
        '<speak><prosody rate="fast" volume="loud">Project update.</prosody></speak>'
    )

    assert audio.duration_seconds == 0.1
    assert manifest["segments"][0]["rate"] == "fast"
    assert manifest["segments"][0]["volume"] == "loud"
