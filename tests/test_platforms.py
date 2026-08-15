import pytest

import nastech_tts.platforms as platform_module
from nastech_tts.platforms import PlatformPlanError, host_platform_report, platform_preflight


def test_host_report_exposes_factual_runtime_provider_inventory() -> None:
    report = host_platform_report()

    assert report["host"]["system"]
    assert isinstance(report["onnxruntime"]["registered_execution_providers"], list)
    assert len(report["profiles"]) >= 9


def test_cpu_preflight_is_truthful_about_current_verified_profile() -> None:
    preflight = platform_preflight("python-cpu")

    assert preflight["target"]["status"] == "verified"
    assert preflight["readiness"] in {
        "verified-on-current-host",
        "runtime-installation-incomplete",
    }
    assert "real synthesis" in " ".join(preflight["activation_steps"])


def test_cuda_preflight_does_not_count_cpu_fallback_as_accelerator(monkeypatch) -> None:
    monkeypatch.setattr(
        platform_module, "_available_execution_providers", lambda: ["CPUExecutionProvider"]
    )

    preflight = platform_preflight("python-cuda")

    assert preflight["target"]["status"] == "planned"
    assert preflight["matching_registered_providers"] == []
    assert preflight["registered_fallback_providers"] == ["CPUExecutionProvider"]
    assert preflight["readiness"] == "target-runtime-not-registered-on-current-host"
    assert "does not prove" in preflight["claim_boundary"]


def test_unknown_platform_target_is_rejected_with_available_options() -> None:
    with pytest.raises(PlatformPlanError, match="Unknown platform target"):
        platform_preflight("imaginary-device")
