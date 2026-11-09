"""Bağlam yargıçları: türemiş sözcük koruması ve ikilemeler."""

from __future__ import annotations

import pytest

from tr_itn import cevir
from tr_itn.baglam import sayi_devami
from tr_itn.metin import kelimeler, parcala


def _kelime(metin: str):
    return kelimeler(parcala(metin))[0]


@pytest.mark.parametrize("sozcuk", ["sekizlik", "yüzlü", "binlerce", "ikili"])
def test_turemis_sayilar_devam_sayilir(sozcuk: str) -> None:
    assert sayi_devami(_kelime(sozcuk)) is True


@pytest.mark.parametrize("sozcuk", ["sekiz", "yüz", "bin", "masa", "ikinci", "onlarca"])
def test_sade_sayilar_devam_degil(sozcuk: str) -> None:
    assert sayi_devami(_kelime(sozcuk)) is False


def test_none_devam_degil() -> None:
    assert sayi_devami(None) is False


def test_ekli_sozcuk_devam_degil() -> None:
    # "otuzunda" çözümlenmiş bir ek taşır; devam sayılmaz.
    assert sayi_devami(_kelime("otuzunda")) is False


@pytest.mark.parametrize(
    ("girdi", "beklenen"),
    [
        ("on sekizlik", "on sekizlik"),
        ("yüzde on sekizlik artış", "yüzde on sekizlik artış"),
        ("iki yüzlü insan", "iki yüzlü insan"),
        ("on binlerce kişi", "on binlerce kişi"),
        ("iki yüz yirmi beş", "225"),
        ("on dört otuzda", "14:30'da"),
    ],
)
def test_metin_uzerinde_etkisi(girdi: str, beklenen: str) -> None:
    assert cevir(girdi) == beklenen
