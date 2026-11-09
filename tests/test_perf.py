"""1 MB metin işleme süresi (kabul ölçütü 5).

Eşik CI makinelerinde dalgalanmasın diye geniştir; asıl ölçüm
``scripts/bench.py`` ile alınır ve README'de raporlanır.
"""

from __future__ import annotations

import time

from tr_itn import cevir

PARAGRAF = (
    "toplantı iki kasım iki bin yirmi altı saat on dört otuzda başlayacak, "
    "yüzde on sekiz kdv ve yüz elli lira gider var. "
    "üç kilometre yol, yirmi beş derece sıcaklık, iki buçuk kilo yük. "
)


def test_bir_megabayt() -> None:
    metin = (PARAGRAF * (1024 * 1024 // len(PARAGRAF.encode()) + 1))[: 1024 * 1024]
    bas = time.perf_counter()
    cikti = cevir(metin)
    sure = time.perf_counter() - bas
    assert len(cikti) < len(metin)
    assert sure < 60.0, f"1 MB metin {sure:.1f} s sürdü"
    print(f"\n1 MB: {sure:.2f} s")
