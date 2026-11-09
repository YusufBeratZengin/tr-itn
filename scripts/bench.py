#!/usr/bin/env python3
"""1 MB metin üzerinde işlem süresini ölçer.

Kullanım::

    python scripts/bench.py [--boyut 1048576] [--tur 3]
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tr_itn import cevir

PARAGRAF = (
    "toplantı iki kasım iki bin yirmi altı saat on dört otuzda başlayacak, "
    "yüzde on sekiz kdv ve yüz elli lira gider var. "
    "üç kilometre yol, yirmi beş derece sıcaklık, iki buçuk kilo yük. "
    "on iki bin üç yüz kırk beş başvuru, ikinci sırada, saat dokuzda. "
)


def metin_uret(boyut: int) -> str:
    tekrar = boyut // len(PARAGRAF.encode("utf-8")) + 1
    return (PARAGRAF * tekrar)[:boyut]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--boyut", type=int, default=1024 * 1024, help="bayt")
    p.add_argument("--tur", type=int, default=3)
    args = p.parse_args()

    metin = metin_uret(args.boyut)
    bayt = len(metin.encode("utf-8"))
    cevir(metin[:1000])  # ısınma
    sureler = []
    for _ in range(args.tur):
        bas = time.perf_counter()
        cikti = cevir(metin)
        sureler.append(time.perf_counter() - bas)
    en_iyi = min(sureler)
    print(f"girdi      : {bayt / 1024 / 1024:.2f} MiB ({len(metin)} karakter)")
    print(f"çıktı      : {len(cikti)} karakter")
    print(f"süre       : {en_iyi:.2f} s (en iyi / {args.tur} tur)")
    print(f"hız        : {bayt / en_iyi / 1024 / 1024:.2f} MiB/s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
