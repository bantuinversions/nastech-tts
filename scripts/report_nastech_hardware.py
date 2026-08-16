from __future__ import annotations

import json

from nastech_tts.hardware import HardwarePlan

print(json.dumps(HardwarePlan.detect().as_dict(), indent=2))
