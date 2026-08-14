"""Evaluation helpers for Nastech behavior-control test suites."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .markup import parse_nastechml
from .model import NASTECH_ORPHEUS_V1, NastechModelSpec
from .types import Fidelity, SpanKind


@dataclass(frozen=True)
class EvaluationCaseResult:
    case_id: str
    expected_fidelity: str
    observed_fidelity: str
    passed: bool


def predicted_fidelity(markup: str, model: NastechModelSpec = NASTECH_ORPHEUS_V1) -> Fidelity:
    """Return the lowest expected fidelity for a document before expensive audio synthesis."""
    _, spans = parse_nastechml(markup)
    lowest = Fidelity.DIRECT
    for span in spans:
        if span.kind is SpanKind.SOUND and str(span.value) not in model.direct_sounds:
            return Fidelity.UNAVAILABLE
        if (
            span.kind is SpanKind.SPEECH
            and span.style.emotion
            and span.style.emotion not in model.direct_emotions
        ):
            lowest = Fidelity.APPROXIMATED
    return lowest


def run_behavior_suite(path: str | Path) -> list[EvaluationCaseResult]:
    raw: dict[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))
    results: list[EvaluationCaseResult] = []
    for case in raw.get("cases", []):
        observed = predicted_fidelity(case["markup"]).value
        expected = case["expected_fidelity"]
        results.append(
            EvaluationCaseResult(
                case_id=case["id"],
                expected_fidelity=expected,
                observed_fidelity=observed,
                passed=expected == observed,
            )
        )
    return results
