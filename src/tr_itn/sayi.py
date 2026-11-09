"""Sayı çözümleme: kardinal, ondalık ve sıra sayıları.

Türkçe sayı sözleri üçlü gruplar hâlinde kurulur ("iki yüz elli üç bin yedi").
Bu modül o grameri katı biçimde uygular: "iki üç" gibi ardışık iki birim sözü
tek sayı sayılmaz, "yüz yüz" reddedilir.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import sozluk
from .baglam import bir_uygun, sira_engel, yuz_uygun
from .ekler import SESLILER, unlu_dortlu
from .metin import Eslesme, KelimeDizisi
from .stil import Stil

MAKS_UZUNLUK = 48  # bir sayı ifadesinde en çok bu kadar sözcük


@dataclass(frozen=True)
class Deger:
    """Yazıya çevrilecek sayısal değer.

    ``kesir`` ondalık kısmın rakamlarıdır ve baştaki sıfırları korur
    ("3,05" -> tam=3, kesir="05").
    """

    tam: int
    kesir: str | None = None

    def metin(self, stil: Stil | None = None) -> str:
        s = stil if stil is not None else Stil()
        tam = _binlik(self.tam, s.binlik_ayirici)
        if self.kesir is None:
            return tam
        return f"{tam}{s.ondalik_ayirici}{self.kesir}"


def _binlik(deger: int, ayirici: str | None) -> str:
    isaret = "-" if deger < 0 else ""
    rakamlar = str(abs(deger))
    if not ayirici or len(rakamlar) <= 3:
        return isaret + rakamlar
    parcalar: list[str] = []
    while rakamlar:
        parcalar.append(rakamlar[-3:])
        rakamlar = rakamlar[:-3]
    return isaret + ayirici.join(reversed(parcalar))


# --- Kardinal ----------------------------------------------------------------


def _grup(ws: list[str], i: int) -> tuple[int | None, int]:
    """0-999 arası bir grubu çözer. Tüketilen sözcük sayısını da döndürür."""
    v = 0
    kullanildi = False
    bas = i
    birim_one = False
    if i < len(ws) and ws[i] in sozluk.BIRLER and ws[i] != "sıfır":
        v = sozluk.BIRLER[ws[i]]
        i += 1
        kullanildi = True
        birim_one = True
    yuz = False
    if i < len(ws) and ws[i] == sozluk.YUZ:
        v = (v or 1) * 100
        i += 1
        kullanildi = True
        yuz = True
    if i < len(ws) and ws[i] in sozluk.ONLAR and (not birim_one or yuz):
        v += sozluk.ONLAR[ws[i]]
        i += 1
        kullanildi = True
    # Ardışık iki birim sözü ("iki üç") sayı değildir; yalnızca araya "yüz"
    # girdiyse ("iki yüz üç") ya da ilk söz birim değilse ("on iki") kabul edilir.
    if (
        i < len(ws)
        and ws[i] in sozluk.BIRLER
        and ws[i] != "sıfır"
        and (not birim_one or yuz)
    ):
        v += sozluk.BIRLER[ws[i]]
        i += 1
        kullanildi = True
    if not kullanildi:
        return None, bas
    return v, i


def kardinal_coz(ws: list[str]) -> int | None:
    """Sözcük dizisinin tamamını tek bir kardinal sayı olarak çözer."""
    if not ws:
        return None
    if ws == ["sıfır"]:
        return 0
    if "sıfır" in ws:
        return None
    toplam = 0
    i = 0
    son_olcek = float("inf")
    while i < len(ws):
        grup, i2 = _grup(ws, i)
        if grup is None:
            # Yalnızca "bin" tek başına 1000'dir; "milyon" için "bir" gerekir.
            if ws[i] == "bin":
                grup = 1
            else:
                return None
        i = i2
        if i < len(ws) and ws[i] in sozluk.OLCEKLER:
            olcek = sozluk.OLCEKLER[ws[i]]
            if olcek >= son_olcek:
                return None
            toplam += grup * olcek
            son_olcek = olcek
            i += 1
        else:
            toplam += grup
            break
    if i != len(ws):
        return None
    if toplam > 10**15:
        return None
    return toplam


def en_uzun_kardinal(ws: list[str], i: int) -> tuple[int, int] | None:
    """``i`` konumundan başlayan en uzun kardinal ifadeyi bulur.

    Dönen değer ``(sayı, tüketilen_sözcük)``; bulunamazsa ``None``.
    """
    j = i
    while j < len(ws) and ws[j] in sozluk.SAYI_SOZLERI:
        j += 1
    ust = min(j - i, MAKS_UZUNLUK)
    for uzunluk in range(ust, 0, -1):
        deger = kardinal_coz(ws[i : i + uzunluk])
        if deger is not None:
            return deger, uzunluk
    return None


# --- Sayıdan söze (yardımcı) -------------------------------------------------

_BIRIM_ADI = {v: k for k, v in sozluk.BIRLER.items() if v}
_ONLUK_ADI = {v: k for k, v in sozluk.ONLAR.items()}
_OLCEK_SIRA: tuple[tuple[int, str], ...] = (
    (1_000_000_000_000, "trilyon"),
    (1_000_000_000, "milyar"),
    (1_000_000, "milyon"),
    (1_000, "bin"),
)


def kardinal_sozcuk(n: int) -> str:
    """Sayının Türkçe okunuşu: 2026 -> "iki bin yirmi altı".

    Kütüphanenin asıl yönü sözden sayıya çevirmedir; bu yardımcı, sıra
    sayılarını kurmak ve gidiş-dönüş testlerini doğrulamak için gereklidir.
    """
    if n < 0:
        raise ValueError("negatif sayı desteklenmiyor")
    if n == 0:
        return "sıfır"
    if n > 999_999_999_999_999:
        raise ValueError("sayı çok büyük")
    parcalar: list[str] = []
    for olcek, ad in _OLCEK_SIRA:
        if n >= olcek:
            kac, n = divmod(n, olcek)
            if olcek == 1_000 and kac == 1:
                parcalar.append("bin")
            else:
                parcalar.append(f"{kardinal_sozcuk(kac)} {ad}")
    if n >= 100:
        yuz, n = divmod(n, 100)
        if yuz > 1:
            parcalar.append(_BIRIM_ADI[yuz])
        parcalar.append("yüz")
    if n >= 10:
        onluk, n = divmod(n, 10)
        parcalar.append(_ONLUK_ADI[onluk * 10])
    if n:
        parcalar.append(_BIRIM_ADI[n])
    return " ".join(parcalar)


# --- Sıra sayıları -----------------------------------------------------------


def _son_bilesen(n: int) -> str:
    """Sayının okunuşundaki son anlamlı sözcüğü döndürür (sıra eki için)."""
    if n == 0:
        return "sıfır"
    if n % 10:
        for sozcuk, deger in sozluk.BIRLER.items():
            if deger == n % 10:
                return sozcuk
    if n % 100:
        for sozcuk, deger in sozluk.ONLAR.items():
            if deger == n % 100:
                return sozcuk
    if n % 1000:
        return "yüz"
    if n % 1_000_000 == 0 and (n // 1_000_000) % 1000 == 0 and n >= 1_000_000_000:
        return "milyar"
    if n % 1_000_000 == 0:
        return "milyon"
    return "bin"


def _sira_govde(kok: str) -> str:
    govde = kok[:-1] if kok and kok[-1] in SESLILER else kok
    if govde == "dört" or (govde.endswith("t") and kok == "dört"):
        govde = "dörd"
    return govde


def sira_sozcuk(n: int) -> str:
    """``n`` sayısının sıra sayısı sözcüğü: 3 -> "üçüncü", 11 -> "on birinci"."""
    sozcukler = kardinal_sozcuk(n).split()
    son = sozcukler[-1]
    govde = _sira_govde(son)
    v = unlu_dortlu(govde)
    sozcukler[-1] = f"{govde}{v}nc{v}"
    return " ".join(sozcukler)


def sira_eki(n: int) -> str:
    """Rakamla yazılan sıra sayısının eki: 3 -> "üncü" (yazım: 3'üncü)."""
    kok = _son_bilesen(n)
    sesli_bitti = kok[-1] in SESLILER
    govde = _sira_govde(kok)
    v = unlu_dortlu(govde)
    if sesli_bitti:
        return f"nc{v}"
    return f"{v}nc{v}"


def sira_metni(n: int, ek: str = "") -> str:
    """Sıra sayısının yazı biçimi: 3 -> "3.", "3'üncüsü"."""
    if not ek:
        return f"{n}."
    return f"{n}'{sira_eki(n)}{ek}"


# --- Ondalık ----------------------------------------------------------------


def _rakam_dizisi(ws: list[str], i: int) -> tuple[str, int]:
    parcalar: list[str] = []
    while i < len(ws) and ws[i] in sozluk.BIRLER:
        parcalar.append(str(sozluk.BIRLER[ws[i]]))
        i += 1
    return "".join(parcalar), i


def ondalik_coz(ws: list[str], i: int) -> tuple[Deger, int] | None:
    """``i`` konumundan başlayan ondalık ifadeyi çözer: "üç virgül beş" -> 3,5."""
    kardinal = en_uzun_kardinal(ws, i)
    if kardinal is None:
        return None
    tam, tuketilen = kardinal
    j = i + tuketilen
    if j >= len(ws) or ws[j] not in ("virgül", "nokta"):
        return None
    j += 1
    if j >= len(ws):
        return None
    # "üç virgül sıfır beş" -> 3,05: baştaki sıfır rakam okumasına işarettir
    if ws[j] == "sıfır":
        rakamlar, j2 = _rakam_dizisi(ws, j)
        return Deger(tam, rakamlar), j2 - i
    kesir_kardinal = en_uzun_kardinal(ws, j)
    if kesir_kardinal is not None:
        kesir, n = kesir_kardinal
        return Deger(tam, str(kesir)), j + n - i
    # "sıfır beş" gibi rakam rakam okunan ondalık kısım
    rakamlar, j2 = _rakam_dizisi(ws, j)
    if not rakamlar:
        return None
    return Deger(tam, rakamlar), j2 - i


# --- Kural eşleştiricileri ---------------------------------------------------


def ifade_coz(ks: KelimeDizisi, i: int) -> tuple[Deger, int] | None:
    """``i``den başlayan en uzun sayısal ifade (ondalık, buçuk, kardinal)."""
    koklar = ks.koklar
    ondalik = ondalik_coz(koklar, i)
    if ondalik is not None:
        return ondalik
    kardinal = en_uzun_kardinal(koklar, i)
    if kardinal is None:
        return None
    deger, n = kardinal
    if i + n < len(koklar) and koklar[i + n] == "buçuk":
        return Deger(deger, "5"), n + 1
    return Deger(deger), n


def _sinir_disi(deger: Deger, stil: Stil) -> bool:
    if deger.tam < stil.esik:
        return True
    return stil.ust_sinir is not None and deger.tam > stil.ust_sinir


def _ek_on_ek_uygun(ks: KelimeDizisi, i: int, adet: int) -> bool:
    """İfadenin son sözcüğü dışında ek taşıyan sözcük var mı?"""
    return any(ks[i + j].ek for j in range(adet - 1))


def kardinal_esle(ks: KelimeDizisi, i: int, stil: Stil) -> Eslesme | None:
    ifade = ifade_coz(ks, i)
    if ifade is None:
        return None
    deger, adet = ifade
    if _ek_on_ek_uygun(ks, i, adet):
        return None
    son = ks[i + adet - 1]
    # Sayı ifadesi ortada kesilmiş olabilir: "on dört otuz", "iki üç".
    if i + adet < len(ks):
        sonraki = ks[i + adet].kok
        if sonraki in sozluk.SAYI_SOZLERI or sonraki in sozluk.SIRA_OZEL:
            return None
    if adet == 1 and son.kok == "bir" and not bir_uygun("kardinal", 1, stil):
        return None
    if adet == 1 and son.kok == "yüz" and not yuz_uygun("kardinal", 1):
        return None
    # Çıplak "üç buçuk" belirsizdir (3,5 mi 3:30 mu); birim/para/saat
    # bağlamı yoksa dönüştürülmez.
    if adet >= 2 and ks[i + adet - 1].kok == "buçuk":
        return None
    if _sinir_disi(deger, stil):
        return None
    metin = deger.metin(stil)
    kural = "ondalik" if deger.kesir is not None else "kardinal"
    guven = 0.85 if adet == 1 and son.kok in ("yüz", "bir") else 0.95
    return Eslesme(metin=metin + (f"'{son.ek}" if son.ek else ""), adet=adet, kural=kural, guven=guven)


def yuzde_esle(ks: KelimeDizisi, i: int, stil: Stil) -> Eslesme | None:
    if ks[i].kucuk not in ("yüzde",):
        return None
    ifade = ifade_coz(ks, i + 1)
    if ifade is None:
        return None
    deger, adet = ifade
    son = ks[i + adet]
    if adet == 1 and son.kok == "bir" and not bir_uygun("yuzde", 1, stil):
        return None
    if son.ek:
        return None
    if _sinir_disi(deger, stil):
        return None
    return Eslesme(metin="%" + deger.metin(stil), adet=1 + adet, kural="yuzde", guven=0.98)


#: Ölçek sözcüğüyle biten sıra sayıları -> kardinal karşılığı. Bunlarda
#: öndeki çarpan toplanmaz, çarpılır: "iki yüzüncü" = 2 x 100.
_SIRA_OLCEK_KOK: dict[str, str] = {
    "yüzüncü": "yüz",
    "bininci": "bin",
    "milyonuncu": "milyon",
    "milyarıncı": "milyar",
}


def sira_esle(ks: KelimeDizisi, i: int, stil: Stil) -> Eslesme | None:
    koklar = ks.koklar
    for adet in range(1, 7):
        j = i + adet - 1
        if j >= len(ks):
            break
        if koklar[j] not in sozluk.SIRA_OZEL:
            continue
        taban = sozluk.SIRA_OZEL[koklar[j]]
        if adet > 1:
            olcek_kok = _SIRA_OLCEK_KOK.get(koklar[j])
            if olcek_kok is not None:
                # Sıra sözcüğünü kardinal karşılığıyla değiştirip ifadenin
                # tamamını yeniden çöz: "bin iki yüzüncü" -> "bin iki yüz".
                cozulen = kardinal_coz([*koklar[i:j], olcek_kok])
                if cozulen is None:
                    continue
                deger = cozulen
            else:
                onek = kardinal_coz(koklar[i:j])
                if onek is None:
                    continue
                deger = onek + taban
        else:
            deger = taban
        if _ek_on_ek_uygun(ks, i, adet):
            return None
        sonraki = koklar[j + 1] if j + 1 < len(koklar) else None
        if sira_engel(deger, sonraki):
            return None
        if _sinir_disi(Deger(deger), stil):
            return None
        return Eslesme(
            metin=sira_metni(deger, ks[j].ek),
            adet=adet,
            kural="sira",
            guven=1.0 if adet > 1 else 0.95,
        )
    return None
