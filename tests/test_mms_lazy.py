from pathlib import Path

from nastech_tts import mms_lazy


def test_resident_model_cache_keeps_one_language(monkeypatch, tmp_path: Path) -> None:
    loaded = []

    def fake_load(language, path, device):
        model = type("Model", (), {"to": lambda self, target: self})()
        loaded.append((language, path, device))
        return object(), model, device

    monkeypatch.setattr(mms_lazy, "_load_model", fake_load)
    mms_lazy.clear_resident_models()

    mms_lazy._resident_model("sw", str(tmp_path / "sw"), "cpu")
    mms_lazy._resident_model("rw", str(tmp_path / "rw"), "cpu")

    assert loaded == [
        ("sw", str(tmp_path / "sw"), "cpu"),
        ("rw", str(tmp_path / "rw"), "cpu"),
    ]
    assert mms_lazy.resident_languages() == ["rw"]
    assert mms_lazy.clear_resident_models() == {
        "cleared_languages": ["rw"],
        "resident_models": 0,
    }
