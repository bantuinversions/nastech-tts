#!/usr/bin/env python3
"""Nastech Research one-time bootstrap launcher for Linux, macOS, and Windows."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import venv
from pathlib import Path
from typing import Any

APP_NAME = "Nastech TTS"
VERSION = "0.12.2"


def _memory_mib() -> int | None:
    system = platform.system()
    try:
        if system == "Linux":
            for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
                if line.startswith("MemTotal:"):
                    return int(line.split()[1]) // 1024
        if system == "Darwin":
            value = subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True)
            return int(value.strip()) // (1024 * 1024)
        if system == "Windows":
            value = subprocess.check_output(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory",
                ],
                text=True,
            )
            return int(value.strip()) // (1024 * 1024)
    except (OSError, ValueError, subprocess.SubprocessError):
        return None
    return None


def _gpu_report() -> dict[str, Any]:
    nvidia = shutil.which("nvidia-smi")
    if not nvidia:
        return {"available": False, "name": None, "source": None}
    try:
        name = (
            subprocess.check_output(
                [nvidia, "--query-gpu=name", "--format=csv,noheader"], text=True, timeout=8
            )
            .strip()
            .splitlines()[0]
        )
        return {"available": True, "name": name, "source": "nvidia-smi"}
    except (IndexError, OSError, subprocess.SubprocessError):
        return {"available": False, "name": None, "source": "nvidia-smi"}


def detect_host() -> dict[str, Any]:
    ram = _memory_mib()
    cpus = os.cpu_count() or 1
    gpu = _gpu_report()
    if gpu["available"] and (ram is None or ram >= 4096):
        device = "auto"
        profile = "balanced"
    elif ram is not None and ram < 4096:
        device = "cpu"
        profile = "low-memory"
    else:
        device = "cpu"
        profile = "balanced"
    parallel = 1 if ram is None or ram < 8192 else min(2, cpus)
    return {
        "os": platform.system(),
        "os_release": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "logical_cpus": cpus,
        "ram_mib": ram,
        "gpu": gpu,
        "device": device,
        "cpu_profile": profile,
        "max_parallel_synthesis": parallel,
    }


def _data_dir() -> Path:
    if platform.system() == "Windows":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif platform.system() == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "NastechResearch" / "NastechTTS"


def _venv_python(env_dir: Path) -> Path:
    return env_dir / ("Scripts/python.exe" if platform.system() == "Windows" else "bin/python")


def _run(command: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    subprocess.run(command, cwd=cwd, check=True, env=env)


def ensure_environment(
    source_root: Path, state_dir: Path, *, no_install: bool, repair: bool
) -> Path:
    state_dir.mkdir(parents=True, exist_ok=True)
    env_dir = state_dir / "venv"
    python = _venv_python(env_dir)
    if not python.exists():
        if no_install:
            raise RuntimeError(f"Nastech environment is missing: {env_dir}")
        venv.EnvBuilder(with_pip=True, clear=False).create(env_dir)
    marker = state_dir / "installed.version"
    if not no_install and (repair or not marker.exists() or marker.read_text().strip() != VERSION):
        _run([str(python), "-m", "pip", "install", "--upgrade", "pip"])
        _run([str(python), "-m", "pip", "install", "--upgrade", str(source_root)])
        marker.write_text(VERSION + "\n", encoding="utf-8")
    return python


def write_state(state_dir: Path, host: dict[str, Any]) -> Path:
    state_dir.mkdir(parents=True, exist_ok=True)
    state = {"app": APP_NAME, "version": VERSION, "host": host, "optional_packs": "on-demand"}
    path = state_dir / "runtime-profile.json"
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=f"{APP_NAME} self-bootstrapping launcher")
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--no-install", action="store_true", help="Do not create or repair the isolated environment"
    )
    parser.add_argument(
        "--repair",
        action="store_true",
        help="Reinstall package dependencies into the isolated environment",
    )
    parser.add_argument("--diagnostics", action="store_true", help="Print detected host and exit")
    parser.add_argument(
        "--reset-environment",
        action="store_true",
        help="Delete the isolated environment before setup",
    )
    parser.add_argument(
        "command", nargs=argparse.REMAINDER, help="Nastech command, for example: serve or platforms"
    )
    args = parser.parse_args()

    state_dir = _data_dir()
    if args.reset_environment and (state_dir / "venv").exists():
        shutil.rmtree(state_dir / "venv")
    host = detect_host()
    profile_path = write_state(state_dir, host)
    if args.diagnostics:
        print(json.dumps({"profile_path": str(profile_path), **host}, indent=2))
        return 0

    python = ensure_environment(
        args.source_root.resolve(), state_dir, no_install=args.no_install, repair=args.repair
    )
    env = os.environ.copy()
    env.update(
        {
            "NASTECH_DEVICE": host["device"],
            "NASTECH_CPU_PROFILE": host["cpu_profile"],
            "NASTECH_MAX_PARALLEL_SYNTHESIS": str(host["max_parallel_synthesis"]),
        }
    )
    command = args.command or ["platforms"]
    if command and command[0] == "--":
        command = command[1:]
    _run([str(python), "-m", "nastech_tts.cli", *command], env=env)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
