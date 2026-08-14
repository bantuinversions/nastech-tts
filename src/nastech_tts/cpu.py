"""Portable CPU tuning policies for Nastech Compact local ONNX inference."""

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


@dataclass(frozen=True)
class CpuTuning:
    """Validated ONNX CPU and request-scheduling controls.

    The upstream Supertonic runtime already enables ORT_ENABLE_ALL graph
    optimizations and executes the dependent ONNX stages sequentially. This
    policy supplies thread counts and prevents request-level oversubscription.
    """

    profile: str
    logical_cpus: int
    intra_op_threads: int | None
    inter_op_threads: int | None
    max_parallel_synthesis: int
    queue_timeout_seconds: float
    audio_cache_entries: int
    audio_cache_mib: int

    @classmethod
    def from_env(cls) -> CpuTuning:
        logical_cpus = os.cpu_count() or 1
        profile = os.getenv("NASTECH_CPU_PROFILE", "balanced").strip().lower()
        defaults: dict[str, tuple[int | None, int | None, int]] = {
            # A capped thread count offers a dependable default for the four
            # sequential model stages while keeping capacity for the web server.
            "balanced": (min(4, logical_cpus), 1, 1),
            # Favor the fastest response for a single interactive caller.
            "latency": (logical_cpus, 1, 1),
            # Reserve CPU capacity for two independent queued requests.
            "throughput": (max(1, min(3, logical_cpus // 2)), 1, 2),
            # Delegate ONNX thread selection to the runtime while serializing
            # model use by default for predictable memory and latency behavior.
            "auto": (None, None, 1),
        }
        if profile not in defaults:
            valid = ", ".join(sorted(defaults))
            raise CpuConfigurationError(f"NASTECH_CPU_PROFILE must be one of: {valid}.")

        default_intra, default_inter, default_parallel = defaults[profile]
        # NASTECH_CPU_THREADS is a compact convenience alias. The more precise
        # NASTECH_INTRA_OP_THREADS takes precedence when both are configured.
        intra = _optional_positive_int("NASTECH_INTRA_OP_THREADS")
        if intra is None:
            intra = _optional_positive_int("NASTECH_CPU_THREADS")
        if intra is None:
            intra = default_intra
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
            audio_cache_entries=_positive_int("NASTECH_AUDIO_CACHE_ENTRIES", 8, maximum=128),
            audio_cache_mib=_positive_int("NASTECH_AUDIO_CACHE_MIB", 32, maximum=512),
        )

    def as_dict(self) -> dict[str, int | float | str | None]:
        return {
            "profile": self.profile,
            "logical_cpus": self.logical_cpus,
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
            "graph_optimization": "ORT_ENABLE_ALL (provided by Supertonic)",
            "execution_mode": "sequential (provided by Supertonic)",
        }
