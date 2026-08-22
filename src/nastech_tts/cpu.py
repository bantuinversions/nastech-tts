"""Portable CPU tuning policies for Nastech TTS local ONNX inference."""

from __future__ import annotations

import os
from dataclasses import dataclass


class CpuConfigurationError(ValueError):
    """Raised when a CPU-tuning environment variable is invalid."""


def _optional_positive_int(name: str) -> int | None:
    value = os.getenv(name)
    if value in {None, "", "auto"}:
        return None
    try:
        parsed = int(value)
    except ValueError as exc:
        raise CpuConfigurationError(f"{name} must be a positive integer or 'auto'.") from exc
    if parsed < 1:
        raise CpuConfigurationError(f"{name} must be at least 1.")
    return parsed


def _positive_int(name: str, default: int, maximum: int | None = None) -> int:
    value = os.getenv(name)
    if value in {None, ""}:
        return default
    try:
        parsed = int(value)
    except ValueError as exc:
        raise CpuConfigurationError(f"{name} must be a positive integer.") from exc
    if parsed < 1:
        raise CpuConfigurationError(f"{name} must be at least 1.")
    if maximum is not None and parsed > maximum:
        raise CpuConfigurationError(f"{name} must not exceed {maximum}.")
    return parsed


def _nonnegative_int(name: str, default: int, maximum: int) -> int:
    value = os.getenv(name)
    if value in {None, ""}:
        return default
    try:
        parsed = int(value)
    except ValueError as exc:
        raise CpuConfigurationError(f"{name} must be a non-negative integer.") from exc
    if parsed < 0 or parsed > maximum:
        raise CpuConfigurationError(f"{name} must be between 0 and {maximum}.")
    return parsed


def _positive_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value in {None, ""}:
        return default
    try:
        parsed = float(value)
    except ValueError as exc:
        raise CpuConfigurationError(f"{name} must be a positive number.") from exc
    if parsed <= 0:
        raise CpuConfigurationError(f"{name} must be greater than 0.")
    return parsed


def _enabled(name: str) -> bool:
    value = os.getenv(name, "").strip().lower()
    if value in {"", "0", "false", "no"}:
        return False
    if value in {"1", "true", "yes"}:
        return True
    raise CpuConfigurationError(f"{name} must be one of: 0, 1, false, true, no, yes.")


@dataclass(frozen=True)
class CpuTuning:
    """Validated ONNX CPU, cache, and request-scheduling controls.

    Nastech Voice Core already enables ORT graph optimisation and sequential model
    execution. This policy reserves CPU capacity for the host by default, serialises
    interactive synthesis, and keeps a bounded in-memory WAV cache for repeat calls.
    """

    profile: str
    logical_cpus: int
    intra_op_threads: int | None
    inter_op_threads: int | None
    max_parallel_synthesis: int
    queue_timeout_seconds: float
    audio_cache_entries: int
    audio_cache_mib: int
    reserved_cores: int = 0
    available_cores: int = 1
    allow_all_cores: bool = False

    @classmethod
    def from_env(cls) -> CpuTuning:
        logical_cpus = os.cpu_count() or 1
        profile = os.getenv("NASTECH_CPU_PROFILE", "balanced").strip().lower()
        if profile not in {"balanced", "latency", "memory", "throughput", "auto"}:
            valid = ", ".join(("auto", "balanced", "latency", "memory", "throughput"))
            raise CpuConfigurationError(f"NASTECH_CPU_PROFILE must be one of: {valid}.")

        allow_all_cores = _enabled("NASTECH_ALLOW_ALL_CORES")
        default_reserved = 0 if logical_cpus == 1 else 1
        reserved_cores = (
            0
            if allow_all_cores
            else _nonnegative_int(
                "NASTECH_RESERVED_CORES", default_reserved, maximum=max(0, logical_cpus - 1)
            )
        )
        available_cores = max(1, logical_cpus - reserved_cores)
        defaults: dict[str, tuple[int | None, int | None, int, int, int]] = {
            # Keep a logical CPU available for OS and web-server work; the compact
            # model stages are sequential, so extra concurrent jobs usually harm latency.
            "balanced": (min(4, available_cores), 1, 1, 32, 128),
            # Interactive route: a larger bounded RAM response cache, still no all-core use.
            "latency": (min(4, available_cores), 1, 1, 64, 256),
            # Prefer repeated-response speed and low contention over maximum cold throughput.
            "memory": (min(2, available_cores), 1, 1, 96, 384),
            # Explicit multi-request mode; each session remains limited to protected cores.
            "throughput": (min(3, available_cores), 1, 2, 16, 64),
            # Delegate ONNX thread selection while retaining a serial request queue.
            "auto": (None, None, 1, 32, 128),
        }
        default_intra, default_inter, default_parallel, default_entries, default_cache_mib = (
            defaults[profile]
        )
        intra = _optional_positive_int("NASTECH_INTRA_OP_THREADS")
        if intra is None:
            intra = _optional_positive_int("NASTECH_CPU_THREADS")
        if intra is None:
            intra = default_intra
        if intra is not None and not allow_all_cores:
            intra = min(intra, available_cores)
        inter = _optional_positive_int("NASTECH_INTER_OP_THREADS")
        if inter is None:
            inter = default_inter

        return cls(
            profile=profile,
            logical_cpus=logical_cpus,
            intra_op_threads=intra,
            inter_op_threads=inter,
            max_parallel_synthesis=_positive_int(
                "NASTECH_MAX_PARALLEL_SYNTHESIS", default_parallel, maximum=32
            ),
            queue_timeout_seconds=_positive_float("NASTECH_QUEUE_TIMEOUT_SECONDS", 120.0),
            audio_cache_entries=_positive_int(
                "NASTECH_AUDIO_CACHE_ENTRIES", default_entries, maximum=256
            ),
            audio_cache_mib=_positive_int(
                "NASTECH_AUDIO_CACHE_MIB", default_cache_mib, maximum=512
            ),
            reserved_cores=reserved_cores,
            available_cores=available_cores,
            allow_all_cores=allow_all_cores,
        )

    def as_dict(self) -> dict[str, int | float | str | bool | None]:
        return {
            "profile": self.profile,
            "logical_cpus": self.logical_cpus,
            "reserved_cores": self.reserved_cores,
            "available_cores": self.available_cores,
            "allow_all_cores": self.allow_all_cores,
            "intra_op_threads": (
                self.intra_op_threads if self.intra_op_threads is not None else "auto"
            ),
            "inter_op_threads": (
                self.inter_op_threads if self.inter_op_threads is not None else "auto"
            ),
            "max_parallel_synthesis": self.max_parallel_synthesis,
            "queue_timeout_seconds": self.queue_timeout_seconds,
            "audio_cache_entries": self.audio_cache_entries,
            "audio_cache_mib": self.audio_cache_mib,
            "cache_policy": "bounded in-memory WAV LRU for identical local requests",
            "graph_optimization": "ORT_ENABLE_ALL (provided by Nastech Voice Core)",
            "execution_mode": "sequential (provided by Nastech Voice Core)",
        }
