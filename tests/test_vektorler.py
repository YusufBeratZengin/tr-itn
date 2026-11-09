"""Elle doğrulanmış vektör dosyaları.

Her satır: girdi, beklenen çıktı, kural adı. Olumsuz kontrol dosyasında
beklenen = girdi (hiçbir dönüşüm olmamalı) ve kural "yok".
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tr_itn import acikla, cevir

VEKTORLER = Path(__file__).parent / "vektorler"


def _oku(ad: str) -> list[dict]:
    kayitlar = []
    with open(VEKTORLER / ad, encoding="utf-8") as f:
        for satir in f:
            satir = satir.strip()
            if satir:
                kayitlar.append(json.loads(satir))
    return kayitlar


DOSYALAR = sorted(p.name for p in VEKTORLER.glob("*.jsonl"))


def test_vektor_sayisi_yeterli() -> None:
    toplam = sum(len(_oku(ad)) for ad in DOSYALAR)
    assert toplam >= 300, f"en az 300 vektör gerekli, {toplam} var"


@pytest.mark.parametrize("dosya", DOSYALAR)
def test_vektor_dosyasi(dosya: str) -> None:
    hatalar = []
    for v in _oku(dosya):
        sonuc = cevir(v["girdi"])
        if sonuc != v["beklenen"]:
            hatalar.append(f"{v['id']}: {v['girdi']!r} -> {sonuc!r} (beklenen {v['beklenen']!r})")
    assert not hatalar, "\n".join(hatalar)


@pytest.mark.parametrize("dosya", DOSYALAR)
def test_kural_adi_izde_var(dosya: str) -> None:
    hatalar = []
    for v in _oku(dosya):
        izler = acikla(v["girdi"])
        adlar = {iz.kural for iz in izler}
        if v["kural"] == "yok":
            if izler:
                hatalar.append(f"{v['id']}: beklenmeyen dönüşüm {adlar}")
        elif v["kural"] not in adlar:
            hatalar.append(f"{v['id']}: {v['kural']} izde yok ({adlar})")
    assert not hatalar, "\n".join(hatalar)


def test_olumsuzlarda_yanlis_donusum_yok() -> None:
    for v in _oku("olumsuz.jsonl"):
        assert cevir(v["girdi"]) == v["girdi"], v["id"]
