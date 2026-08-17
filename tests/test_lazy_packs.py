from pathlib import Path

import pytest

from nastech_tts.lazy_packs import (
    LazyPackError,
    download_language_pack,
    ensure_pack,
    pack_inventory,
)


def test_pack_inventory_never_downloads_at_startup(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("NASTECH_BANTU_CACHE", str(tmp_path))

    inventory = pack_inventory()

    assert inventory["startup_downloads"] == 0
    assert inventory["startup_loaded_models"] == 0
    assert {item["language"] for item in inventory["packs"]} >= {"sw", "zu"}
    assert not any(tmp_path.iterdir())


def test_missing_pack_requires_explicit_download_permission(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("NASTECH_BANTU_CACHE", str(tmp_path))

    with pytest.raises(LazyPackError, match="explicit pack-download"):
        ensure_pack("sw")


def test_explicit_download_materializes_only_requested_language(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("NASTECH_BANTU_CACHE", str(tmp_path))

    def fake_download(definition, destination):
        destination.mkdir(parents=True)
        (destination / "config.json").write_text("{}", encoding="utf-8")

    monkeypatch.setattr("nastech_tts.lazy_packs._download_pack", fake_download)
    result = download_language_pack("sw")

    assert result["language"] == "sw"
    assert result["downloaded_now"] is True
    assert (tmp_path / "sw" / "config.json").is_file()
    assert not (tmp_path / "rw").exists()


def test_cached_pack_is_reused_without_second_download(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("NASTECH_BANTU_CACHE", str(tmp_path))
    cached = tmp_path / "sw"
    cached.mkdir()
    (cached / "config.json").write_text("{}", encoding="utf-8")

    def fail_download(*args, **kwargs):
        raise AssertionError("cached pack should not download again")

    monkeypatch.setattr("nastech_tts.lazy_packs._download_pack", fail_download)
    assert ensure_pack("sw", allow_download=True) == cached


def test_unmapped_language_is_truthfully_rejected(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("NASTECH_BANTU_CACHE", str(tmp_path))

    with pytest.raises(LazyPackError, match="No verified local model pack"):
        ensure_pack("zu", allow_download=True)
