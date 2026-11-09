"""Para ifadeleri.

"yüz elli lira" -> "150 TL", "iki bin dolar" -> "$2000".
Ek, okunuşa göre uyumlanır: "yüz elli liraya" -> "150 TL'ye".
Sembol önde olan para birimlerinde ek varsa ad yazılır: "150 dolara".
"""

from __future__ import annotations

from . import sozluk
from .ekler import ek_turu, ek_uret
from .metin import Eslesme, KelimeDizisi
from .sayi import ifade_coz
from .stil import Stil


def para_metni(deger_metni: str, kok: str, ek: str, stil: Stil) -> str | None:
    sembol, onde = sozluk.PARA_BIRIMLERI[kok]
    if not stil.para_sembolu:
        sembol, onde = kok, False
    if not ek:
        return f"{sembol}{deger_metni}" if onde else f"{deger_metni} {sembol}"
    tur = ek_turu(kok, ek)
    if tur is None:
        return None
    if sembol.isalpha() and sembol == kok:
        # düz Türkçe sözcük: kesme işareti yok, ek aynen
        return f"{deger_metni} {sembol}{ek}"
    if onde:
        # sembol önde: eki taşımak yerine adı yaz
        return f"{deger_metni} {kok}{ek}"
    okunus = sozluk.SEMBOL_OKUNUS.get(sembol, kok)
    return f"{deger_metni} {sembol}'{ek_uret(okunus, tur)}"


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
    if birim_k.tuzak or birim_k.kok not in sozluk.PARA_BIRIMLERI:
        return None
    if deger.tam < stil.esik:
        return None
    if stil.ust_sinir is not None and deger.tam > stil.ust_sinir:
        return None
    metin = para_metni(deger.metin(stil), birim_k.kok, birim_k.ek, stil)
    if metin is None:
        return None
    return Eslesme(
        metin=metin,
        adet=adet + 1,
        kural="para",
        guven=0.95 if not birim_k.ek else 0.85,
        aciklama=f"para birimi: {birim_k.kok}",
    )
