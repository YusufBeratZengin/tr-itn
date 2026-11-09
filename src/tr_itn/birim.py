"""Ölçü birimleri.

"üç kilometre" -> "3 km", "beş kilo" -> "5 kg", "yirmi beş derece" -> "25°".
Kısaltmalar okunuşa göre ek alır ("üç kilometreye" -> "3 km'ye"); düz Türkçe
sözcüklerde kesme işareti kullanılmaz ("üç saatte" -> "3 saatte").
"""

from __future__ import annotations

from . import sozluk
from .baglam import bir_uygun, yuz_uygun
from .ekler import ek_turu, ek_uret
from .metin import Eslesme, KelimeDizisi
from .sayi import ifade_coz
from .stil import Stil


def birim_metni(deger_metni: str, kok: str, ek: str) -> str | None:
    yazim = sozluk.BIRIMLER[kok]
    ayrac = "" if yazim == "°" else " "
    if not ek:
        return f"{deger_metni}{ayrac}{yazim}"
    tur = ek_turu(kok, ek)
    if tur is None:
        return None
    if yazim == kok:
        return f"{deger_metni}{ayrac}{yazim}{ek}"
    okunus = sozluk.SEMBOL_OKUNUS.get(yazim, kok)
    return f"{deger_metni}{ayrac}{yazim}'{ek_uret(okunus, tur)}"


def coz(ks: KelimeDizisi, i: int, stil: Stil) -> Eslesme | None:
    ifade = ifade_coz(ks, i)
    if ifade is None:
        return None
    deger, adet = ifade
    if any(ks[i + j].ek for j in range(adet)):
        return None
    j = i + adet
    if j >= len(ks):
        return None
    birim_k = ks[j]
    if birim_k.tuzak or birim_k.kok not in sozluk.BIRIMLER:
        return None
    if adet == 1 and ks[i].kok == "bir" and not bir_uygun("birim", 1, stil):
        return None
    if adet == 1 and ks[i].kok == "yüz" and not yuz_uygun("birim", 1):
        return None
    if deger.tam < stil.esik:
        return None
    if stil.ust_sinir is not None and deger.tam > stil.ust_sinir:
        return None
    metin = birim_metni(deger.metin(stil), birim_k.kok, birim_k.ek)
    if metin is None:
        return None
    return Eslesme(
        metin=metin,
        adet=adet + 1,
        kural="birim",
        guven=0.95 if not birim_k.ek else 0.85,
        aciklama=f"birim: {birim_k.kok}",
    )
