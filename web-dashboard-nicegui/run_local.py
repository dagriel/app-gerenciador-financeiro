from __future__ import annotations

import sys
from pathlib import Path

# Permite rodar sem "pip install -e .", adicionando o src/ ao PYTHONPATH.
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from dashboard_nicegui.main import run  # noqa: E402

if __name__ == "__main__":
    run()
