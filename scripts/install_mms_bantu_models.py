from __future__ import annotations

from pathlib import Path

from huggingface_hub import snapshot_download

MODELS = {
    "lg": "facebook/mms-tts-lug",
    "nyn": "facebook/mms-tts-nyn",
    "ach": "facebook/mms-tts-ach",
    "teo": "facebook/mms-tts-teo",
    "sw": "facebook/mms-tts-swh",
    "rw": "facebook/mms-tts-kin",
    "rn": "facebook/mms-tts-run",
    "ki": "facebook/mms-tts-kik",
    "ts": "facebook/mms-tts-tso",
    "sn": "facebook/mms-tts-sna",
    "ny": "facebook/mms-tts-nya",
}
CACHE = Path("/home/ubuntu/nastech-bantu-models")
for code, model_id in MODELS.items():
    path = snapshot_download(
        repo_id=model_id,
        cache_dir=str(CACHE),
        local_dir=str(CACHE / code),
        local_dir_use_symlinks=False,
        allow_patterns=[
            "config.json",
            "generation_config.json",
            "model.safetensors",
            "pytorch_model.bin",
            "special_tokens_map.json",
            "tokenizer_config.json",
            "vocab.json",
            "preprocessor_config.json",
        ],
    )
    print(code, model_id, path)
