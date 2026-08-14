import pytest

from nastech_tts.cpu import CpuConfigurationError, CpuTuning


def test_balanced_profile_uses_bounded_cpu_defaults(monkeypatch) -> None:
    for key in (
        "NASTECH_CPU_PROFILE",
        "NASTECH_CPU_THREADS",
        "NASTECH_INTRA_OP_THREADS",
        "NASTECH_INTER_OP_THREADS",
        "NASTECH_MAX_PARALLEL_SYNTHESIS",
    ):
        monkeypatch.delenv(key, raising=False)

    tuning = CpuTuning.from_env()

    assert tuning.profile == "balanced"
    assert tuning.inter_op_threads == 1
    assert tuning.max_parallel_synthesis == 1
    assert tuning.intra_op_threads is None or tuning.intra_op_threads >= 1


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


def test_invalid_cpu_profile_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("NASTECH_CPU_PROFILE", "turbo")

    with pytest.raises(CpuConfigurationError, match="NASTECH_CPU_PROFILE"):
        CpuTuning.from_env()
