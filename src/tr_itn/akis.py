"""Akış kipi: parça parça gelen ASR metni.

ASR çıktısı genelde kelime kelime gelir; "iki bin" ile "yirmi altı" ayrı
parçalarda düşerse sayı bölünmemelidir. Bu modül, tamponun sonundaki sayı
sözcüklerini ve yarım kalmış sözcüğü tutar; kararlı kısmı hemen çevirir.

>>> a = Akis()
>>> a.besle("toplantı iki bin")
'toplantı '
>>> a.besle(" yirmi altı")
''
>>> a.bitir()
'2026'
"""

from __future__ import annotations

from . import sozluk
from .metin import KELIME, Kelime, kelimeler, parcala
from .motor import cevir
from .stil import Stil


def _tutulur(k: Kelime) -> bool:
    return (
        k.kok in sozluk.SAYI_SOZLERI
        or k.kok in sozluk.SIRA_OZEL
        or k.kok in sozluk.AYLAR
        or k.kucuk in ("buçuk", "çeyrek", "virgül", "nokta", "yüzde", "saat")
    )


class Akis:
    """Parça parça beslenen metni güvenli biçimde dönüştürür."""

    def __init__(self, stil: Stil | None = None) -> None:
        self.stil = stil
        self._tampon = ""

    @property
    def tampon(self) -> str:
        """Henüz çıkarılmamış metin."""
        return self._tampon

    def besle(self, parca: str) -> str:
        """Yeni parçayı ekler, çevrilebilir kararlı kısmı döndürür."""
        if not isinstance(parca, str):
            raise TypeError("parca str olmalı")
        self._tampon += parca
        p = parcala(self._tampon)
        if not p:
            return ""
        kes = len(self._tampon)
        if p[-1].tip == KELIME:
            kes = p[-1].bas  # yarım kalmış sözcük
        ks = kelimeler(p)
        j = len(ks)
        while j > 0 and p[ks[j - 1].sira].bas >= kes:
            j -= 1
        while j > 0 and _tutulur(ks[j - 1]):
            kes = p[ks[j - 1].sira].bas
            j -= 1
        govde, kuyruk = self._tampon[:kes], self._tampon[kes:]
        self._tampon = kuyruk
        return cevir(govde, self.stil) if govde else ""

    def bitir(self) -> str:
        """Tamponda kalan metni çevirip boşaltır."""
        kalan, self._tampon = self._tampon, ""
        return cevir(kalan, self.stil) if kalan else ""
