from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "benchmark_base_timbres.py"


def _benchmark_module():
    spec = importlib.util.spec_from_file_location("base_timbre_benchmark", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_all_ten_base_timbres_are_the_default_matrix() -> None:
    benchmark = _benchmark_module()
    assert (
        benchmark._selected_base_timbres(",".join(benchmark.BASE_TIMBRES)) == benchmark.BASE_TIMBRES
    )


def test_timbre_selection_rejects_unknown_styles() -> None:
    benchmark = _benchmark_module()
    with pytest.raises(ValueError, match="invalid"):
        benchmark._selected_base_timbres("F1,unknown")


def test_fixed_benchmark_markup_varies_only_by_requested_base_timbre() -> None:
    benchmark = _benchmark_module()
    text = "A fixed local benchmark sentence."
    assert (
        benchmark._fixed_markup("F1", text)
        == '<speak voice="F1">A fixed local benchmark sentence.</speak>'
    )
    assert (
        benchmark._fixed_markup("M5", text)
        == '<speak voice="M5">A fixed local benchmark sentence.</speak>'
    )


def test_portable_memory_observation_has_a_documented_source() -> None:
    benchmark = _benchmark_module()
    observed = benchmark.observe_memory().as_dict()
    assert observed["source"]
    assert "mib" in " ".join(observed)
