"""Alan sözlüğü, akış kipi, altyazı filtresi ve WER testleri."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tr_itn import Akis, AlanSozlugu, acikla, cevir, srt_cevir, vtt_cevir
from tr_itn.olcum import duzenleme_mesafesi, rapor, wer

# --- alan sözlüğü ------------------------------------------------------------


def test_sozluk_varsayilani_ezer() -> None:
    s = AlanSozlugu.kurallardan([("kdv", "KDV")])
    assert cevir("yüzde on sekiz kdv", alan=s) == "%18 KDV"


def test_sozluk_sayi_sozcugunu_korur() -> None:
    s = AlanSozlugu.kurallardan([("yüz", "YÜZ")])
    assert cevir("yüzde yüz", alan=s) == "yüzde YÜZ"
    assert s.cakismalar == ["yüz"]


def test_sozluk_cakisma_hata() -> None:
    with pytest.raises(ValueError, match="çakışan"):
        AlanSozlugu(kurallar={"bir": "1", "bir ": "2"})


def test_sozluk_bos_girdi_hata() -> None:
    with pytest.raises(ValueError):
        AlanSozlugu(kurallar={" ": "x"})


def test_sozluk_json_dosyasi(tmp_path: Path) -> None:
    yol = tmp_path / "finans.json"
    icerik = json.dumps({"ad": "finans", "kurallar": {"tl": "TL"}}, ensure_ascii=False)
    yol.write_text(icerik, encoding="utf-8")
    s = AlanSozlugu.dosyadan(yol)
    assert s.ad == "finans"
    assert cevir("kdv ve tl", alan=s) == "kdv ve TL"


def test_sozluk_yaml_dosyasi(tmp_path: Path) -> None:
    yol = tmp_path / "tip.yaml"
    yol.write_text("# yorum\nkdv: KDV\nmr: MR\n", encoding="utf-8")
    s = AlanSozlugu.dosyadan(yol)
    assert s.kurallar == {"kdv": "KDV", "mr": "MR"}
    assert len(s) == 2


def test_sozluk_tam_kelime_eslesmesi() -> None:
    s = AlanSozlugu.kurallardan([("kdv", "KDV")])
    assert cevir("kdvli", alan=s) == "kdvli"


def test_sozluk_uzun_eslesme_once() -> None:
    s = AlanSozlugu.kurallardan([("kdv", "A"), ("kdv oranı", "B")])
    assert cevir("kdv oranı", alan=s) == "B"


def test_sozluk_bos() -> None:
    s = AlanSozlugu()
    assert s.uygula("bir şey") == "bir şey"
    assert len(s) == 0


def test_sozluk_gecersiz_yapi() -> None:
    with pytest.raises(ValueError):
        AlanSozlugu.sozlukten({"kurallar": ["a"]})


# --- regresyon: Türkçe büyük/küçük harf (İ/I) --------------------------------


@pytest.mark.parametrize(
    ("anahtar", "girdi"),
    [
        ("istanbul", "İSTANBUL"),
        ("istanbul", "ISTANBUL"),
        ("istanbul", "İstanbul"),
        ("ışık", "IŞIK"),
        ("işık", "İŞIK"),
        ("ıstanbul", "ISTANBUL"),
    ],
)
def test_alan_turkce_buyuk_harf(anahtar: str, girdi: str) -> None:
    """İ/I çiftleri sözlük anahtarında KeyError üretmemeli."""
    s = AlanSozlugu.kurallardan([(anahtar, "X")])
    assert s.uygula(girdi) == "X"
    assert cevir(girdi + " üç", alan=s) == "X 3"
    assert acikla(girdi + " üç", alan=s)


@pytest.mark.parametrize("girdi", ["ISTANBUL üç", "İstanbul üç", "istanbul üç"])
def test_alan_ascii_buyuk_i_anahtara_cozulur(girdi: str) -> None:
    """Regex eşleşmesi ile Türkçe normalizasyon aynı anahtara varmalı."""
    s = AlanSozlugu(kurallar={"istanbul": "X"})
    assert cevir(girdi, alan=s) == "X 3"
    assert acikla(girdi, alan=s)  # KeyError yok, sayı izi gelir


@pytest.mark.parametrize(
    ("anahtar", "girdi"),
    [("başlık bilgisi", "BAŞLIK BILGISI"), ("kayıt bilgisi", "KAYIT BILGISI")],
)
def test_alan_karisik_i_anahtara_cozulur(anahtar: str, girdi: str) -> None:
    s = AlanSozlugu(kurallar={anahtar: "X"})
    assert cevir(girdi + " üç", alan=s) == "X 3"
    assert s.uygula(girdi) == "X"
    korumali, yer = s.uygula_korumali(girdi)
    assert s.geri_yukle(korumali, yer) == "X"
    assert acikla(girdi + " üç", alan=s)


@pytest.mark.parametrize(
    ("anahtar", "girdi"),
    [("straße", "STRAẞE"), ("ος", "ΟΣ")],
)
def test_alan_unicode_buyuk_kucuk_harf(anahtar: str, girdi: str) -> None:
    s = AlanSozlugu(kurallar={anahtar: "X"})
    assert cevir(girdi + " üç", alan=s) == "X 3"
    assert s.uygula(girdi) == "X"
    korumali, yer = s.uygula_korumali(girdi)
    assert s.geri_yukle(korumali, yer) == "X"
    assert acikla(girdi + " üç", alan=s)


# --- akış kipi ---------------------------------------------------------------


def test_akis_bolunen_sayi() -> None:
    a = Akis()
    assert a.besle("toplantı iki bin") == "toplantı "
    assert a.besle(" yirmi altı") == ""
    assert a.bitir() == "2026"


def test_akis_yarim_kelime() -> None:
    a = Akis()
    assert a.besle("yirmi bi") == ""
    # "kişi" hâlâ sürebilir; ayırıcı gelene kadar tutulur
    assert a.besle("r kişi") == ""
    assert a.besle(" ") == "21 kişi "


def test_akis_bos_parca() -> None:
    a = Akis()
    assert a.besle("") == ""
    assert a.bitir() == ""


def test_akis_tampon() -> None:
    a = Akis()
    a.besle("iki")
    assert a.tampon == "iki"


def test_akis_hata() -> None:
    with pytest.raises(TypeError):
        Akis().besle(None)  # type: ignore[arg-type]


def test_akis_metin_kaybetmez() -> None:
    metin = "saat on dört otuzda yüzde on sekiz kdv ve iki bin yirmi altı yılı"
    for kesim in range(1, len(metin), 7):
        a = Akis()
        cikti = a.besle(metin[:kesim]) + a.besle(metin[kesim:]) + a.bitir()
        assert cikti == cevir(metin), kesim


# --- altyazı -----------------------------------------------------------------


SRT = (
    "1\n"
    "00:00:01,000 --> 00:00:03,000\n"
    "toplantı saat on dört otuzda\n"
    "\n"
    "2\n"
    "00:00:04,000 --> 00:00:06,000\n"
    "yüzde on sekiz kdv\n"
)


def test_srt_cevir() -> None:
    cikti = srt_cevir(SRT)
    assert "00:00:01,000 --> 00:00:03,000" in cikti
    assert "toplantı saat 14:30'da" in cikti
    assert "%18 kdv" in cikti
    assert cikti.count("-->") == 2


def test_vtt_cevir() -> None:
    vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\nüç kilometre\n"
    cikti = vtt_cevir(vtt)
    assert cikti.startswith("WEBVTT")
    assert "3 km" in cikti


def test_srt_satir_sonu_korunur() -> None:
    assert srt_cevir("1\r\n00:00:01,000 --> 00:00:02,000\r\nüç\r\n").endswith("3\r\n")


def test_srt_bos() -> None:
    assert srt_cevir("") == ""


# --- WER ---------------------------------------------------------------------


def test_duzenleme_mesafesi() -> None:
    assert duzenleme_mesafesi([], []) == 0
    assert duzenleme_mesafesi(["a"], []) == 1
    assert duzenleme_mesafesi([], ["a", "b"]) == 2
    assert duzenleme_mesafesi(["a", "b"], ["a", "b"]) == 0
    assert duzenleme_mesafesi(["a", "b"], ["a", "c"]) == 1


def test_wer() -> None:
    assert wer("a b c", "a b c") == 0.0
    assert wer("a b", "a") == 0.5
    assert wer("", "herhangi") == 0.0


def test_wer_raporu() -> None:
    kayitlar = [
        {"referans": "2 Kasım", "hipotez": "iki kasım"},
        {"referans": "150 TL", "hipotez": "yüz elli lira"},
    ]
    r = rapor(kayitlar)
    assert r.kayit_sayisi == 2
    assert r.once > r.sonra
    assert r.fark > 0


def test_wer_raporu_bos() -> None:
    r = rapor([])
    assert r.kayit_sayisi == 0
    assert r.fark == 0.0
