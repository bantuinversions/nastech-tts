"""Truthful local English voice-profile inventory for Nastech TTS.

Nastech Voice Core provides ten verified base timbres (F1-F5 and M1-M5).
Nastech TTS exposes ten requested named base profiles plus thirty delivery
profiles that select one base timbre and a documented default rate. Raw base
style IDs remain accepted as aliases. A profile is not represented as a
separate trained speaker identity.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class EnglishVoiceProfile:
    """A selectable local English voice style with an auditable base timbre."""

    profile_id: str
    label: str
    base_voice: str
    default_speed: float
    kind: str
    description: str


_BASE_VOICES = ("F1", "F2", "F3", "F4", "F5", "M1", "M2", "M3", "M4", "M5")
_NAMED_BASE_PROFILES = (
    ("siya", "Siya", "F1"),
    ("nasi", "Nasi", "F2"),
    ("jafta", "Jafta", "M1"),
    ("della", "Della", "F3"),
    ("axam", "Axam", "M2"),
    ("alicia", "Alicia", "F4"),
    ("shanice", "Shanice", "F5"),
    ("adam", "Adam", "M3"),
    ("shakira", "Shakira", "M4"),
    ("shimah", "Shimah", "M5"),
)
_PROFILE_VARIANTS = (
    ("clear", "Clear", 1.00, "neutral, measured delivery"),
    ("soft", "Soft", 0.90, "slower, gentle delivery"),
    ("dynamic", "Dynamic", 1.10, "faster, energetic delivery"),
)


def _profiles() -> tuple[EnglishVoiceProfile, ...]:
    direct = tuple(
        EnglishVoiceProfile(
            profile_id=profile_id,
            label=label,
            base_voice=voice,
            default_speed=1.0,
            kind="named-base-profile",
            description=(
                f"Named Nastech profile backed by verified Nastech Voice Core timbre {voice}. "
                "The display name is not claimed as a separately trained speaker identity."
            ),
        )
        for profile_id, label, voice in _NAMED_BASE_PROFILES
    )
    variants = tuple(
        EnglishVoiceProfile(
            profile_id=f"en-{voice.lower()}-{suffix}",
            label=f"English {voice} {title}",
            base_voice=voice,
            default_speed=speed,
            kind="delivery-profile",
            description=(
                f"{description.capitalize()} using verified Nastech Voice Core timbre {voice}. "
                "This is a delivery profile, not a distinct trained speaker identity."
            ),
        )
        for voice in _BASE_VOICES
        for suffix, title, speed, description in _PROFILE_VARIANTS
    )
    return direct + variants


ENGLISH_VOICE_PROFILES = _profiles()
_PROFILE_BY_ID = {profile.profile_id.lower(): profile for profile in ENGLISH_VOICE_PROFILES}
_PROFILE_BY_ID.update(
    {
        profile.base_voice.lower(): profile
        for profile in ENGLISH_VOICE_PROFILES
        if profile.kind == "named-base-profile"
    }
)


def resolve_english_voice_profile(voice: str) -> EnglishVoiceProfile | None:
    """Return the profile for a known English voice selector, if one exists."""

    return _PROFILE_BY_ID.get(voice.lower())


def english_voice_inventory() -> list[dict[str, object]]:
    """Return all local English selectors with their exact base-timbre boundary."""

    return [asdict(profile) for profile in ENGLISH_VOICE_PROFILES]


def english_voice_summary() -> dict[str, int]:
    """Return profile/base counts used by CLI, API, and CI contract checks."""

    return {
        "selectable_profiles": len(ENGLISH_VOICE_PROFILES),
        "verified_base_timbres": len(_BASE_VOICES),
        "delivery_profiles": len(ENGLISH_VOICE_PROFILES) - len(_BASE_VOICES),
    }
