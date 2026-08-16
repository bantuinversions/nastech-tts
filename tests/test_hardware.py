from __future__ import annotations

import json

import pytest

from nastech_tts.hardware import HardwareConfigurationError, HardwarePlan


def test_auto_detects_cpu_without_optional_cuda(monkeypatch) -> None:
    monkeypatch.setenv("NASTECH_DEVICE", "auto")
    monkeypatch.setattr("nastech_tts.hardware._torch_cuda", lambda: (False, None, None))
    monkeypatch.setattr("nastech_tts.hardware._onnx_providers", lambda: ("CPUExecutionProvider",))
    monkeypatch.setattr("nastech_tts.hardware._ram_mib", lambda: 4096)
    plan = HardwarePlan.detect()
    assert plan.device == "cpu"
    assert plan.accelerator == "CPUExecutionProvider"
    assert plan.precision == "fp32"
    assert plan.max_parallel_synthesis == 1


def test_gpu_requires_cuda_provider(monkeypatch) -> None:
    monkeypatch.setenv("NASTECH_DEVICE", "gpu")
    monkeypatch.setattr("nastech_tts.hardware._torch_cuda", lambda: (True, "Test GPU", 8192))
    monkeypatch.setattr("nastech_tts.hardware._onnx_providers", lambda: ("CPUExecutionProvider",))
    with pytest.raises(HardwareConfigurationError, match="CUDA is unavailable"):
        HardwarePlan.detect()


def test_gpu_plan_selects_fp16_and_batch_from_vram(monkeypatch) -> None:
    monkeypatch.setenv("NASTECH_DEVICE", "auto")
    monkeypatch.setattr("nastech_tts.hardware._torch_cuda", lambda: (True, "Test GPU", 8192))
    monkeypatch.setattr(
        "nastech_tts.hardware._onnx_providers",
        lambda: ("CUDAExecutionProvider", "CPUExecutionProvider"),
    )
    plan = HardwarePlan.detect()
    assert plan.device == "cuda"
    assert plan.precision == "fp16"
    assert plan.recommended_batch_size == 4
    json.dumps(plan.as_dict())


def test_invalid_device_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("NASTECH_DEVICE", "tpu")
    with pytest.raises(HardwareConfigurationError, match="NASTECH_DEVICE"):
        HardwarePlan.detect()
