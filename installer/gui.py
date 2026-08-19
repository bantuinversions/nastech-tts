#!/usr/bin/env python3
"""Animated cross-platform Nastech Research installer UI."""

from __future__ import annotations

import argparse
import os
import subprocess
import threading
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import messagebox, ttk

    _TK_AVAILABLE = True
except ImportError:  # Minimal Python builds may omit Tk; the headless launcher remains usable.
    tk = None  # type: ignore[assignment]
    messagebox = None  # type: ignore[assignment]
    ttk = None  # type: ignore[assignment]
    _TK_AVAILABLE = False

from .launcher import VERSION, _data_dir, detect_host, ensure_environment, write_state


class NastechInstaller(tk.Tk if tk is not None else object):
    def __init__(self, source_root: Path, *, repair: bool, reset: bool, command: list[str]) -> None:
        super().__init__()
        self.source_root = source_root.resolve()
        self.repair = repair
        self.reset = reset
        self.command = command or ["platforms"]
        self.title(f"Nastech Research — Nastech TTS {VERSION}")
        self.geometry("620x430")
        self.minsize(620, 430)
        self.configure(bg="#07111f")
        self.resizable(False, False)
        self._phase = 0
        self._running = False
        self._build_ui()
        self.after(120, self._animate)
        self.after(500, self._start_setup)

    def _build_ui(self) -> None:
        header = tk.Frame(self, bg="#07111f")
        header.pack(fill="x", padx=34, pady=(28, 8))
        tk.Label(
            header,
            text="NASTECH RESEARCH",
            fg="#53d8ff",
            bg="#07111f",
            font=("Arial", 13, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header,
            text="Nastech TTS",
            fg="#f5fbff",
            bg="#07111f",
            font=("Arial", 30, "bold"),
        ).pack(anchor="w", pady=(2, 0))
        tk.Label(
            header,
            text="Local-first expressive speech. Configured for your computer.",
            fg="#a9bdd0",
            bg="#07111f",
            font=("Arial", 11),
        ).pack(anchor="w", pady=(4, 0))

        self.canvas = tk.Canvas(self, width=552, height=92, bg="#07111f", highlightthickness=0)
        self.canvas.pack(padx=34, pady=(12, 0))
        self.orb = self.canvas.create_oval(270, 20, 282, 32, fill="#53d8ff", outline="")
        self.ring = self.canvas.create_oval(250, 0, 302, 52, outline="#1c6685", width=2)

        body = tk.Frame(self, bg="#0d1d30")
        body.pack(fill="both", expand=True, padx=34, pady=(8, 26))
        body.pack_propagate(False)
        self.status = tk.Label(
            body, text="Preparing Nastech setup…", fg="#f5fbff", bg="#0d1d30", font=("Arial", 13)
        )
        self.status.pack(anchor="w", padx=22, pady=(22, 10))
        self.detail = tk.Label(
            body, text="", fg="#a9bdd0", bg="#0d1d30", font=("Arial", 10), justify="left"
        )
        self.detail.pack(anchor="w", padx=22, pady=(0, 14))
        self.progress = ttk.Progressbar(body, mode="determinate", maximum=100, length=505)
        self.progress.pack(padx=22, pady=(2, 16))
        self.progress["value"] = 5
        self.footer = tk.Label(
            body,
            text="Optional language packs stay on-demand. No cloud speech proxy is used.",
            fg="#718ca4",
            bg="#0d1d30",
            font=("Arial", 9),
        )
        self.footer.pack(anchor="w", padx=22)

    def _animate(self) -> None:
        self._phase = (self._phase + 1) % 360
        pulse = 22 + (self._phase % 24)
        self.canvas.coords(self.ring, 276 - pulse, 26 - pulse, 276 + pulse, 26 + pulse)
        self.canvas.itemconfigure(self.ring, outline="#1c6685" if self._running else "#24405d")
        self.after(60, self._animate)

    def _set(self, status: str, detail: str, value: int) -> None:
        self.after(0, lambda: self._apply(status, detail, value))

    def _apply(self, status: str, detail: str, value: int) -> None:
        self.status.configure(text=status)
        self.detail.configure(text=detail)
        self.progress["value"] = value

    def _start_setup(self) -> None:
        self._running = True
        threading.Thread(target=self._setup, daemon=True).start()

    def _setup(self) -> None:
        try:
            self._set(
                "Reading your computer",
                "Detecting operating system, CPU, RAM, and graphics acceleration…",
                18,
            )
            host = detect_host()
            state_dir = _data_dir()
            self._set(
                "Optimization selected",
                f"{host['os']} · {host['machine']} · {host['logical_cpus']} CPUs · "
                f"{host['ram_mib'] or 'unknown'} MiB RAM · {host['device']} mode",
                36,
            )
            if self.reset and (state_dir / "venv").exists():
                import shutil

                shutil.rmtree(state_dir / "venv")
            write_state(state_dir, host)
            self._set(
                "Preparing the private environment",
                "Creating or checking the isolated Nastech runtime…",
                54,
            )
            python = ensure_environment(
                self.source_root, state_dir, no_install=False, repair=self.repair
            )
            self._set(
                "Connecting Nastech Agent",
                "Registering the local TTS bridge in your .nastech configuration…",
                78,
            )
            from nastech_tts.agent_integration import connect_to_nastech_home, nastech_home

            agent_config = connect_to_nastech_home(
                nastech_home(), [str(python), "-m", "nastech_tts.cli", "mcp-server"]
            )
            env = os.environ.copy()
            env.update(
                {
                    "NASTECH_DEVICE": host["device"],
                    "NASTECH_CPU_PROFILE": host["cpu_profile"],
                    "NASTECH_MAX_PARALLEL_SYNTHESIS": str(host["max_parallel_synthesis"]),
                }
            )
            self._set(
                "Nastech is ready",
                f"Local TTS bridge connected: {agent_config}. Starting your selected command…",
                94,
            )
            subprocess.Popen([str(python), "-m", "nastech_tts.cli", *self.command], env=env)
            self._set(
                "Installation complete",
                "Nastech TTS is running locally. You may close this window.",
                100,
            )
            self._running = False
        except Exception as exc:  # pragma: no cover - UI error boundary
            self._running = False
            error = str(exc)
            self.after(0, lambda: self._failure(error))

    def _failure(self, error: str) -> None:
        self._apply("Setup needs attention", error, 0)
        messagebox.showerror("Nastech TTS setup", error, parent=self)


def main() -> int:
    parser = argparse.ArgumentParser(description="Animated Nastech TTS installer")
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--repair", action="store_true")
    parser.add_argument("--reset-environment", action="store_true")
    parser.add_argument(
        "--headless", action="store_true", help="Use the CLI launcher instead of opening a window"
    )
    parser.add_argument("--diagnostics", action="store_true", help="Print hardware diagnostics")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    if args.headless or not _TK_AVAILABLE:
        import sys

        from . import launcher

        original_argv = sys.argv
        sys.argv = [original_argv[0], "--source-root", str(args.source_root)]
        if args.repair:
            sys.argv.append("--repair")
        if args.reset_environment:
            sys.argv.append("--reset-environment")
        if args.diagnostics:
            sys.argv.append("--diagnostics")
        sys.argv.extend(command)
        try:
            return launcher.main()
        finally:
            sys.argv = original_argv
    app = NastechInstaller(
        args.source_root,
        repair=args.repair,
        reset=args.reset_environment,
        command=command,
    )
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
