from pathlib import Path

import pytest

from nastech_tts.cpu import CpuTuning
from nastech_tts.supertonic import (
    CompactAudio,
    CompactCompiledRequest,
    CompactSettings,
    SupertonicRuntime,
)


def _runtime(entries: int = 3, cache_mib: int = 1) -> SupertonicRuntime:
    return SupertonicRuntime(
        settings=CompactSettings(cache_dir=Path("/tmp/nastech-test-cache")),
        cpu=CpuTuning(
            profile="test",
            logical_cpus=1,
            intra_op_threads=1,
            inter_op_threads=1,
            max_parallel_synthesis=1,
            queue_timeout_seconds=1.0,
            audio_cache_entries=entries,
            audio_cache_mib=cache_mib,
        ),
    )


def _compiled(text: str = "Hello.", voice: str = "F1", speed: float = 1.0, steps: int = 8):
    return CompactCompiledRequest(
        request_id="test-request",
        text=text,
        voice=voice,
        speed=speed,
        steps=steps,
        manifest={},
    )


def _audio(data: bytes = b"wav") -> CompactAudio:
    return CompactAudio(data=data, content_type="audio/wav", duration_seconds=0.1)


@pytest.mark.parametrize(
    "changed_request",
    [
        _compiled(text="Different."),
        _compiled(voice="M1"),
        _compiled(speed=1.2),
        _compiled(steps=10),
    ],
)
def test_cache_key_changes_with_synthesis_controls(changed_request: CompactCompiledRequest) -> None:
    assert SupertonicRuntime._cache_key(_compiled()) != SupertonicRuntime._cache_key(
        changed_request
    )


def test_cached_audio_round_trips_and_records_a_hit() -> None:
    runtime = _runtime()
    key = runtime._cache_key(_compiled())
    expected = _audio(b"first")

    runtime._store_cached_audio(key, expected)

    assert runtime._read_cached_audio(key) == expected
    assert runtime.status()["metrics"]["audio_cache_hits"] == 1


def test_clear_cache_reports_entries_and_bytes() -> None:
    runtime = _runtime()
    runtime._store_cached_audio(runtime._cache_key(_compiled()), _audio(b"12345"))

    result = runtime.clear_audio_cache()

    assert result == {"entries_cleared": 1, "bytes_cleared": 5}
    assert runtime.status()["audio_cache"] == {"entries": 0, "bytes": 0, "mib": 0.0}


def test_cache_uses_lru_eviction_at_entry_limit() -> None:
    runtime = _runtime(entries=1)
    first = runtime._cache_key(_compiled("First."))
    second = runtime._cache_key(_compiled("Second."))

    runtime._store_cached_audio(first, _audio(b"one"))
    runtime._store_cached_audio(second, _audio(b"two"))

    assert runtime._read_cached_audio(first) is None
    assert runtime._read_cached_audio(second) == _audio(b"two")


def test_cache_rejects_audio_larger_than_budget() -> None:
    runtime = _runtime(cache_mib=1)
    oversized = _audio(b"x" * (1024 * 1024 + 1))

    runtime._store_cached_audio(runtime._cache_key(_compiled()), oversized)

    assert runtime.status()["audio_cache"]["entries"] == 0
