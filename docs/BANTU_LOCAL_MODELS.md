# Nastech Optional Bantu Local Model Packs

Nastech TTS keeps the compact English core separate from optional multilingual
model packs. A pack is **not downloaded at startup**, is not stored in Git, and
is not included in the 1 GiB compact-core budget. The catalog presents each
choice in a readable form such as **`lg - Luganda`**.

## What “available” means

The following table lists the **35 exact local MMS checkpoint routes** verified
in the official collection and model registry. “Available on demand” does not
mean the pack is already installed on a user's computer, and it does not mean
Nastech makes a native-speaker quality or commercial-use claim. All listed MMS
checkpoints retain the published CC-BY-NC-4.0 boundary. [1] [2]

| Regional area | Available on-demand pack labels |
|---|---|
| East Africa and Great Lakes | `lg - Luganda`, `nyn - Runyankole`, `ach - Acholi`, `teo - Ateso`, `sw - Kiswahili`, `rw - Kinyarwanda`, `rn - Kirundi`, `ki - Gikuyu`, `flr - Fuliiru`, `nyf - Kigiryama`, `myx - Masaaba`, `xog - Lusoga`, `nyo - Runyoro`, `nyy - Nyakyusa-Ngonde`, `hay - Haya`, `heh - Hehe`, `gog - Gogo`, `ruf - Luguru`, `cwe - Kwere`, `ziw - Zigula`, `ksb - Shambala`, `suk - Sukuma` |
| Central Africa | `bem - Bemba`, `bss - Akoose` |
| Southern Africa and adjacent Bantu-speaking communities | `ngl - Lomwe`, `lon - Malawi Lomwe`, `vmw - Makhuwa`, `mgh - Makhuwa-Meetto`, `kde - Makonde`, `yao - Yao`, `seh - Sena`, `toh - Malawi Tonga`, `ts - Xitsonga`, `sn - Shona`, `ny - Chichewa / Nyanja` |

The complete catalog also contains `planned` targets from Kenya, Central Africa,
Angola, South Africa, Botswana, Zimbabwe, Lesotho, and Eswatini. A planned
entry—including `zu - isiZulu`, `xh - isiXhosa`, `st - Sesotho`, `tn -
Setswana`, and `ve - Tshivenda`—has no exact verified pack mapping. Nastech
fails closed instead of silently downloading or synthesizing a different
language.

## Lazy on-demand behavior

`GET /v1/languages/packs` and `nastech-tts language-packs` inspect the registry
and local external cache without network access. The returned data includes both
`label` and `display_label`, with the latter always following the `code - Name`
convention. An operator explicitly requests one pack with
`POST /v1/languages/packs/download` or, for example,
`nastech-tts download-language-pack lg`.

The download is resumable through the Hugging Face cache and is written
atomically under `NASTECH_BANTU_CACHE` (default: `~/.cache/nastech-bantu`).
Synthesis through the `mms-lazy` provider loads only the requested language and
evicts the prior MMS model before loading another. `NASTECH_ALLOW_LAZY_DOWNLOAD=1`
permits a request to acquire an uncached selected pack; leaving it unset fails
closed and requires the explicit download operation first.

## Quality boundary

An available checkpoint only establishes an exact, local technical route. A
language requires locally generated native-language fixtures, deterministic WAV
checks, a pronunciation issue log, and competent native-speaker review before
Nastech can call it a verified local voice. Neither English text nor
transliteration may be used to make that claim.

## Hardware behavior

`NASTECH_DEVICE=auto|cpu|gpu` controls the shared hardware planner. In automatic
mode, the runtime uses CUDA only when the required runtime capabilities are
actually present; otherwise it selects CPU float32 inference. One optional model
is kept resident at a time to control RAM. A forced GPU request fails closed
rather than silently falling back to CPU.

## References

[1] [Meta MMS TTS model card](https://huggingface.co/facebook/mms-tts)

[2] [Official MMS TTS supported-language list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

[3] [Transformers MMS documentation](https://huggingface.co/docs/transformers/en/model_doc/mms)
