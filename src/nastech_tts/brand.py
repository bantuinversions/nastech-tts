"""Stable Nastech TTS product identity for public interfaces.

Public product copy uses this module rather than a model or dependency name. Required
third-party licensing and dependency disclosures remain in the repository NOTICE.md.
"""

from __future__ import annotations

from typing import Any

PUBLISHER = "Nastech Research"
PRODUCT_NAME = "Nastech TTS"
PRODUCT_SLUG = "nastech-tts"
VOICE_CORE_NAME = "Nastech Voice Core"
PRODUCT_DESCRIPTION = (
    "Nastech TTS is a local-first, expressive multilingual speech platform developed by "
    "Nastech Research."
)
PUBLIC_RUNTIME_DESCRIPTION = (
    "Nastech Voice Core performs bounded local speech synthesis with auditable controls, "
    "hardware-aware execution, and no cloud proxy by default."
)


def product_identity() -> dict[str, Any]:
    """Return public Nastech TTS product identity without model-vendor branding."""
    return {
        "product": PRODUCT_NAME,
        "slug": PRODUCT_SLUG,
        "publisher": PUBLISHER,
        "voice_core": VOICE_CORE_NAME,
        "description": PRODUCT_DESCRIPTION,
        "runtime_boundary": PUBLIC_RUNTIME_DESCRIPTION,
        "attribution_notice": "NOTICE.md",
    }
