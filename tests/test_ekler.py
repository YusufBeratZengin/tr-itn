"""Ek çözümleme ve ünlü uyumu testleri."""

from __future__ import annotations

import pytest

from tr_itn import sozluk
from tr_itn.ekler import (
    EkCozum,
    ek_cozumle,
    ek_turu,
    ek_uret,
    ekle_yaz,
    ekler,
    sert_mi,
    son_sesli,
    unlu_dortlu,
    unlu_ikili,
)

KOKLER = frozenset(sozluk.SAYI_SOZLERI)


@pytest.mark.parametrize(
    ("kelime", "beklenen"),
    [("altı", "ı"), ("dört", "ö"), ("yüz", "ü"), ("bin", "i"), ("kırk", "ı"), ("tl", None)],
)
def test_son_sesli(kelime: str, beklenen: str | None) -> None:
    assert son_sesli(kelime) == beklenen


@pytest.mark.parametrize(
    ("kelime", "ikili", "dortlu"),
    [("altı", "a", "ı"), ("elli", "e", "i"), ("otuz", "a", "u"), ("dört", "e", "ü")],
)
def test_unlu_uyumu(kelime: str, ikili: str, dortlu: str) -> None:
    assert unlu_ikili(kelime) == ikili
    assert unlu_dortlu(kelime) == dortlu


def test_sert_mi() -> None:
    assert sert_mi("dört")
    assert sert_mi("beş")
    assert not sert_mi("bin")
    assert not sert_mi("")


@pytest.mark.parametrize(
    ("kelime", "kok", "ek"),
    [
        ("altıda", "altı", "da"),
        ("dörtte", "dört", "te"),
        ("otuzunda", "otuz", "unda"),
        ("binde", "bin", "de"),
        ("yüzünde", "yüz", "ünde"),
        ("altıya", "altı", "ya"),
        ("beşi", "beş", "i"),
        ("ikimiz", "iki", "miz"),
        ("üçümüz", "üç", "ümüz"),
        ("yirmi", "yirmi", ""),
    ],
)
def test_ek_cozumle(kelime: str, kok: str, ek: str) -> None:
    assert ek_cozumle(kelime, KOKLER) == EkCozum(kok, ek)


@pytest.mark.parametrize(
    "kelime",
    [
        "",
        "altında",   # alt + ında (alt madeni)
        "altına",    # alt + ına
        "altın",
        "binlerce",
        "ikinci",    # sıra sayısı, kardinal kök değil
        "merhaba",
        "yüzlerce",
        "biner",
    ],
)
def test_ek_cozumle_yok(kelime: str) -> None:
    assert ek_cozumle(kelime, KOKLER) is None


def test_ekler_onbellek() -> None:
    assert "da" in ekler("altı")
    assert ekler("altı") is ekler("altı")


def test_ek_turu_ve_uret() -> None:
    assert ek_turu("lira", "ya") == "dat"
    assert ek_turu("lira", "da") == "loc"
    assert ek_turu("lira", "dan") == "abl"
    assert ek_turu("lira", "zzz") is None
    assert ek_uret("tele", "dat") == "ye"
    assert ek_uret("tele", "loc") == "de"
    assert ek_uret("dolar", "dat") == "a"
    assert ek_uret("euro", "loc") == "da"
    assert ek_uret("tele", "bilinmeyen") == ""


def test_ekle_yaz() -> None:
    assert ekle_yaz("14:30", "da") == "14:30'da"
    assert ekle_yaz("3", "") == "3"
