"""The sole Nastech synthesis runtime: an Orpheus-family CPU adapter."""

from __future__ import annotations

import importlib.util

from ..model import NASTECH_ORPHEUS_V1, NastechModelSpec
from ..types import AudioChunk, AudioSpan, Fidelity, SpanKind
from .base import EngineUnavailableError, SynthesisEngine


class NastechOrpheusEngine(SynthesisEngine):
    """Run the selected ready-made Orpheus fine-tune through its CPU-compatible backend."""

    name = "nastech-orpheus"
    model = NASTECH_ORPHEUS_V1

    def __init__(self, model: NastechModelSpec = NASTECH_ORPHEUS_V1) -> None:
        self.model = model
        self._runtime = None

    def is_available(self) -> bool:
        return importlib.util.find_spec("orpheus_cpp") is not None

    def fidelity_for(self, span: AudioSpan) -> Fidelity:
        if span.kind is SpanKind.SOUND:
            return Fidelity.DIRECT if str(span.value) in self.model.direct_sounds else Fidelity.UNAVAILABLE
        if span.kind is SpanKind.SPEECH and span.style.emotion:
            return Fidelity.DIRECT if span.style.emotion in self.model.direct_emotions else Fidelity.APPROXIMATED
        if span.kind is SpanKind.SPEECH:
            return Fidelity.DIRECT
        return Fidelity.UNAVAILABLE

    def synthesize(self, span: AudioSpan) -> AudioChunk:
        if not self.is_available():
            raise EngineUnavailableError(
                "Nastech local runtime is unavailable. Install 'nastech-tts[local]' "
                "with CPU-compatible llama-cpp wheels."
            )
        fidelity = self.fidelity_for(span)
        if fidelity is Fidelity.UNAVAILABLE:
            raise ValueError(f"Nastech base model cannot render this span: {span!r}")

        import numpy as np
        from orpheus_cpp import OrpheusCpp

        if self._runtime is None:
            self._runtime = OrpheusCpp(verbose=False, lang="en")

        prompt = f"<{span.value}>" if span.kind is SpanKind.SOUND else str(span.value)
        options = {"voice_id": span.voice or self.model.default_voice}
        chunks = [chunk for _, chunk in self._runtime.stream_tts_sync(prompt, options=options)]
        if not chunks:
            raise RuntimeError("Nastech base model returned no audio chunks.")
        audio = np.concatenate(chunks, axis=-1).reshape(-1).astype("float32")
        if span.style.volume == "soft":
            audio *= 0.65
        elif span.style.volume == "loud":
            audio *= 1.25
        return AudioChunk(samples=audio, sample_rate=24_000)


# Alias retained for clients of Nastech 0.1; new code should use NastechOrpheusEngine.
OrpheusCppEngine = NastechOrpheusEngine
