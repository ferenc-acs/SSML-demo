# /// script
# dependencies = [
#   "python-dotenv",
# ]
# ///

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from tts_backends import diagnose_linux_piper


def main() -> int:
    piper_binary = os.getenv("PIPER_BINARY", "piper")
    piper_model_path = os.getenv("PIPER_MODEL_PATH", "")
    report = diagnose_linux_piper(piper_binary, piper_model_path)

    print("Linux Audio Check")
    print("=================")
    print(f"Piper binary: {report['piper_binary']}")
    print(f"Piper binary found: {report['piper_found']}")
    print(f"Piper model path: {report['piper_model_path'] or '(not set)'}")
    print(f"Piper model found: {report['model_found']}")
    print(f"Playback tools: {', '.join(report['playback_tools']) or '(none found)'}")
    print(f"ssml2piper available: {report['ssml2piper_available']}")

    if report["ok"]:
        print("Status: OK")
        return 0

    print("Status: NEEDS ATTENTION")
    return 1


if __name__ == "__main__":
    sys.exit(main())
