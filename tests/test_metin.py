"""Parçalama ve sözcük çözümleme testleri."""

from __future__ import annotations

import pytest

from tr_itn.metin import (
    BOSLUK,
    DIGER,
    KELIME,
    ilk_buyuk,
    kelimeler,
    koklar,
    kucult,
    parcala,
)


def test_parcala_tipleri() -> None:
    parcalar = parcala("Saat 14:30'da, tamam mı?")
    tipler = [p.tip for p in parcalar]
    assert KELIME in tipler and BOSLUK in tipler and DIGER in tipler
    assert "".join(p.metin for p in parcalar) == "Saat 14:30'da, tamam mı?"


def test_parcala_konumlar() -> None:
    metin = "iki kasım"
    parcalar = parcala(metin)
    for p in parcalar:
        assert metin[p.bas : p.bas + len(p.metin)] == p.metin


@pytest.mark.parametrize(
    ("girdi", "beklenen"),
    [
        ("İSTANBUL", "istanbul"),
        ("IŞIK", "ışık"),
        ("Kasım", "kasım"),
        ("ÇĞÜÖŞ", "çğüöş"),
    ],
)
def test_kucult(girdi: str, beklenen: str) -> None:
    assert kucult(girdi) == beklenen


@pytest.mark.parametrize(
    ("girdi", "beklenen"),
    [
        ("kasım", "Kasım"),
        ("istanbul", "İstanbul"),
        ("ılık", "Ilık"),
        ("", ""),
        ("3", "3"),
    ],
)
def test_ilk_buyuk(girdi: str, beklenen: str) -> None:
    assert ilk_buyuk(girdi) == beklenen


def test_kelimeler_ek_cozer() -> None:
    ks = kelimeler(parcala("otuzunda"))
    assert ks[0].kok == "otuz"
    assert ks[0].ek == "unda"


def test_kelimeler_tuzak_isaretler() -> None:
    ks = kelimeler(parcala("onun biri"))
    assert ks[0].tuzak and ks[1].tuzak


def test_kelimeler_ascii_duzeltme() -> None:
    ks = kelimeler(parcala("yuzde on sekiz"))
    assert ks[0].kucuk == "yüzde"
    assert ks[0].kok == "yüz"


def test_koklar() -> None:
    ks = kelimeler(parcala("iki kasım"))
    assert koklar(ks) == ["iki", "kasım"]


def test_kelime_ekli_mi() -> None:
    ks = kelimeler(parcala("altıda ve beş"))
    assert ks[0].ekli_mi
    assert not ks[1].ekli_mi


def test_bos_metin() -> None:
    assert kelimeler(parcala("")) == []
