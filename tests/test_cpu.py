import pytest

from nastech_tts.cpu import CpuConfigurationError, CpuTuning


def test_balanced_profile_uses_bounded_cpu_defaults(monkeypatch) -> None:
    for key in (
        "NASTECH_CPU_PROFILE",
        "NASTECH_CPU_THREADS",
        "NASTECH_INTRA_OP_THREADS",
        "NASTECH_INTER_OP_THREADS",
        "NASTECH_MAX_PARALLEL_SYNTHESIS",
        "NASTECH_RESERVED_CORES",
        "NASTECH_ALLOW_ALL_CORES",
    ):
        monkeypatch.delenv(key, raising=False)

    tuning = CpuTuning.from_env()

    assert tuning.profile == "balanced"
    assert tuning.inter_op_threads == 1
    assert tuning.max_parallel_synthesis == 1
    assert tuning.reserved_cores == (0 if tuning.logical_cpus == 1 else 1)
    assert tuning.available_cores == tuning.logical_cpus - tuning.reserved_cores
    assert tuning.intra_op_threads is None or tuning.intra_op_threads <= tuning.available_cores
    assert tuning.audio_cache_entries == 32
    assert tuning.audio_cache_mib == 128


def test_explicit_cpu_overrides_take_precedence(monkeypatch) -> None:
    monkeypatch.setenv("NASTECH_CPU_PROFILE", "throughput")
    monkeypatch.setenv("NASTECH_INTRA_OP_THREADS", "3")
    monkeypatch.setenv("NASTECH_INTER_OP_THREADS", "1")
    monkeypatch.setenv("NASTECH_MAX_PARALLEL_SYNTHESIS", "2")

    tuning = CpuTuning.from_env()

    assert tuning.profile == "throughput"
    assert tuning.intra_op_threads == 3
    assert tuning.inter_op_threads == 1
    assert tuning.max_parallel_synthesis == 2


def test_latency_profile_preserves_a_core_and_expands_bounded_ram_cache(monkeypatch) -> None:
    monkeypatch.setenv("NASTECH_CPU_PROFILE", "latency")
    monkeypatch.setenv("NASTECH_RESERVED_CORES", "1")
    monkeypatch.setenv("NASTECH_CPU_THREADS", "999")
    tuning = CpuTuning.from_env()

    assert tuning.max_parallel_synthesis == 1
    assert tuning.reserved_cores == 1
    assert tuning.intra_op_threads == tuning.available_cores
    assert tuning.audio_cache_entries == 64
    assert tuning.audio_cache_mib == 256


def test_all_core_use_requires_explicit_opt_in(monkeypatch) -> None:
    monkeypatch.setenv("NASTECH_ALLOW_ALL_CORES", "true")
    monkeypatch.setenv("NASTECH_CPU_THREADS", "999")
    tuning = CpuTuning.from_env()

    assert tuning.reserved_cores == 0
    assert tuning.available_cores == tuning.logical_cpus
    assert tuning.intra_op_threads == 999


def test_invalid_cpu_profile_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("NASTECH_CPU_PROFILE", "turbo")

    with pytest.raises(CpuConfigurationError, match="NASTECH_CPU_PROFILE"):
        CpuTuning.from_env()
