import io
import math
import struct
import wave

import pytest

from nastech_tts.audio_levels import AudioLevelError, analyze_wav_levels, validate_release_wav
from nastech_tts.cleanup import clean_wav


def _wav(
    samples: list[int], *, channels: int = 1, sample_rate_hz: int = 44100, width: int = 2
) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as writer:
        writer.setnchannels(channels)
        writer.setsampwidth(width)
        writer.setframerate(sample_rate_hz)
        if width == 2:
            writer.writeframes(struct.pack(f"<{len(samples)}h", *samples))
        else:
            writer.writeframes(bytes(samples))
    return buffer.getvalue()


def _half_second_tone(*, dc_offset: int = 0, amplitude: int = 12000) -> list[int]:
    return [
        int(dc_offset + amplitude * math.sin(2 * math.pi * 440 * sample / 44100))
        for sample in range(44100 // 2)
    ]


def test_analyze_wav_levels_reports_pcm_format_and_measurements() -> None:
    report = analyze_wav_levels(_wav([-1000, 0, 1000, 0]))

    assert report.channels == 1
    assert report.sample_width_bytes == 2
    assert report.sample_rate_hz == 44100
    assert report.frames == 4
    assert report.duration_seconds == pytest.approx(4 / 44100)
    assert report.peak_pcm == 1000
    assert report.peak_dbfs is not None
    assert report.rms_dbfs is not None
    assert report.clipped_samples == 0


def test_release_gate_accepts_cleaned_audio_with_valid_levels() -> None:
    source = _wav(_half_second_tone(dc_offset=750))
    cleaned = clean_wav(source, fade_milliseconds=0)

    report = validate_release_wav(cleaned.data)

    assert report.sample_rate_hz == 44100
    assert report.channels == 1
    assert report.duration_seconds == pytest.approx(0.5)
    assert report.peak_dbfs is not None and report.peak_dbfs <= -0.1
    assert report.rms_dbfs is not None and report.rms_dbfs >= -60.0
    assert abs(report.dc_offset_pcm) <= 1.0
    assert report.clipped_samples == 0


def test_release_gate_rejects_digital_full_scale_clipping() -> None:
    clipped = _wav([32767] * (44100 // 2))

    with pytest.raises(AudioLevelError, match="clipping"):
        validate_release_wav(clipped)


def test_release_gate_rejects_wrong_sample_rate() -> None:
    wrong_rate = _wav(_half_second_tone(), sample_rate_hz=22050)

    with pytest.raises(AudioLevelError, match="Expected 44100 Hz"):
        validate_release_wav(wrong_rate)


def test_level_analysis_rejects_stereo_or_non_pcm16_input() -> None:
    stereo = _wav([100, -100] * 10, channels=2)

    with pytest.raises(AudioLevelError, match="mono 16-bit PCM"):
        analyze_wav_levels(stereo)
