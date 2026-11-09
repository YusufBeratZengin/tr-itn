"""Bağlam ve belirsizlik kuralları.

Türkçede sayı sözleri ile günlük sözcükler çakışır: "bir gün", "ikinci el",
"yüz yüze", "onun". Bu modül, dönüşümün güvenli olup olmadığına karar veren
küçük yargıçları toplar. Kural: emin değilsen dönüştürme.
"""

from __future__ import annotations

from . import sozluk
from .metin import Kelime, KelimeDizisi
from .stil import Stil


def tuzak_mi(k: Kelime) -> bool:
    """Sözcük, sayıya benzeyen ama sayı olmayan bir biçim mi?"""
    return k.tuzak or k.kucuk in sozluk.SAYI_GIBI_TUZAKLAR


def ikileme_uzunlugu(ks: KelimeDizisi, i: int) -> int:
    """``i`` konumunda deyimsel bir ikileme varsa uzunluğunu döndürür."""
    for kaliplar in sozluk.IKILEMELER:
        n = len(kaliplar)
        if i + n > len(ks):
            continue
        if ks[i].kucuk != kaliplar[0]:
            continue
        if all(ks[i + j].kok == kaliplar[j] for j in range(n)):
            return n
    return 0


def bir_uygun(kural: str, adet: int, stil: Stil) -> bool:
    """Çıplak "bir" dönüştürülmeli mi?

    Varsayılan ("siki"): yalnızca açık sayı bağlamında (tarih, saat, yüzde,
    para, sıra sayısı) ya da çok sözcüklü sayı ifadesinin parçası olarak.
    "gevsek" kipinde her yerde dönüştürülür.
    """
    if stil.bir_baglami == "gevsek":
        return True
    if adet > 1:
        return True
    return kural in ("tarih", "saat", "yuzde", "para", "sira", "rakam_dizisi")


def yuz_uygun(kural: str, adet: int) -> bool:
    """Çıplak "yüz" (surat) dönüştürülmeli mi? Yalnızca açık bağlamda."""
    return adet > 1 or kural in ("tarih", "saat", "yuzde", "para", "birim")


_SAYI_ONEKLERI: tuple[str, ...] = tuple(
    sorted(set(sozluk.SAYI_SOZLERI) | set(sozluk.SIRA_OZEL), key=len, reverse=True)
)


def sayi_devami(k: Kelime | None) -> bool:
    """Sözcük, çözülememiş bir sayı gövdesinin devamı mı?

    "sekizlik", "yüzlü", "binlerce" gibi türemiş biçimler sayı sözüyle
    başlar ama sayı değildir. Böyle bir sözcük bir sayı ifadesinin hemen
    ardından geliyorsa ifade yarım bırakılır ("yüzde on sekizlik" ->
    "%10 sekizlik" olmaz).
    """
    if k is None or k.ek or k.tuzak:
        return False
    if k.kucuk in sozluk.SAYI_SOZLERI or k.kucuk in sozluk.SIRA_OZEL:
        return False
    return any(len(k.kucuk) > len(onek) and k.kucuk.startswith(onek) for onek in _SAYI_ONEKLERI)


def sira_engel(deger: int, sonraki: str | None) -> bool:
    """Sıra sayısı deyim oluşturuyor mu? ("ikinci el")"""
    if sonraki is None:
        return False
    return sonraki in sozluk.SIRA_ENGEL.get(str(deger), frozenset())


def baglam_ipucu(ks: KelimeDizisi, i: int, ipuclari: frozenset[str]) -> bool:
    """``i``den önceki iki sözcükten biri ipucu mu?"""
    return any(j >= 0 and ks[j].kok in ipuclari for j in (i - 1, i - 2))


def guven_ayarla(temel: float, belirsiz: bool) -> float:
    return temel if not belirsiz else round(temel * 0.75, 2)
