"""Gidiş-dönüş testi: sayı -> yazı -> sayı.

Kartın 4. kabul ölçütü 10 bin rastgele sayının yazıya çevrilip geri
döndürülmesini ister. `kardinal_sozcuk` bu depodaki referans üreteçtir;
kurulu ise `tr_sayi_yazi` (011) paketi de kullanılabilir.
"""

from __future__ import annotations

import random

import pytest

from tr_itn import cevir
from tr_itn.sayi import kardinal_sozcuk

try:  # pragma: no cover - isteğe bağlı dış paket
    from tr_sayi_yazi import sayiya_cevir as _dis_uretec  # type: ignore[import-not-found]
except Exception:
    _dis_uretec = None


def _uretec(n: int) -> str:
    if _dis_uretec is not None:  # pragma: no cover
        return str(_dis_uretec(n))
    return kardinal_sozcuk(n)


def _ornekler(adet: int = 10_000) -> list[int]:
    rng = random.Random(20261103)
    degerler = []
    for _ in range(adet):
        dilim = rng.choice([10, 100, 1_000, 1_000_000, 1_000_000_000, 10**12])
        degerler.append(rng.randrange(0, dilim))
    return degerler


def test_gidis_donus_10_bin() -> None:
    hatalar = []
    for n in _ornekler(10_000):
        # Çıplak "bir" ve "yüz" güvenli varsayılan gereği dönüştürülmez.
        if n in (1, 100):
            continue
        sozcuk = _uretec(n)
        sonuc = cevir(sozcuk)
        if sonuc != str(n):
            hatalar.append(f"{n}: {sozcuk!r} -> {sonuc!r}")
            if len(hatalar) > 10:
                break
    assert not hatalar, "\n".join(hatalar[:10])


@pytest.mark.parametrize("n", [0, 2, 9, 10, 11, 99, 101, 999, 1000, 1001, 2026, 10**6, 10**9])
def test_gidis_donus_ornekleri(n: int) -> None:
    assert cevir(_uretec(n)) == str(n)


def test_sifir_gidis_donus() -> None:
    assert cevir("sıfır") == "0"
