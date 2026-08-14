from pathlib import Path
import json
import sys

import soundfile as sf

if len(sys.argv) != 2:
    raise SystemExit('Usage: python scripts_inspect_output.py path/to/audio.wav')

path = Path(sys.argv[1])
info = sf.info(str(path))
manifest_path = path.with_suffix('.manifest.json')
print(f'audio={path}')
print(f'duration_seconds={info.duration:.2f}')
print(f'sample_rate={info.samplerate}')
print(f'channels={info.channels}')
print(f'file_bytes={path.stat().st_size}')
if manifest_path.exists():
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    print(f'decision_count={len(manifest["decisions"])}')
    print(f'warning_count={len(manifest["warnings"])}')
