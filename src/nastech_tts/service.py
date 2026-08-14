"""Single-model Nastech TTS orchestration."""

from __future__ import annotations

import json
from pathlib import Path

from .engines import EngineUnavailableError, NastechOrpheusEngine
from .markup import parse_nastechml
from .mixer import silence, write_wav
from .model import NASTECH_ORPHEUS_V1, NastechModelSpec
from .types import (
    AudioChunk,
    AudioSpan,
    Fidelity,
    RenderDecision,
    RenderManifest,
    RenderResult,
    SpanKind,
)


class NastechRenderError(RuntimeError):
    """Raised when Nastech's selected model cannot render a requested document."""


class NastechService:
    """Compile NastechML into audio through one adaptable model family only."""

    def __init__(self, model: NastechModelSpec = NASTECH_ORPHEUS_V1) -> None:
        self.model = model
        self.engine = NastechOrpheusEngine(model=model)

    def engine_status(self) -> dict[str, object]:
        return {
            "product_model_id": self.model.product_model_id,
            "upstream_model_id": self.model.upstream_model_id,
            "runtime": self.engine.name,
            "available": self.engine.is_available(),
            "adaptation_method": self.model.adaptation_method,
            "direct_sounds": list(self.model.direct_sounds),
            "direct_emotions": list(self.model.direct_emotions),
        }

    def _reason_for(self, span: AudioSpan, fidelity: Fidelity) -> str:
        if span.kind is SpanKind.SOUND:
            return "The selected Nastech base model directly supports this vocal-sound tag."
        if span.style.emotion and fidelity is Fidelity.APPROXIMATED:
            return (
                "The current ready-made base fine-tune has not yet received a Nastech behavior "
                "adapter for deterministic named emotion control."
            )
        return "Rendered by the selected Nastech base model."

    def render(self, markup: str, output_path: str | Path) -> RenderResult:
        voice, spans = parse_nastechml(markup)
        manifest = RenderManifest(voice=voice)
        chunks: list[AudioChunk] = []

        if not self.engine.is_available():
            raise NastechRenderError(
                "Nastech local runtime is not installed. Install the project with the [local] extra."
            )

        for index, span in enumerate(spans):
            if span.kind is SpanKind.PAUSE:
                chunks.append(silence(int(span.value), 24_000))
                manifest.decisions.append(
                    RenderDecision(
                        span_index=index,
                        engine="nastech-mixer",
                        fidelity=Fidelity.DIRECT,
                        reason="Generated deterministic silence.",
                    )
                )
                continue

            fidelity = self.engine.fidelity_for(span)
            if fidelity is Fidelity.UNAVAILABLE:
                raise NastechRenderError(
                    f"The Nastech base model cannot render '{span.value}' directly. "
                    "Train a Nastech adapter with licensed examples before enabling this behavior."
                )
            try:
                chunks.append(self.engine.synthesize(span))
            except EngineUnavailableError as exc:
                raise NastechRenderError(str(exc)) from exc

            requested_behavior = str(span.value) if span.kind is SpanKind.SOUND else span.style.emotion
            manifest.decisions.append(
                RenderDecision(
                    span_index=index,
                    engine=self.engine.name,
                    fidelity=fidelity,
                    reason=self._reason_for(span, fidelity),
                    requested_behavior=requested_behavior,
                )
            )
            if fidelity is Fidelity.APPROXIMATED:
                manifest.warnings.append(
                    f"Span {index} requested '{requested_behavior}', which requires a trained Nastech adapter "
                    "for deterministic control."
                )

        rendered_path = write_wav(Path(output_path), chunks)
        manifest_path = rendered_path.with_suffix(".manifest.json")
        manifest_payload = manifest.to_dict()
        manifest_payload["model"] = self.model.to_dict()
        manifest_path.write_text(json.dumps(manifest_payload, indent=2) + "\n", encoding="utf-8")
        return RenderResult(audio_path=rendered_path, manifest_path=manifest_path, manifest=manifest)
