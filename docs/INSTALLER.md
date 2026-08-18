# Nastech TTS cross-platform installer

Nastech Research provides a source-based, one-time bootstrap installer for Linux, macOS, and Windows. The installer uses the operating system’s Python launcher, creates an isolated Nastech environment, installs the local package and its declared dependencies, detects the host hardware, persists a runtime profile, and then starts the requested Nastech command.

## Quick start

On Linux or macOS, run:

```sh
./installer/install.sh --diagnostics
./installer/install.sh -- platforms
./installer/install.sh -- serve --host 127.0.0.1 --port 8765
```

On Windows PowerShell, run:

```powershell
.\installer\install.ps1 --diagnostics
.\installer\install.ps1 -- platforms
.\installer\install.ps1 -- serve --host 127.0.0.1 --port 8765
```

The first non-diagnostic launch creates an isolated environment under the platform’s per-user application-data directory and installs Nastech TTS into it. Later launches reuse that environment. Use `--repair` when dependencies need to be reinstalled or the package must be refreshed. Use `--reset-environment` to recreate the environment from scratch.

The launcher detects operating system, machine architecture, Python version, logical CPU count, RAM, and NVIDIA availability. It then sets `NASTECH_DEVICE`, `NASTECH_CPU_PROFILE`, and `NASTECH_MAX_PARALLEL_SYNTHESIS` for the child process and writes `runtime-profile.json`. The compact core is installed first; Bantu model packs remain lazy and are downloaded only through an explicit language-pack operation.

The release workflow builds platform-labelled installer bundles for Ubuntu/Linux, macOS, and Windows and uploads them to version-tagged GitHub releases. These are bootstrap bundles rather than opaque native binaries, which keeps the installer auditable and lets the launcher use the correct Python and hardware behavior on the user’s machine.

The installer does not claim that every GPU is supported. Automatic GPU selection is used only where the installed local runtime reports a usable path; otherwise the launcher selects a bounded CPU profile. Users can inspect the selected plan with `platforms` and the persisted profile file.
