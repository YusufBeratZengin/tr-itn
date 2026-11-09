"""Saat ifadeleri.

Kurallar:

* "saat" sözcüğü açık bağlam yaratır: "saat on dört otuz" -> "saat 14:30".
* "saat" olmadan, iki parçalı ifade (saat + dakika) ve bulunma/ayrılma eki
  varsa saat sayılır: "on dört otuzda" -> "14:30'da".
* "buçuk" 30, "çeyrek" 15 dakikadır; tek başına "üç buçuk" belirsiz olduğu
  için dönüştürülmez (ondalık mı saat mi belli değil).
* "sıfır dokuz" baştaki sıfırı korur: "09:00".
"""

from __future__ import annotations

from . import sozluk
from .metin import Eslesme, Kelime, KelimeDizisi
from .sayi import kardinal_coz
from .stil import Stil

_DAKIKA_ONEK = {"buçuk": 30, "çeyrek": 15}


def _dakika(koklar: list[str], j: int) -> tuple[int, int] | None:
    if j >= len(koklar):
        return None
    if koklar[j] in _DAKIKA_ONEK:
        return _DAKIKA_ONEK[koklar[j]], 1
    if koklar[j] == "sıfır" and j + 1 < len(koklar) and koklar[j + 1] in sozluk.BIRLER:
        return sozluk.BIRLER[koklar[j + 1]], 2
    for n in (2, 1):
        if j + n <= len(koklar):
            deger = kardinal_coz(koklar[j : j + n])
            if deger is not None and 0 <= deger <= 59:
                return deger, n
    return None


def _zaman(koklar: list[str], j: int) -> tuple[int, int, bool, int] | None:
    """(saat, dakika, baştaki_sıfır, tüketilen) döndürür."""
    if j >= len(koklar):
        return None
    bas_sifir = False
    adet = 0
    saat: int | None = None
    if koklar[j] == "sıfır" and j + 1 < len(koklar) and koklar[j + 1] in sozluk.BIRLER:
        saat = sozluk.BIRLER[koklar[j + 1]]
        bas_sifir = True
        adet = 2
    else:
        for n in (2, 1):
            if j + n <= len(koklar):
                deger = kardinal_coz(koklar[j : j + n])
                if deger is not None and 0 <= deger <= 24:
                    saat = deger
                    adet = n
                    break
    if saat is None:
        return None
    dakika = 0
    d = _dakika(koklar, j + adet)
    if d is not None:
        dakika, d_adet = d
        adet += d_adet
        if dakika > 59:
            return None
    return saat, dakika, bas_sifir, adet


def _bicim(saat: int, dakika: int, bas_sifir: bool) -> str:
    saat_metni = f"{saat:02d}" if bas_sifir else str(saat)
    return f"{saat_metni}:{dakika:02d}"


def coz(ks: KelimeDizisi, i: int, stil: Stil) -> Eslesme | None:
    koklar = ks.koklar

    # 1) "saat" öneki: "saat on dört otuz"
    if ks[i].kucuk == "saat" and not ks[i].ek:
        zaman = _zaman(koklar, i + 1)
        if zaman is not None:
            saat, dakika, bas_sifir, adet = zaman
            son = ks[i + adet]
            if i + adet + 1 < len(ks) and koklar[i + adet + 1] in sozluk.SAYI_SOZLERI:
                return None
            # "saat beşte" -> "saat 5'te": dakika yoksa ":00" yazılmaz
            if dakika == 0 and son.ek and not bas_sifir:
                metin = f"saat {saat}{f'{chr(39)}{son.ek}' if son.ek else ''}"
            else:
                metin = f"saat {_bicim(saat, dakika, bas_sifir)}"
                if son.ek:
                    metin += f"'{son.ek}"
            return Eslesme(
                metin=metin,
                adet=1 + adet,
                kural="saat",
                guven=1.0 if dakika else 0.9,
                aciklama="'saat' sözcüğü açık zaman bağlamı",
            )

    # 2) Eksiz / bağlamsız: yalnızca iki parçalı ve ekli ifade saat sayılır
    zaman = _zaman(koklar, i)
    if zaman is None:
        return None
    saat, dakika, bas_sifir, adet = zaman
    son = ks[i + adet - 1]
    if son.ek:
        tur = _ek_turu_guvenli(son)
        if tur not in ("loc", "abl", "dat"):
            return None
    elif not (stil.saat_kipi and dakika > 0):
        return None
    if dakika == 0 and not bas_sifir:
        return None
    if i + adet < len(ks) and koklar[i + adet] in sozluk.SAYI_SOZLERI:
        return None
    if not (0 <= saat <= 24):
        return None
    return Eslesme(
        metin=_bicim(saat, dakika, bas_sifir) + (f"'{son.ek}" if son.ek else ""),
        adet=adet,
        kural="saat",
        guven=0.9 if son.ek else 0.75,
        aciklama=(
            "iki parçalı ifade + hâl eki zaman bağlamı sayıldı"
            if son.ek
            else "saat_kipi açık: iki parçalı ifade saat sayıldı"
        ),
    )


def _ek_turu_guvenli(k: Kelime) -> str | None:
    from .ekler import ek_turu

    return ek_turu(k.kok, k.ek) if k.ek else None
