"""Portable runtime discovery and platform preflight planning for Nastech.

This module reports registered runtime capabilities without equating provider
registration to successful model execution. A non-CPU target remains planned
until a real Supertonic synthesis acceptance record is attached.
"""

from __future__ import annotations

import platform
from dataclasses import dataclass
from typing import Any


class PlatformPlanError(ValueError):
    """Raised when a client requests an unknown portability target."""


@dataclass(frozen=True)
class PlatformProfile:
    """Declarative platform target with explicit validation conditions."""

    identifier: str
    title: str
    status: str
    execution_providers: tuple[str, ...]
    target_environment: str
    requirements: tuple[str, ...]
    evidence_required: tuple[str, ...]
    claim_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.identifier,
            "title": self.title,
            "status": self.status,
            "execution_providers": list(self.execution_providers),
            "target_environment": self.target_environment,
            "requirements": list(self.requirements),
            "evidence_required": list(self.evidence_required),
            "claim_boundary": self.claim_boundary,
        }


_PROFILES = (
    PlatformProfile(
        identifier="python-cpu",
        title="Python CPU local runtime",
        status="verified",
        execution_providers=("CPUExecutionProvider",),
        target_environment="Linux, macOS, or Windows Python host",
        requirements=("Python 3.10+", "Supertonic ONNX assets", "onnxruntime CPU runtime"),
        evidence_required=("real local synthesis", "WAV validity", "bundle budget check"),
        claim_boundary="The verified Nastech Compact runtime is CPU-first and English-only.",
    ),
    PlatformProfile(
        identifier="python-cuda",
        title="Python NVIDIA CUDA runtime",
        status="planned",
        execution_providers=("CUDAExecutionProvider", "CPUExecutionProvider"),
        target_environment="NVIDIA GPU host with CUDA/cuDNN-compatible ONNX Runtime",
        requirements=(
            "CUDA provider registered in the target runtime",
            "Supertonic graph provider compatibility",
            "explicit provider ordering in local sessions",
        ),
        evidence_required=(
            "real CUDA Supertonic synthesis",
            "provider assignment record",
            "audio/latency/memory acceptance",
        ),
        claim_boundary="Registered CUDA support alone does not prove the model executed on a GPU.",
    ),
    PlatformProfile(
        identifier="python-tensorrt",
        title="Python NVIDIA TensorRT runtime",
        status="planned",
        execution_providers=(
            "TensorrtExecutionProvider",
            "CUDAExecutionProvider",
            "CPUExecutionProvider",
        ),
        target_environment="NVIDIA TensorRT-compatible production host",
        requirements=(
            "TensorRT provider build",
            "supported graph partitions",
            "engine/cache strategy",
        ),
        evidence_required=("real TensorRT synthesis", "output parity", "latency/memory benchmark"),
        claim_boundary=(
            "TensorRT is not claimed until the complete graph and fallback behavior are measured."
        ),
    ),
    PlatformProfile(
        identifier="windows-directml",
        title="Windows DirectML runtime",
        status="planned",
        execution_providers=("DmlExecutionProvider", "CPUExecutionProvider"),
        target_environment="Windows host with DirectML-compatible GPU",
        requirements=("Windows ONNX Runtime DirectML package", "graph/provider compatibility"),
        evidence_required=(
            "real Windows synthesis",
            "provider output record",
            "latency acceptance",
        ),
        claim_boundary="DirectML availability is device and driver dependent.",
    ),
    PlatformProfile(
        identifier="intel-openvino",
        title="Intel OpenVINO runtime",
        status="planned",
        execution_providers=("OpenVINOExecutionProvider", "CPUExecutionProvider"),
        target_environment="Intel CPU/GPU/NPU host",
        requirements=("OpenVINO provider build", "supported model conversion/execution"),
        evidence_required=("real OpenVINO synthesis", "audio parity", "latency/memory benchmark"),
        claim_boundary=(
            "OpenVINO is planned until the Supertonic graph is validated on the target device."
        ),
    ),
    PlatformProfile(
        identifier="android-cpu-xnnpack",
        title="Android CPU/XNNPACK client",
        status="planned",
        execution_providers=("XNNPACKExecutionProvider", "CPUExecutionProvider"),
        target_environment="Android native application",
        requirements=(
            "ONNX Runtime Android package",
            "arm64 model compatibility",
            "device disk/memory budget",
        ),
        evidence_required=(
            "real Android synthesis",
            "APK/AAB size",
            "latency/memory/battery record",
        ),
        claim_boundary="A Python server profile is not an Android application artifact.",
    ),
    PlatformProfile(
        identifier="android-nnapi",
        title="Android NNAPI accelerator client",
        status="planned-device-specific",
        execution_providers=("NnapiExecutionProvider", "CPUExecutionProvider"),
        target_environment="Android 8.1+ device; Android 9+ preferred",
        requirements=(
            "NNAPI provider registration",
            "device/API-level graph compatibility",
            "fallback policy",
        ),
        evidence_required=(
            "real target-device synthesis",
            "partition/fallback inspection",
            "thermal/battery benchmark",
        ),
        claim_boundary="NNAPI may route to CPU, GPU, or NPU and results are device/model specific.",
    ),
    PlatformProfile(
        identifier="ios-coreml",
        title="iOS CoreML client",
        status="planned",
        execution_providers=("CoreMLExecutionProvider", "CPUExecutionProvider"),
        target_environment="Native iOS/macOS application",
        requirements=(
            "iOS ONNX Runtime/CoreML package",
            "CoreML graph compatibility",
            "app bundle budget",
        ),
        evidence_required=(
            "real device synthesis",
            "bundle/memory/latency record",
            "audio acceptance",
        ),
        claim_boundary="CoreML remains planned until a signed native target runs the model.",
    ),
    PlatformProfile(
        identifier="web-webgpu",
        title="Browser WebGPU client",
        status="planned",
        execution_providers=("WebGPUExecutionProvider", "WASMExecutionProvider"),
        target_environment="Modern browser client",
        requirements=(
            "onnxruntime-web build",
            "WebGPU/WASM graph support",
            "browser memory budget",
        ),
        evidence_required=(
            "real browser synthesis",
            "browser/device matrix",
            "download/startup benchmark",
        ),
        claim_boundary="WebGPU support is browser and device dependent.",
    ),
)

_PROFILE_MAP = {profile.identifier: profile for profile in _PROFILES}


def _available_execution_providers() -> list[str]:
    try:
        import onnxruntime as ort

        return list(ort.get_available_providers())
    except (ImportError, AttributeError):
        return []


def host_platform_report() -> dict[str, Any]:
    """Return factual host/runtime details without claiming model-provider execution."""
    providers = _available_execution_providers()
    return {
        "host": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "onnxruntime": {
            "registered_execution_providers": providers,
            "cpu_provider_registered": "CPUExecutionProvider" in providers,
            "non_cpu_provider_registered": any(
                provider != "CPUExecutionProvider" for provider in providers
            ),
        },
        "profiles": [profile.to_dict() for profile in _PROFILES],
    }


def platform_preflight(target: str) -> dict[str, Any]:
    """Return a truth-preserving activation plan for a named target."""
    profile = _PROFILE_MAP.get(target)
    if profile is None:
        available = ", ".join(sorted(_PROFILE_MAP))
        raise PlatformPlanError(f"Unknown platform target '{target}'. Available: {available}.")

    report = host_platform_report()
    registered = set(report["onnxruntime"]["registered_execution_providers"])
    target_providers = [
        provider
        for provider in profile.execution_providers
        if provider != "CPUExecutionProvider" and provider in registered
    ]
    fallback_providers = [
        provider
        for provider in profile.execution_providers
        if provider == "CPUExecutionProvider" and provider in registered
    ]
    if profile.identifier == "python-cpu":
        readiness = (
            "verified-on-current-host" if fallback_providers else "runtime-installation-incomplete"
        )
    elif target_providers:
        readiness = "provider-registered-but-model-validation-required"
    else:
        readiness = "target-runtime-not-registered-on-current-host"

    return {
        "target": profile.to_dict(),
        "host": report["host"],
        "registered_execution_providers": sorted(registered),
        "matching_registered_providers": target_providers,
        "registered_fallback_providers": fallback_providers,
        "readiness": readiness,
        "activation_steps": [
            "Install or package the target-specific ONNX Runtime provider.",
            "Pass the provider priority explicitly into Supertonic ONNX sessions.",
            "Run real synthesis on the target hardware or device.",
            "Record provider use, audio validity, latency, memory, and target package size.",
            "Mark the profile verified only after acceptance evidence is committed.",
        ],
        "claim_boundary": profile.claim_boundary,
    }
