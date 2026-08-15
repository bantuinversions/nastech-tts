import io
import struct
import wave

import pytest

from nastech_tts.cleanup import VoiceCleanupError, clean_wav


def _wav(samples: list[int], channels: int = 1, width: int = 2) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as writer:
        writer.setnchannels(channels)
        writer.setsampwidth(width)
        writer.setframerate(44100)
        if width == 2:
            writer.writeframes(struct.pack(f"<{len(samples)}h", *samples))
        else:
            writer.writeframes(bytes(samples))
    return buffer.getvalue()


def test_cleanup_returns_readable_wav_and_audit_report() -> None:
    source = _wav([0, 50, -50, 1200, -1200, 0])

    cleaned = clean_wav(source, noise_gate_dbfs=-40.0, fade_milliseconds=0)

    with wave.open(io.BytesIO(cleaned.data), "rb") as reader:
        assert reader.getnchannels() == 1
        assert reader.getsampwidth() == 2
        assert reader.getframerate() == 44100
        assert reader.getnframes() == 6
    assert cleaned.report["processor"] == "nastech-local-pcm-cleanup"
    assert cleaned.report["noise_gate_samples"] >= 3


def test_cleanup_removes_fixed_dc_offset() -> None:
    cleaned = clean_wav(_wav([2000, 2000, 2000, 2000]), fade_milliseconds=0)

    with wave.open(io.BytesIO(cleaned.data), "rb") as reader:
        frames = reader.readframes(reader.getnframes())
    assert struct.unpack("<4h", frames) == (0, 0, 0, 0)
    assert cleaned.report["dc_offset_removed"] == 2000.0


def test_cleanup_rejects_unsupported_stereo_wav() -> None:
    with pytest.raises(VoiceCleanupError, match="mono 16-bit PCM"):
        clean_wav(_wav([0, 0, 0, 0], channels=2))
