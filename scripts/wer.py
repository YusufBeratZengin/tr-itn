#!/usr/bin/env python3
"""Normalize ederek WER ölçümü.

Girdi: satır başına bir JSON nesnesi: {"referans": "...", "hipotez": "..."}

Kullanım::

    python scripts/wer.py ornekler/wer_ornek.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tr_itn.olcum import rapor


def oku(yol: Path) -> list[dict[str, str]]:
    kayitlar = []
    with open(yol, encoding="utf-8") as f:
        for satir in f:
            satir = satir.strip()
            if satir:
                kayitlar.append(json.loads(satir))
    return kayitlar


def main() -> int:
    p = argparse.ArgumentParser(description="ITN öncesi/sonrası WER karşılaştırması")
    p.add_argument("dosya", type=Path)
    args = p.parse_args()
    try:
        kayitlar = oku(args.dosya)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"wer: {args.dosya}: {exc}", file=sys.stderr)
        return 1
    rapor_ = rapor(kayitlar)
    print(f"kayıt        : {rapor_.kayit_sayisi}")
    print(f"WER (ham)    : {rapor_.once:.3f}")
    print(f"WER (ITN)    : {rapor_.sonra:.3f}")
    print(f"fark         : {rapor_.fark:+.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
