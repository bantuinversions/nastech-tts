"""Benchmark Nastech's ten verified local English base timbres.

The report measures warm synthesis speed, portable process-memory observations,
and deterministic WAV integrity. It does not claim subjective voice preference,
linguistic correctness, or emotional quality, which require human evaluation.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import sys
import threading
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from nastech_tts.audio_levels import validate_release_wav
from nastech_tts.hardware import HardwarePlan
from nastech_tts.supertonic import SupertonicRuntime, compile_nastechml

BASE_TIMBRES = ("F1", "F2", "F3", "F4", "F5", "M1", "M2", "M3", "M4", "M5")
DEFAULT_TEXT = (
    "Nastech Research measures local speech with care. "
    "Every voice should be fast, clear, private, and useful."
)


@dataclass(frozen=True)
class MemoryObservation:
    """One portable process working-set observation."""

    current_mib: float | None
    process_peak_mib: float | None
    source: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _linux_memory() -> MemoryObservation:
    fields: dict[str, int] = {}
    for line in Path("/proc/self/status").read_text(encoding="utf-8").splitlines():
        key, _, value = line.partition(":")
        if key in {"VmRSS", "VmHWM"}:
            fields[key] = int(value.split()[0]) * 1024
    return MemoryObservation(
        current_mib=round(fields.get("VmRSS", 0) / 1024 / 1024, 3) or None,
        process_peak_mib=round(fields.get("VmHWM", 0) / 1024 / 1024, 3) or None,
        source="/proc/self/status (VmRSS/VmHWM)",
    )


def _windows_memory() -> MemoryObservation:
    import ctypes
    from ctypes import wintypes

    class ProcessMemoryCountersEx(ctypes.Structure):
        _fields_ = [
            ("cb", wintypes.DWORD),
            ("PageFaultCount", wintypes.DWORD),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
            ("PrivateUsage", ctypes.c_size_t),
        ]

    counters = ProcessMemoryCountersEx()
    counters.cb = ctypes.sizeof(counters)
    process = ctypes.windll.kernel32.GetCurrentProcess()
    ok = ctypes.windll.psapi.GetProcessMemoryInfo(process, ctypes.byref(counters), counters.cb)
    if not ok:
        return MemoryObservation(None, None, "Windows GetProcessMemoryInfo unavailable")
    return MemoryObservation(
        current_mib=round(counters.WorkingSetSize / 1024 / 1024, 3),
        process_peak_mib=round(counters.PeakWorkingSetSize / 1024 / 1024, 3),
        source="Windows GetProcessMemoryInfo (working set)",
    )


def _posix_peak_memory() -> MemoryObservation:
    import resource

    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # macOS returns bytes; Linux returns KiB. Other POSIX systems are marked explicitly.
    multiplier = 1 if sys.platform == "darwin" else 1024
    return MemoryObservation(
        current_mib=None,
        process_peak_mib=round(peak * multiplier / 1024 / 1024, 3),
        source="resource.getrusage (process peak; current RSS unavailable on this platform)",
    )


def observe_memory() -> MemoryObservation:
    """Read a documented native process-memory signal without extra packages."""

    if sys.platform.startswith("linux") and Path("/proc/self/status").exists():
        return _linux_memory()
    if sys.platform == "win32":
        return _windows_memory()
    return _posix_peak_memory()


class MemorySampler:
    """Collect the largest observable current working set during a synthesis span."""

    def __init__(self, interval_seconds: float = 0.02) -> None:
        self.interval_seconds = interval_seconds
        self._maximum_current_mib: float | None = None
        self._maximum_process_peak_mib: float | None = None
        self._source = "unstarted"
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._sample, daemon=True)

    def _sample(self) -> None:
        while not self._stop.is_set():
            observed = observe_memory()
            self._source = observed.source
            if observed.current_mib is not None:
                self._maximum_current_mib = max(
                    self._maximum_current_mib or observed.current_mib,
                    observed.current_mib,
                )
            if observed.process_peak_mib is not None:
                self._maximum_process_peak_mib = max(
                    self._maximum_process_peak_mib or observed.process_peak_mib,
                    observed.process_peak_mib,
                )
            self._stop.wait(self.interval_seconds)

    def __enter__(self) -> MemorySampler:
        self._thread.start()
        return self

    def __exit__(self, *_: object) -> None:
        self._stop.set()
        self._thread.join(timeout=1)

    def as_dict(self) -> dict[str, Any]:
        return {
            "peak_sampled_current_mib": self._maximum_current_mib,
            "peak_observed_process_mib": self._maximum_process_peak_mib,
            "source": self._source,
        }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="Destination JSON report.")
    parser.add_argument(
        "--runs", type=int, default=3, help="Warm runs per base timbre (default: 3)."
    )
    parser.add_argument(
        "--text", default=DEFAULT_TEXT, help="Fixed plain-English benchmark text for every timbre."
    )
    parser.add_argument(
        "--voices",
        default=",".join(BASE_TIMBRES),
        help="Comma-separated base timbres to benchmark; default is all ten.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the benchmark plan without loading a model.",
    )
    return parser.parse_args()


def _selected_base_timbres(raw: str) -> tuple[str, ...]:
    voices = tuple(voice.strip().upper() for voice in raw.split(",") if voice.strip())
    invalid = sorted(set(voices) - set(BASE_TIMBRES))
    if not voices or invalid:
        raise ValueError(
            f"--voices must contain one or more base timbres {BASE_TIMBRES}; invalid: {invalid}"
        )
    return voices


def _fixed_markup(voice: str, text: str) -> str:
    return f'<speak voice="{voice}">{text}</speak>'


def _quality_payload(data: bytes) -> dict[str, Any]:
    return validate_release_wav(data, maximum_duration_seconds=120).as_dict()


def _warm_measurement(runtime: SupertonicRuntime, markup: str) -> tuple[dict[str, Any], bytes]:
    compiled = compile_nastechml(markup, runtime.settings, language="en")
    before = observe_memory()
    started = time.perf_counter()
    with MemorySampler() as sampler:
        audio = runtime.synthesize(compiled, use_cache=False)
    elapsed = time.perf_counter() - started
    after = observe_memory()
    return (
        {
            "elapsed_seconds": round(elapsed, 5),
            "audio_seconds": round(audio.duration_seconds, 5),
            "real_time_factor": round(elapsed / audio.duration_seconds, 5),
            "memory_before": before.as_dict(),
            "memory_after": after.as_dict(),
            "memory_during": sampler.as_dict(),
            "audio_quality": _quality_payload(audio.data),
        },
        audio.data,
    )


def _host_payload() -> dict[str, Any]:
    hardware = HardwarePlan.detect().as_dict()
    return {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "logical_cpus": os.cpu_count(),
        "hardware_plan": hardware,
        "initial_memory": observe_memory().as_dict(),
    }


def benchmark(voices: tuple[str, ...], text: str, runs: int) -> dict[str, Any]:
    """Run one model warm-up and detailed serial measures for every selected base timbre."""

    if not 1 <= runs <= 20:
        raise ValueError("--runs must be between 1 and 20.")
    runtime = SupertonicRuntime()
    warmup_started = time.perf_counter()
    warmup = runtime.warmup()
    warmup_seconds = time.perf_counter() - warmup_started
    results: list[dict[str, Any]] = []
    for voice in voices:
        markup = _fixed_markup(voice, text)
        first_started = time.perf_counter()
        first, _ = _warm_measurement(runtime, markup)
        first_elapsed = time.perf_counter() - first_started
        runs_payload = [_warm_measurement(runtime, markup)[0] for _ in range(runs)]
        elapsed = [item["elapsed_seconds"] for item in runs_payload]
        rtf = [item["real_time_factor"] for item in runs_payload]
        results.append(
            {
                "voice": voice,
                "first_synthesis_seconds": round(first_elapsed, 5),
                "first_measurement": first,
                "warm_runs": runs_payload,
                "warm_summary": {
                    "count": len(runs_payload),
                    "mean_elapsed_seconds": round(statistics.fmean(elapsed), 5),
                    "median_elapsed_seconds": round(statistics.median(elapsed), 5),
                    "best_elapsed_seconds": round(min(elapsed), 5),
                    "mean_real_time_factor": round(statistics.fmean(rtf), 5),
                    "mean_audio_seconds": round(
                        statistics.fmean(item["audio_seconds"] for item in runs_payload), 5
                    ),
                },
            }
        )
    return {
        "benchmark": "nastech-base-timbres-v1",
        "measurement_boundary": {
            "speed": "Serial local synthesis after one model warm-up; audio cache disabled.",
            "memory": (
                "Native process working-set signals vary by operating system; source is recorded "
                "for each observation and results must be compared within a runner class."
            ),
            "audio_quality": (
                "Deterministic WAV format, duration, level, DC-offset, and clipping checks; not a "
                "subjective or linguistic-quality score."
            ),
        },
        "host": _host_payload(),
        "benchmark_text": text,
        "voices": results,
        "model_warmup": {**warmup, "elapsed_seconds": round(warmup_seconds, 5)},
        "runtime_status": runtime.status(),
    }


def main() -> int:
    args = _parse_args()
    voices = _selected_base_timbres(args.voices)
    if args.runs < 1 or args.runs > 20:
        raise SystemExit("--runs must be between 1 and 20.")
    if args.dry_run:
        payload: dict[str, Any] = {
            "benchmark": "nastech-base-timbres-v1",
            "host": _host_payload(),
            "voices": list(voices),
            "runs": args.runs,
            "status": "planned-no-model-load",
        }
    else:
        payload = benchmark(voices, args.text, args.runs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
