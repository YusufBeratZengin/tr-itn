"""Sayı çözümleme birim testleri."""

from __future__ import annotations

import pytest

from tr_itn import cevir
from tr_itn.sayi import (
    Deger,
    en_uzun_kardinal,
    kardinal_coz,
    kardinal_sozcuk,
    ondalik_coz,
    sira_eki,
    sira_metni,
    sira_sozcuk,
)
from tr_itn.stil import Stil


@pytest.mark.parametrize(
    ("sozcuk", "deger"),
    [
        ("sıfır", 0),
        ("bir", 1),
        ("on", 10),
        ("on bir", 11),
        ("yirmi bir", 21),
        ("yüz", 100),
        ("yüz bir", 101),
        ("iki yüz", 200),
        ("iki yüz elli üç", 253),
        ("bin", 1000),
        ("bin bir", 1001),
        ("iki bin yirmi altı", 2026),
        ("yüz bin", 100000),
        ("bir milyon", 1000000),
        ("iki milyar beş yüz milyon", 2500000000),
        ("bir trilyon", 1000000000000),
    ],
)
def test_kardinal_coz(sozcuk: str, deger: int) -> None:
    assert kardinal_coz(sozcuk.split()) == deger


@pytest.mark.parametrize(
    "sozcuk",
    [
        "",
        "iki üç",
        "yüz yüz",
        "bin bin",
        "milyon bin",
        "sıfır beş",
        "beş on",
        "dört otuz",
        "yüz elli bin milyon",
    ],
)
def test_kardinal_gecersiz(sozcuk: str) -> None:
    assert kardinal_coz(sozcuk.split()) is None


def test_en_uzun_kardinal_ortadan_baslar() -> None:
    koklar = ["saat", "on", "dört", "otuz"]
    assert en_uzun_kardinal(koklar, 1) == (14, 2)


def test_en_uzun_kardinal_bulunamaz() -> None:
    assert en_uzun_kardinal(["merhaba"], 0) is None


def test_kardinal_sozcuk_gidis_donus() -> None:
    for n in (0, 7, 42, 100, 101, 1000, 2026, 999999, 1000000):
        assert kardinal_coz(kardinal_sozcuk(n).split()) == n


def test_kardinal_sozcuk_hatalari() -> None:
    with pytest.raises(ValueError):
        kardinal_sozcuk(-1)
    with pytest.raises(ValueError):
        kardinal_sozcuk(10**16)


def test_sira_sozcuk() -> None:
    assert sira_sozcuk(1) == "birinci"
    assert sira_sozcuk(2) == "ikinci"
    assert sira_sozcuk(3) == "üçüncü"
    assert sira_sozcuk(4) == "dördüncü"
    assert sira_sozcuk(6) == "altıncı"
    assert sira_sozcuk(11) == "on birinci"
    assert sira_sozcuk(20) == "yirminci"
    assert sira_sozcuk(100) == "yüzüncü"


def test_sira_eki_rakamla() -> None:
    assert sira_eki(2) == "nci"
    assert sira_eki(3) == "üncü"
    assert sira_eki(6) == "ncı"
    assert sira_eki(100) == "üncü"


def test_sira_metni() -> None:
    assert sira_metni(3) == "3."
    assert sira_metni(3, "sü") == "3'üncüsü"


def test_deger_bicimleme() -> None:
    assert Deger(1500).metin() == "1500"
    assert Deger(1500).metin(Stil(binlik_ayirici=".")) == "1.500"
    assert Deger(1234567).metin(Stil(binlik_ayirici=".")) == "1.234.567"
    assert Deger(3, "05").metin() == "3,05"
    assert Deger(3, "05").metin(Stil(ondalik_ayirici=".")) == "3.05"
    assert Deger(-1500).metin(Stil(binlik_ayirici=".")) == "-1.500"


def test_ondalik_coz() -> None:
    assert ondalik_coz(["üç", "virgül", "beş"], 0) == (Deger(3, "5"), 3)
    assert ondalik_coz(["üç", "virgül", "sıfır", "beş"], 0) == (Deger(3, "05"), 4)
    assert ondalik_coz(["beş"], 0) is None
    assert ondalik_coz(["üç", "virgül"], 0) is None
    assert ondalik_coz(["üç", "nokta", "iki"], 0) == (Deger(3, "2"), 3)


# --- regresyon: ölçekli sıra sayıları ---------------------------------------


@pytest.mark.parametrize(
    ("sozcuk", "beklenen"),
    [
        ("iki yüzüncü", "200."),
        ("üç bininci", "3000."),
        ("on bininci", "10000."),
        ("iki milyonuncu", "2000000."),
        ("yüz milyonuncu", "100000000."),
        ("bin iki yüzüncü", "1200."),
        ("yüz elli üçüncü", "153."),
    ],
)
def test_sira_olcekli_sayi(sozcuk: str, beklenen: str) -> None:
    """Ölçek sözcüğü çarpan olmalı, toplanacak sayı değil."""
    assert cevir(sozcuk) == beklenen


def test_sira_gidis_donus_0_2000() -> None:
    """Rapordaki 0-2000 gidiş-dönüş taraması temiz olmalı."""
    hatalar = []
    for n in range(2001):
        sozcuk = sira_sozcuk(n)
        sonuc = cevir(sozcuk)
        if sonuc != f"{n}.":
            hatalar.append(f"{n}: {sozcuk!r} -> {sonuc!r}")
    assert not hatalar, "\n".join(hatalar[:10])

