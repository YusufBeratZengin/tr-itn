"""Testler kurulum yapılmadan da çalışsın diye src/ yolunu ekler."""

from __future__ import annotations

import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
SRC = KOK / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
