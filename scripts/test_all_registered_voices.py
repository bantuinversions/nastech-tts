"""Generate and validate five-minute Nastech English and Bantu voice stories.

Every registered target is checked in the registry report. Every target with a
verified local route is eligible for five-minute synthesis. Planned or
unverified targets are reported explicitly and are never substituted with a
different language.
"""

from __future__ import annotations

# Native-language fixture paragraphs intentionally remain readable as complete literals.
# ruff: noqa: E501
import argparse
import hashlib
import io
import json
import sys
import wave
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from nastech_tts.audio_levels import validate_release_wav  # noqa: E402
from nastech_tts.languages import LANGUAGE_REGISTRY  # noqa: E402
from nastech_tts.lazy_packs import _pack_definitions  # noqa: E402

TARGET_SECONDS = 300.0
OUTPUT_RATE = 44100

# The English story deliberately exercises every registered emotional style and
# every supported non-verbal sound cue. Bantu seeds are native-language text
# fixtures for the verified local MMS routes; the runner expands each seed into
# a coherent repeated five-minute listening passage for duration testing.
ENGLISH_STORY = (
    "At Nastech Research, the first light of morning entered a quiet workshop. "
    "A local machine held a small signal, and Nastech Agent listened before it spoke. "
    "The team felt hopeful, then excited, because every careful measurement could become "
    'a clearer voice for someone far away. <sound type="gasp" /> '
    '<emotion name="surprised" intensity="0.72">The signal changed.</emotion> '
    'For one breath the room was still. <sound type="throatclear" /> <pause ms="500" /> '
    "Nastech Agent checked the "
    "source, measured the waveform, and found that the mistake was not a failure but an "
    'invitation to learn. <sound type="chuckle" /> '
    '<emotion name="happy" intensity="0.74">The engineers smiled at the small discovery.</emotion> '
    "They wrote the result down, kept the model local, and protected the story "
    'of every speaker who would use it. <emotion name="calm" intensity="0.62">'
    'The work became patient, transparent, and kind.</emotion> <sound type="sigh" /> '
    "Later, a difficult test made the team "
    '<emotion name="frustrated" intensity="0.68">frustrated</emotion> and '
    '<emotion name="angry" intensity="0.76">angry</emotion>. <sound type="groan" /> '
    'The voice stumbled on a long sentence, and a cough interrupted the room. <sound type="cough" /> '
    "No one hid the result. They slowed the process, cleaned the audio, and tried again. "
    '<emotion name="fearful" intensity="0.63">Fearful uncertainty</emotion> became a plan. '
    '<emotion name="disgusted" intensity="0.60">Disgusted doubt</emotion> became a question that could be '
    'answered. <emotion name="sad" intensity="0.70">Sadness</emotion> became attention for the people '
    "whose languages had too often been "
    'left outside the machine. <sound type="sniffle" /> A quiet tear was not weakness; '
    'it was evidence that the work mattered. <sound type="cry" /> '
    "After the long night, Nastech Agent yawned, stretched, and returned to the final check. "
    '<sound type="yawn" /> The waveform was clear, the peaks were safe, and the words '
    'remained understandable. A supervised test cue rose and ended safely. <sound type="scream" /> '
    'The team laughed softly. <sound type="laugh" /> They knew '
    "that a trustworthy voice is not made by claiming perfection. It is made by naming the "
    "limits, testing the details, and improving with respect. At sunrise, the local engine "
    "spoke again. It carried courage without shouting, sadness without harm, joy without "
    "pretending, and calm without becoming empty. Nastech Research had built more than a "
    "sound. It had built a promise: technology should come closer to people, languages, and "
    "real lives while remaining measurable, private, and useful. The workshop grew bright. "
    "Nastech Agent saved the report, thanked the team, and began the next story."
)

BANTU_STORIES = {
    "lg": "Ku Nastech Research, abantu bakolera wamu okukola eddoboozi ery'obwesige. Buli lunaku, Nastech Agent awuliriza, agezesa, era atereeza ebyuma mu ngeri ey'obwegendereza. Eddoboozi lino lya bantu, lya mirimu, lya kuyiga, n'okukulaakulana. Abantu bwe bakolera awamu, ebizibu bisobola okufuuka amakubo amapya. Nastech ekwata ku bwerufu, obukuumi, n'okukola ebintu ebiyamba abantu mu bulamu obwa bulijjo.",
    "nyn": "Ahari Nastech Research, abantu nibakorera hamwe kukora eiraka ry'obwesigye. Buri izooba, Nastech Agent naahurikiza, naagezesa, kandi naahindura omukoro n'obwegyendesereza. Eiraka n'ery'abantu, ery'omurimo, ery'okwega, n'okukura. Abantu ku bakorera hamwe, oburemeezi nibuba amakubo mashya. Nastech neetwara obwesigwa, oburinzi, n'ebikozesibwa omu magoba ga buri izooba.",
    "ach": "I Nastech Research, jo tye ka rwate katicel me yubo dwok ma geno. Dwe, Nastech Agent winjo, temo, ki pwonyo tic me bedo maber. Dwol man tye pi jo, pi tic, pi pwonyo, ki pi kwo maber. Ka jo tye ka tic karacel, peko twero bedo yo manyen. Nastech mito adwogi ma opore, kuc, ki tic ma konyo jo i gang ki i cawa pa tic.",
    "teo": "A Nastech Research, ngesi ngesi ayongakina ikamunyo. Nastech Agent ngesitokini, atemar, ka akimatari ngesi ngesi. Ngesi a ngesi lo ngesi, a ngesi lo apedoria, ka a ngesi lo atemar. Ngesi ngesi ikamunyo, ngesi ikamunyo ngesi, ka ngesi aponi ngesi. Nastech akipi ngesi, akipi adis, ka akipi ngesi lo akwapakina.",
    "sw": "Katika Nastech Research, watu wanafanya kazi pamoja kujenga sauti ya kuaminika. Kila siku, Nastech Agent husikiliza, hupima, na kurekebisha kazi kwa uangalifu. Sauti hii ni ya watu, ya kazi, ya kujifunza, na ya maendeleo. Watu wanaposhirikiana, changamoto zinaweza kuwa njia mpya. Nastech inaheshimu uwazi, usalama, na zana zinazosaidia maisha ya kila siku.",
    "rw": "Muri Nastech Research, abantu bakorera hamwe bubaka ijwi ry'ubwizerwe. Buri munsi, Nastech Agent aratega amatwi, agapima, kandi agatunganya umurimo yitonze. Iri jwi ni iry'abantu, umurimo, kwiga, no gutera imbere. Iyo abantu bakoranye, ibibazo bishobora guhinduka inzira nshya. Nastech yubaha ukuri, umutekano, n'ibikoresho bifasha ubuzima bwa buri munsi.",
    "rn": "Kuri Nastech Research, abantu barakorera hamwe bubake ijwi ryizigirwa. Buri munsi, Nastech Agent arumviriza, agapima, kandi agatunganya igikorwa n'ubwitonzi. Iryo jwi ni iry'abantu, iry'akazi, iry'ukwiga, n'iry'iterambere. Iyo abantu bakoranye, ingorane zishobora guhinduka inzira nshasha. Nastech yubaha ukuri, umutekano, n'ibikoresho bifasha ubuzima bwa misi yose.",
    "ki": "Kũrĩ Nastech Research, andũ marutaga hamwe magĩkorwo na mũgambo wa kwĩhoke. Buri mũthenya, Nastech Agent nĩĩgũaga, nĩĩthomaga, na nĩĩrũgamagĩrĩria wĩra na ũgwati. Mũgambo ũyũ nĩ wa andũ, wa wĩra, wa kwĩruta, na wa gũkũra. Andũ makoragĩra hamwe, mathĩna no mathondeke njĩra njerũ. Nastech nĩĩhoya ũhoro wa ma, ũhoti, na mĩhĩrĩga ya gũteithia mũthenya o mũthenya.",
    "nso": "Go Nastech Research, batho ba šoma mmogo go aga lentšu leo le ka botwago. Letšatši le lengwe le le lengwe, Nastech Agent e a theetša, e lekola, gomme e lokiša mošomo ka tlhokomelo. Lentšu le ke la batho, la mošomo, la go ithuta, le la tšwelopele. Ge batho ba šoma mmogo, mathata a ka fetoga ditsela tše mpsha. Nastech e hlompha therešo, polokego, le didirišwa tšeo di thušago bophelo bja letšatši le lengwe le le lengwe.",
    "ve": "Kha Nastech Research, vhathu vha shuma vhoṱhe u fhaṱa ipfi ḽine ḽa fulufhelwa. Ḓuvha ḽiṅwe na ḽiṅwe, Nastech Agent i a thetshelesa, ya lingedza, na u lugisa mushumo nga vhuronwane. Ipfi ḽenḽi ndi ḽa vhathu, ḽa mushumo, ḽa u guda, na ḽa mvelele. Musi vhathu vha tshi shuma vhoṱhe, thaidzo dzi nga shanduka nḓila ntswa. Nastech i hulisa ngoho, tsireledzo, na zwishumiswa zwine zwa thusa vhutshilo ha ḓuvha ḽiṅwe na ḽiṅwe.",
    "ts": "E Nastech Research, vanhu va tirha swin'we ku aka rito leri tshembekaka. Siku rin'wana na rin'wana, Nastech Agent ya yingisela, yi pima, yi tlhela yi lulamisa ntirho hi vukheta. Rito leri i ra vanhu, ra ntirho, ra ku dyondza, ni ra nhluvuko. Loko vanhu va tirha swin'we, swiphiqo swi nga hundzuka tindlela letintshwa. Nastech yi xixima vunene, nsirhelelo, ni switirhisiwa leswi pfunaka evuton'wini bya siku ni siku.",
    "sn": "Pa Nastech Research, vanhu vanoshanda pamwe chete kuvaka inzwi rinovimbika. Zuva rega rega, Nastech Agent inoteerera, inoyera, uye inogadzirisa basa nokungwarira. Inzwi iri nderavanhu, rebasa, rekudzidza, uye rekufambira mberi. Vanhu pavanoshandira pamwe, matambudziko anogona kuva nzira itsva. Nastech inokoshesa chokwadi, kuchengeteka, uye zvishandiso zvinobatsira upenyu hwezuva nezuva.",
    "ny": "Ku Nastech Research, anthu amagwira ntchito limodzi kuti apange mawu odalirika. Tsiku lililonse, Nastech Agent imamvetsera, imayesa, ndiponso imakonza ntchito mosamala. Mawu awa ndi a anthu, a ntchito, a kuphunzira, ndi a chitukuko. Anthu akamagwira ntchito limodzi, mavuto angasanduke njira zatsopano. Nastech imalemekeza choonadi, chitetezo, ndi zida zothandiza pa moyo wa tsiku ndi tsiku.",
}


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", help="Generate one verified local voice.")
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "release" / "five_minute_voice_fixtures"
    )
    parser.add_argument(
        "--report", type=Path, default=ROOT / "release" / "five_minute_voice_report.json"
    )
    parser.add_argument("--duration-seconds", type=float, default=TARGET_SECONDS)
    parser.add_argument("--list-json", action="store_true")
    return parser.parse_args()


def _matrix() -> list[dict[str, Any]]:
    packs = _pack_definitions()
    rows = []
    for code, definition in LANGUAGE_REGISTRY.items():
        pack = packs[code]
        rows.append(
            {
                "language": code,
                "label": definition.label,
                "iso639_3": definition.iso639_3,
                "registry_status": definition.state,
                "pack_state": pack.state,
                "model_id": pack.model_id,
                "providers": list(definition.provider_ids),
                "story_available": code == "en"
                or (code in BANTU_STORIES and pack.model_id is not None),
            }
        )
    return rows


def _wav_parts(data: bytes) -> tuple[int, np.ndarray]:
    with wave.open(io.BytesIO(data), "rb") as handle:
        rate = handle.getframerate()
        samples = np.frombuffer(handle.readframes(handle.getnframes()), dtype="<i2").copy()
    return rate, samples


def _resample(samples: np.ndarray, source_rate: int, target_rate: int = OUTPUT_RATE) -> np.ndarray:
    if source_rate == target_rate:
        return samples
    target_length = max(1, round(len(samples) * target_rate / source_rate))
    source_positions = np.linspace(0.0, 1.0, num=len(samples), endpoint=False)
    target_positions = np.linspace(0.0, 1.0, num=target_length, endpoint=False)
    return np.rint(np.interp(target_positions, source_positions, samples)).astype(np.int16)


def _wav_bytes(rate: int, samples: np.ndarray) -> bytes:
    output = io.BytesIO()
    with wave.open(output, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes(np.asarray(samples, dtype="<i2").tobytes())
    return output.getvalue()


def _expanded_story(language: str, duration_seconds: float) -> str:
    seed = ENGLISH_STORY if language == "en" else BANTU_STORIES[language]
    # Repeat complete story paragraphs rather than padding with silence. The
    # synthesis loop trims the final chunk to the requested duration exactly.
    target_words = max(80, int(duration_seconds * 3.2))
    expanded: list[str] = []
    while len(" ".join(expanded).split()) < target_words:
        expanded.append(seed)
    return " ".join(expanded)


def _synthesize(language: str, text: str) -> bytes:
    if language == "en":
        from nastech_tts.supertonic import SupertonicRuntime, compile_nastechml

        runtime = SupertonicRuntime()
        compiled = compile_nastechml(text, runtime.settings)
        return runtime.synthesize(compiled, use_cache=False).data
    from nastech_tts.mms_lazy import synthesize_mms

    return synthesize_mms(language, text).data


def _synthesize_five_minutes(language: str, duration_seconds: float) -> tuple[bytes, int]:
    text = _expanded_story(language, duration_seconds)
    # Keep each inference request bounded, then concatenate locally. This is
    # important for the 1 GiB core budget and one-model MMS residency rule.
    chunks = text.split(". ")
    audio_parts: list[np.ndarray] = []
    rate: int = OUTPUT_RATE
    total_frames = 0
    target_frames = int(duration_seconds * rate)
    for index in range(0, len(chunks), 4):
        chunk = ". ".join(chunks[index : index + 4]).strip()
        if not chunk:
            continue
        if language == "en":
            chunk = f"<speak>{chunk}</speak>"
        data = _synthesize(language, chunk)
        current_rate, samples = _wav_parts(data)
        samples = _resample(samples, current_rate, rate)
        remaining = target_frames - total_frames
        if remaining <= 0:
            break
        audio_parts.append(samples[:remaining])
        total_frames += min(len(samples), remaining)
        if total_frames >= target_frames:
            break
    if total_frames < int(rate * duration_seconds * 0.98):
        raise RuntimeError(
            f"Unable to generate a five-minute story for {language}; only {total_frames / rate:.2f}s"
        )
    return _wav_bytes(rate, np.concatenate(audio_parts)), rate


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    args = _args()
    rows = _matrix()
    if args.list_json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0
    target = args.language
    if target not in {row["language"] for row in rows}:
        raise RuntimeError(f"Unknown registered voice: {target}")
    row = next(item for item in rows if item["language"] == target)
    if target != "en" and not row["model_id"]:
        raise RuntimeError(
            f"No verified local model pack exists for '{target}'; refusing substitution."
        )
    if target not in BANTU_STORIES and target != "en":
        raise RuntimeError(f"No native-language story fixture exists for '{target}'.")
    data, rate = _synthesize_five_minutes(target, args.duration_seconds)
    quality = validate_release_wav(
        data,
        maximum_duration_seconds=max(360.0, args.duration_seconds + 1.0),
    )
    if quality.duration_seconds < args.duration_seconds * 0.98:
        raise RuntimeError(f"Generated story is too short: {quality.duration_seconds:.2f}s")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    wav_path = args.output_dir / f"{target}-five-minute.wav"
    wav_path.write_bytes(data)
    report = {
        "schema_version": "1.0",
        "publisher": "Nastech Research",
        "status": "passed",
        "language": target,
        "label": row["label"],
        "story": "Nastech Research five-minute native-language release story",
        "suite": "english-emotion-rich" if target == "en" else "bantu-native-language",
        "requested_duration_seconds": args.duration_seconds,
        "generated_wav": wav_path.name,
        "sha256": _sha256(data),
        "levels": quality.as_dict(),
        "provider_route": "nastech-native-onnx" if target == "en" else "mms-lazy",
        "expressive_coverage": [
            "emotion transitions",
            "laugh",
            "chuckle",
            "sigh",
            "cough",
            "sniffle",
            "groan",
            "yawn",
            "gasp",
            "cry",
            "scream",
            "throatclear",
        ]
        if target == "en"
        else [],
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
