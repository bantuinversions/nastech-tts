

## Lazy Bantu registry research

The official Facebook Research MMS documentation states that MMS provides TTS checkpoints for more than 1,100 languages and publishes a machine-readable ISO-code list and per-language generator archives. The documented generator archive contains `G_100000.pth`, `config.json`, and `vocab.txt`; only the generator is needed for inference. MMS code and model weights are CC-BY-NC 4.0, so Nastech must keep these packs external and must not represent them as Apache-2.0 core assets. Source: https://github.com/facebookresearch/fairseq/blob/main/examples/mms/README.md.

The public `facebook/mms-tts-swh` model page confirms the per-language Hugging Face checkpoint pattern, local Transformers/VITS inference path, separate model per language, 36.3M-parameter F32 size for Swahili, and CC-BY-NC-4.0 licence. Source: https://huggingface.co/facebook/mms-tts-swh.

The BantuLanguages Initiative presents a broader Bantu scope of 500+ languages and lists Lingala, Swahili, Kikongo, Tshiluba, Kinyarwanda, Shona, Zulu, Luganda, Sesotho, Xhosa, Chichewa, and Tsonga, but marks most as planned and does not provide a general TTS checkpoint catalogue. It is useful for registry expansion and community/data discovery, not proof that every listed language has a ready local TTS model. Source: https://bantulanguageinitiative.com/.

Design consequence: Nastech should expose a broad registry immediately, but use lazy per-language acquisition. Registry presence means a target is known; `model_available` must be independently verified. Startup must not download or instantiate every language. On first request, the resolver downloads only the requested language pack, verifies its manifest and licence metadata, loads one model, and evicts inactive models under a configurable RAM/cache budget.
