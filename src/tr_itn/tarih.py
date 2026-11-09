"""Tarih ifadeleri.

Desteklenen biçimler:

* "iki kasım"                         -> "2 Kasım"
* "iki kasım iki bin yirmi altı"      -> "2 Kasım 2026"
* "kasım iki bin yirmi altı"          -> "Kasım 2026"
* "iki kasımda"                       -> "2 Kasım'da"
* "iki bin yirmi altı yılında"        -> "2026 yılında"

Gün 1-31, yıl 1000-2999 aralığında olmalıdır; aksi hâlde dönüşüm yapılmaz.
"Kasımın üçü" gibi iyelikli biçimler kapsam dışıdır ve olduğu gibi bırakılır.
"""

from __future__ import annotations

from . import sozluk
from .ekler import ek_turu
from .metin import Eslesme, KelimeDizisi
from .sayi import en_uzun_kardinal
from .stil import Stil


def _ay_adi(deger: int, stil: Stil) -> str:
    ad = sozluk.AY_ADLARI[deger]
    return ad if stil.ay_buyuk_harf else ad.lower()


def _yil(koklar: list[str], j: int) -> tuple[int, int] | None:
    if j >= len(koklar):
        return None
    bulunan = en_uzun_kardinal(koklar, j)
    if bulunan is None:
        return None
    deger, adet = bulunan
    if not (1000 <= deger <= 2999):
        return None
    return deger, adet


def _gun_ay(ks: KelimeDizisi, koklar: list[str], i: int, stil: Stil) -> Eslesme | None:
    aday = en_uzun_kardinal(koklar, i)
    if aday is None:
        return None
    gun, adet = aday
    if not (1 <= gun <= 31) or i + adet >= len(ks):
        return None
    if koklar[i + adet] not in sozluk.AYLAR:
        return None
    if any(ks[i + j].ek for j in range(adet)):
        return None
    ay_k = ks[i + adet]
    if ay_k.ek and ek_turu(ay_k.kok, ay_k.ek) not in ("loc", "abl", "dat"):
        return None
    yil = _yil(koklar, i + adet + 1)
    ay = _ay_adi(sozluk.AYLAR[ay_k.kok], stil)
    if yil is not None:
        yil_degeri, yil_adet = yil
        if ay_k.ek:
            return None
        son = ks[i + adet + 1 + yil_adet - 1]
        metin = f"{gun} {ay} {yil_degeri}"
        if son.ek:
            if ek_turu(son.kok, son.ek) is None:
                return None
            metin += f"'{son.ek}"
        return Eslesme(metin=metin, adet=adet + 1 + yil_adet, kural="tarih", guven=1.0)
    metin = f"{gun} {ay}"
    if ay_k.ek:
        metin += f"'{ay_k.ek}"
    return Eslesme(metin=metin, adet=adet + 1, kural="tarih", guven=1.0)


def _ay_yil(ks: KelimeDizisi, koklar: list[str], i: int, stil: Stil) -> Eslesme | None:
    k = ks[i]
    if k.ek and ek_turu(k.kok, k.ek) not in ("loc", "abl", "dat"):
        return None
    yil = _yil(koklar, i + 1)
    if yil is None:
        return None
    yil_degeri, yil_adet = yil
    if k.ek:
        return None
    son = ks[i + yil_adet]
    metin = f"{_ay_adi(sozluk.AYLAR[k.kok], stil)} {yil_degeri}"
    if son.ek:
        if ek_turu(son.kok, son.ek) is None:
            return None
        metin += f"'{son.ek}"
    return Eslesme(metin=metin, adet=1 + yil_adet, kural="tarih", guven=0.9)


def _yil_ipucu(ks: KelimeDizisi, koklar: list[str], i: int) -> Eslesme | None:
    bulunan = en_uzun_kardinal(koklar, i)
    if bulunan is None:
        return None
    deger, adet = bulunan
    if not (1000 <= deger <= 2999) or i + adet >= len(ks):
        return None
    sonraki = ks[i + adet]
    if sonraki.kok == "yıl" and sonraki.ek:
        return Eslesme(
            metin=f"{deger} {sonraki.metin}",
            adet=adet + 1,
            kural="tarih",
            guven=0.9,
            aciklama="'yıl' sözcüğü tarih bağlamı",
        )
    return None


def coz(ks: KelimeDizisi, i: int, stil: Stil) -> Eslesme | None:
    koklar = ks.koklar
    if koklar[i] in sozluk.AYLAR:
        return _ay_yil(ks, koklar, i, stil)
    return _gun_ay(ks, koklar, i, stil) or _yil_ipucu(ks, koklar, i)
