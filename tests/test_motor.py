"""Motor, stil seçenekleri ve kural izleri testleri."""

from __future__ import annotations

import pytest

from tr_itn import acikla, cevir, cevir_ayrintili
from tr_itn.motor import KuralIzi
from tr_itn.stil import Stil


def test_kart_ornegi() -> None:
    girdi = "toplantı iki kasım iki bin yirmi altı saat on dört otuzda"
    assert cevir(girdi) == "toplantı 2 Kasım 2026 saat 14:30'da"


def test_karma_cumle() -> None:
    girdi = "yüzde on sekiz kdv, yüz elli lira ve üç kilometre"
    assert cevir(girdi) == "%18 kdv, 150 TL ve 3 km"


def test_acikla_izleri() -> None:
    izler = acikla("yüzde on sekiz")
    assert len(izler) == 1
    iz = izler[0]
    assert isinstance(iz, KuralIzi)
    assert iz.kural == "yuzde"
    assert iz.girdi == "yüzde on sekiz"
    assert iz.cikti == "%18"
    assert iz.konum == (0, 14)
    assert 0.0 < iz.guven <= 1.0


def test_acikla_konumlari_ozgun_metne_isaret_eder() -> None:
    metin = "saat on dört otuz"
    iz = acikla(metin)[0]
    bas, bitis = iz.konum
    assert metin[bas:bitis] == iz.girdi


def test_acikla_bos() -> None:
    assert acikla("merhaba dünya") == []


def test_ayar_binlik() -> None:
    stil = Stil(binlik_ayirici=".")
    assert cevir("iki bin yirmi altı", stil) == "2.026"
    assert cevir("yüz elli lira", stil) == "150 TL"


def test_ayar_ondalik_nokta() -> None:
    assert cevir("üç virgül beş", Stil(ondalik_ayirici=".")) == "3.5"


def test_ayar_esik() -> None:
    stil = Stil(esik=10)
    assert cevir("beş kişi", stil) == "beş kişi"
    assert cevir("on kişi", stil) == "10 kişi"


def test_ayar_ust_sinir() -> None:
    stil = Stil(ust_sinir=1000)
    assert cevir("doksan dokuz", stil) == "99"
    assert cevir("iki bin", stil) == "iki bin"


def test_ayar_bir_gevsek() -> None:
    assert cevir("bir gün gelecek", Stil(bir_baglami="gevsek")) == "1 gün gelecek"
    assert cevir("bir gün gelecek") == "bir gün gelecek"


def test_ayar_saat_kipi() -> None:
    assert cevir("on dört otuz", Stil(saat_kipi=True)) == "14:30"
    assert cevir("on dört otuz") == "on dört otuz"


def test_ayar_rakam_dizisi() -> None:
    metin = "sıfır beş üç iki bir iki üç dört beş altı yedi"
    assert cevir(metin, Stil(rakam_dizisi=True)) == "05321234567"


def test_rakam_ipucu_kelime() -> None:
    metin = "telefon numarası sıfır beş üç iki sıfır sıfır sıfır sıfır sıfır sıfır"
    cikti = cevir(metin)
    assert cikti.startswith("telefon numarası 0532")


def test_ayar_para_adi() -> None:
    assert cevir("yüz elli lira", Stil(para_sembolu=False)) == "150 lira"


def test_ayar_ay_kucuk() -> None:
    assert cevir("iki kasım", Stil(ay_buyuk_harf=False)) == "2 kasım"


def test_saat_kipi_saat_sozcugu_ile() -> None:
    assert cevir("saat on dört") == "saat 14:00"


@pytest.mark.parametrize(
    "girdi",
    [
        "",
        " ",
        "...",
        "!!?",
        "أرقام",
        "123 456",
        "2026 yılında",
        "'tırnak' \"içinde\"",
        "yüzde",
        "saat",
        "bir",
        "yüz",
        "bin",
        "on iki üç dört beş altı yedi sekiz dokuz on",
        "\n\n",
        "a" * 5000,
    ],
)
def test_asla_firlatmaz(girdi: str) -> None:
    sonuc = cevir(girdi)
    assert isinstance(sonuc, str)


def test_hata_none() -> None:
    with pytest.raises(TypeError):
        cevir(None)  # type: ignore[arg-type]


def test_noktalama_korunur() -> None:
    assert cevir("(iki kasım), saat üçte!") == "(2 Kasım), saat 3'te!"


def test_cok_satirli() -> None:
    metin = "birinci satır\nüçüncü satır"
    assert cevir(metin) == "1. satır\n3. satır"


def test_buyuk_harf_girdi() -> None:
    assert cevir("İki Kasım") == "2 Kasım"


def test_ayrintili_sonuc() -> None:
    sonuc = cevir_ayrintili("üçüncü")
    assert sonuc.metin == "3."
    assert sonuc.izler[0].kural == "sira"


def test_guven_dusuk_olabilir() -> None:
    iz = acikla("ikinci")[0]
    assert iz.guven <= 1.0


def test_stil_varsayilanlari() -> None:
    s = Stil()
    assert s.ondalik_ayirici == ","
    assert s.binlik_ayirici is None
    assert s.bir_baglami == "siki"


def test_stil_ile() -> None:
    assert Stil().ile(esik=5).esik == 5


@pytest.mark.parametrize(
    "kwargs",
    [
        {"ondalik_ayirici": ";"},
        {"binlik_ayirici": "x"},
        {"bir_baglami": "serbest"},
        {"esik": -1},
    ],
)
def test_stil_gecersiz(kwargs: dict) -> None:
    with pytest.raises(ValueError):
        Stil(**kwargs)


# --- regresyon: çok sözcüklü eşleşmede araya giren veri ---------------------


@pytest.mark.parametrize(
    "girdi",
    [
        "iki 3 kasım",
        "iki 2026 kasım",
        "saat on 14 otuzda",
        "yüz 5 elli lira",
        "toplantı iki\nkasım",
        "toplantı iki (kasım)",
    ],
)
def test_cok_sozcuklu_eslesme_araya_giren_veriyi_korur(girdi: str) -> None:
    """Araya giren rakam, noktalama ve satır sonu silinmemeli."""
    assert cevir(girdi) == girdi


def test_acikla_araya_giren_rakami_yutmez() -> None:
    assert cevir("iki 3 kasım") == "iki 3 kasım"
    assert acikla("iki 3 kasım") == []


# --- regresyon: Unicode satır/sayfa ayırıcıları -----------------------------


@pytest.mark.parametrize(
    "ayirici",
    ["\u2028", "\u2029", "\u0085", "\x0b", "\x0c", "\x1c", "\x1d", "\x1e"],
    ids=lambda ch: f"U+{ord(ch):04X}",
)
def test_unicode_satir_ayirici_kopru_sayilmaz(ayirici: str) -> None:
    """Ayırıcı silinmemeli; çok sözcüklü kural onun üzerinden kurulmamalı."""
    girdi = f"iki{ayirici}kasım"
    assert cevir(girdi) == girdi
    assert acikla(girdi) == []
