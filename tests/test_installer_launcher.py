from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from installer.launcher import detect_host, write_state  # noqa: E402


def test_detect_host_returns_optimization_contract() -> None:
    report = detect_host()
    assert report["os"]
    assert report["machine"]
    assert report["logical_cpus"] >= 1
    assert report["device"] in {"auto", "cpu"}
    assert report["cpu_profile"] in {"balanced", "low-memory"}
    assert report["max_parallel_synthesis"] >= 1


def test_write_state_persists_hardware_profile(tmp_path: Path) -> None:
    path = write_state(tmp_path, {"os": "TestOS", "device": "cpu"})
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["app"] == "Nastech TTS"
    assert payload["version"] == "0.12.2"
    assert payload["host"]["device"] == "cpu"
    assert payload["optional_packs"] == "on-demand"
