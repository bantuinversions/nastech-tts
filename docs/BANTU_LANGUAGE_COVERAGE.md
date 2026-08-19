# Nastech TTS Bantu Language Coverage

**Nastech Research** maintains this catalog so people can choose a language
unambiguously. Every selection is shown in code-first form, such as **`lg -
Luganda`**. The registry covers **60 regional African language targets** from
East Africa through Central and Southern Africa, plus the English core. It is a
truthful route registry: a language target is not presented as a verified voice
until the exact local checkpoint, digital-audio checks, and native-language
review have been completed.

> **Important distinction:** `lazy-downloadable` means that an exact local MMS
> checkpoint was confirmed and can be downloaded only when selected. It is not
> a claim that Nastech has completed a native-speaker naturalness, dialect, or
> intelligibility review for that language. `planned` means Nastech will not
> substitute a neighbouring language or a different model under that name.

## How to select a language

Use the short code in the API, CLI, installer, or language-pack view. The
inventory now returns both `label` and `display_label`; the latter is the
human-facing form.

| Example | Meaning |
|---|---|
| `lg - Luganda` | Select with `lg`, `lug`, or `Luganda`. The exact MMS pack is optional and local. |
| `sw - Kiswahili` | Select with `sw`, `swa`, `swahili`, or `Kiswahili`. The exact MMS pack is optional and local. |
| `zu - isiZulu` | A named target, currently planned. Nastech will report it as unavailable instead of speaking another language. |

## Local lazy-download routes

The following **35** routes have exact, public MMS TTS checkpoint identifiers.
They stay outside the compact core and are downloaded only after an explicit
request. The source model family describes its checkpoints as non-commercial
under CC-BY-NC-4.0; deployment therefore requires a compatible use case and
licence review. [1] [2]

| Regional coverage | Selectable language labels with an exact local route |
|---|---|
| East Africa and Great Lakes | `lg - Luganda`, `nyn - Runyankole`, `ach - Acholi`, `teo - Ateso`, `sw - Kiswahili`, `rw - Kinyarwanda`, `rn - Kirundi`, `ki - Gikuyu`, `flr - Fuliiru`, `nyf - Kigiryama`, `myx - Masaaba`, `xog - Lusoga`, `nyo - Runyoro`, `nyy - Nyakyusa-Ngonde`, `hay - Haya`, `heh - Hehe`, `gog - Gogo`, `ruf - Luguru`, `cwe - Kwere`, `ziw - Zigula`, `ksb - Shambala`, `suk - Sukuma` |
| Central Africa | `bem - Bemba`, `bss - Akoose` |
| Southern Africa and adjacent Bantu-speaking communities | `ngl - Lomwe`, `lon - Malawi Lomwe`, `vmw - Makhuwa`, `mgh - Makhuwa-Meetto`, `kde - Makonde`, `yao - Yao`, `seh - Sena`, `toh - Malawi Tonga`, `ts - Xitsonga`, `sn - Shona`, `ny - Chichewa / Nyanja` |

## Named regional targets without a verified local checkpoint

The following **25** languages are deliberately present in the catalog with a
`planned` state. Their names, regional placement, and stable identifiers are
available to users now, but the system will not create an audio route until an
exact checkpoint passes the Nastech evidence process.

| Regional coverage | Planned selection labels |
|---|---|
| East Africa | `kam - Kamba`, `luy - Luhya`, `luo - Dholuo` |
| Central Africa | `lin - Lingala`, `kon - Kikongo`, `lua - Tshiluba`, `lub - Luba-Katanga`, `dua - Duala`, `ewo - Ewondo`, `fan - Fang`, `kmb - Kimbundu`, `umb - Umbundu`, `cjk - Chokwe`, `lun - Lunda`, `lue - Luvale` |
| Southern Africa | `tum - Tumbuka`, `zu - isiZulu`, `xh - isiXhosa`, `st - Sesotho`, `nso - Sepedi / Northern Sotho`, `tn - Setswana`, `ve - Tshivenda`, `ss - siSwati`, `nd - isiNdebele (Northern)`, `nr - isiNdebele (Southern)` |

## Quality and review boundary

A language route must not be advertised as “pure” or production-ready merely
because a model downloads. Before a claim of verified local synthesis, Nastech
requires a locally generated WAV from native-language text, deterministic WAV
acceptance checks, a documented pronunciation issue log, and competent
native-speaker review. English text, a transliteration, or a language-adjacent
checkpoint cannot satisfy this rule.

## References

[1] [Meta MMS TTS model card](https://huggingface.co/facebook/mms-tts)

[2] [Official MMS TTS supported-language list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

[3] [MMS implementation and checkpoint documentation](https://github.com/facebookresearch/fairseq/blob/main/examples/mms/README.md)
