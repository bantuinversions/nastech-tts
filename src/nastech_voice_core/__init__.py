"""Nastech Voice Core — Lightning Fast, On-Device TTS.

Nastech Voice Core is a high-performance, on-device text-to-speech system powered by
ONNX Runtime. It delivers state-of-the-art speech synthesis with unprecedented
speed and efficiency.

Nastech Voice Core (default) supports multilingual synthesis across 31 languages:

    en, ko, ja, ar, bg, cs, da, de, el, es, et, fi, fr, hi, hr, hu, id,
    it, lt, lv, nl, pl, pt, ro, ru, sk, sl, sv, tr, uk, vi

For text whose language is unknown or outside this set, pass ``lang="na"``
to fall back to the language-agnostic ``<na>`` token.

Example:
    ```python
    from nastech_voice_core import TTS

    tts = TTS()
    style = tts.get_voice_style("M1")  # 10 built-in voices: M1–M5, F1–F5

    # English — pass an ISO code to opt into language-specific handling
    wav, duration = tts.synthesize("Welcome to Nastech Voice Core!", voice_style=style, lang="en")

    # Korean
    wav_ko, _ = tts.synthesize("안녕하세요!", voice_style=style, lang="ko")

    # Default: `lang=None` resolves to the "na" fallback for Nastech Voice Core,
    # so unknown text just works without picking a code.
    wav_na, _ = tts.synthesize("Some text", voice_style=style)

    tts.save_audio(wav, "output.wav")
    ```
"""

from __future__ import annotations

import logging

from .config import (
    AVAILABLE_LANGUAGES,
    AVAILABLE_MODELS,
    DEFAULT_LANGUAGE,
    DEFAULT_MODEL,
    SUPPORTED_LANGUAGES,
    UNKNOWN_LANGUAGE,
)
from .core import Style, UnicodeProcessor
from .pipeline import TTS

__version__ = "1.3.1"

__all__ = [
    "TTS",
    "Style",
    "UnicodeProcessor",
    "AVAILABLE_LANGUAGES",
    "AVAILABLE_MODELS",
    "DEFAULT_LANGUAGE",
    "DEFAULT_MODEL",
    "SUPPORTED_LANGUAGES",
    "UNKNOWN_LANGUAGE",
    "__version__",
]

# Configure logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
