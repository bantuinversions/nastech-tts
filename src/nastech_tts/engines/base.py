"""Common interface for Nastech synthesis adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..types import AudioChunk, AudioSpan, Fidelity


class EngineUnavailableError(RuntimeError):
    """Raised when an optional synthesis engine is not installed or configured."""


class SynthesisEngine(ABC):
    """Backend adapter for one family of TTS capabilities."""

    name: str

    @abstractmethod
    def is_available(self) -> bool:
        """Return whether the backend can be used in the current runtime."""

    @abstractmethod
    def fidelity_for(self, span: AudioSpan) -> Fidelity:
        """State whether the backend can render a span directly or only approximately."""

    @abstractmethod
    def synthesize(self, span: AudioSpan) -> AudioChunk:
        """Render a supported span into mono floating-point audio."""
