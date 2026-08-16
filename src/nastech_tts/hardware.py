"""Automatic CPU/GPU hardware detection and memory-aware Nastech runtime planning."""

from __future__ import annotations

import importlib.util
import os
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class HardwareConfigurationError(ValueError):
    """Raised when an explicit hardware mode is invalid or unavailable."""


def _ram_mib() -> int | None:
    try:
        for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("MemTotal:"):
                return int(line.split()[1]) // 1024
    except (OSError, ValueError):
        return None
    return None


def _torch_cuda() -> tuple[bool, str | None, int | None]:
    if importlib.util.find_spec("torch") is None:
        return False, None, None
    try:
        import torch

        if not torch.cuda.is_available():
            return False, None, None
        index = torch.cuda.current_device()
        name = torch.cuda.get_device_name(index)
        vram = int(torch.cuda.get_device_properties(index).total_memory // (1024 * 1024))
        return True, name, vram
    except Exception:  # noqa: BLE001
        return False, None, None


def _onnx_providers() -> tuple[str, ...]:
    if importlib.util.find_spec("onnxruntime") is None:
        return ()
    try:
        import onnxruntime as ort

        return tuple(ort.get_available_providers())
    except Exception:  # noqa: BLE001
        return ()


@dataclass(frozen=True)
class HardwarePlan:
    """Resolved execution device and conservative optimizer settings."""

    requested_device: str
    device: str
    operating_system: str
    logical_cpus: int
    ram_mib: int | None
    gpu_available: bool
    gpu_name: str | None
    gpu_vram_mib: int | None
    onnx_providers: tuple[str, ...]
    accelerator: str
    precision: str
    intra_op_threads: int | None
    inter_op_threads: int | None
    max_parallel_synthesis: int
    recommended_batch_size: int
    reason: str

    @classmethod
    def detect(cls) -> HardwarePlan:
        requested = os.getenv("NASTECH_DEVICE", "auto").strip().lower()
        if requested not in {"auto", "cpu", "gpu", "cuda"}:
            raise HardwareConfigurationError("NASTECH_DEVICE must be auto, cpu, or gpu.")
        logical = os.cpu_count() or 1
        ram = _ram_mib()
        gpu, gpu_name, vram = _torch_cuda()
        providers = _onnx_providers()
        cuda_provider = "CUDAExecutionProvider" in providers
        if requested in {"gpu", "cuda"} and not (gpu and cuda_provider):
            raise HardwareConfigurationError(
                "GPU mode requested but CUDA is unavailable in both the device runtime "
                "and ONNX Runtime."
            )
        use_gpu = requested in {"gpu", "cuda"} or (requested == "auto" and gpu and cuda_provider)
        if use_gpu:
            safe_vram = vram or 4096
            return cls(
                requested_device=requested,
                device="cuda",
                operating_system=platform.system(),
                logical_cpus=logical,
                ram_mib=ram,
                gpu_available=True,
                gpu_name=gpu_name,
                gpu_vram_mib=vram,
                onnx_providers=providers,
                accelerator="CUDAExecutionProvider",
                precision="fp16" if safe_vram >= 4096 else "fp32",
                intra_op_threads=max(1, min(4, logical)),
                inter_op_threads=1,
                max_parallel_synthesis=1,
                recommended_batch_size=max(1, min(8, safe_vram // 2048)),
                reason="CUDA is available and registered with ONNX Runtime.",
            )
        threads = max(1, min(4, logical))
        if ram is not None and ram < 4096:
            threads = max(1, min(2, logical))
        return cls(
            requested_device=requested,
            device="cpu",
            operating_system=platform.system(),
            logical_cpus=logical,
            ram_mib=ram,
            gpu_available=gpu,
            gpu_name=gpu_name,
            gpu_vram_mib=vram,
            onnx_providers=providers,
            accelerator="CPUExecutionProvider",
            precision="fp32",
            intra_op_threads=threads,
            inter_op_threads=1,
            max_parallel_synthesis=1 if ram is None or ram < 8192 else 2,
            recommended_batch_size=1,
            reason="CPU profile selected because CUDA is unavailable or NASTECH_DEVICE=cpu.",
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "requested_device": self.requested_device,
            "device": self.device,
            "operating_system": self.operating_system,
            "logical_cpus": self.logical_cpus,
            "ram_mib": self.ram_mib,
            "gpu_available": self.gpu_available,
            "gpu_name": self.gpu_name,
            "gpu_vram_mib": self.gpu_vram_mib,
            "onnx_providers": list(self.onnx_providers),
            "accelerator": self.accelerator,
            "precision": self.precision,
            "intra_op_threads": self.intra_op_threads,
            "inter_op_threads": self.inter_op_threads,
            "max_parallel_synthesis": self.max_parallel_synthesis,
            "recommended_batch_size": self.recommended_batch_size,
            "optimizer": {
                "thread_policy": "memory-aware bounded threads",
                "request_policy": "bounded parallel synthesis",
                "graph_policy": "ORT_ENABLE_ALL when supported by runtime",
            },
            "reason": self.reason,
        }
