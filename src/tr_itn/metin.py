"""Metni parçalara ayırma ve sözcük çözümleme.

Girdi, boşluk ve noktalama korunarak parçalanır; yalnızca sözcük parçaları
dönüştürülür. Her sözcük için kök ve ek bir kez çözülür, böylece kurallar
aynı işi tekrar etmez.
"""

from __future__ import annotations

import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass

from . import sozluk
from .ekler import ek_cozumle

#: Harf, rakam, boşluk ve diğer (noktalama) parçaları.
_PARCALAR = re.compile(r"\d+|[^\W\d_]+|\s+|[^\w\s]", re.UNICODE)

KELIME = "kelime"
BOSLUK = "bosluk"
DIGER = "diger"

#: Türkçe küçük harfe çevirme ("İ" -> "i", "I" -> "ı").
_TR_KUCUK = str.maketrans({"İ": "i", "I": "ı"})

#: Satır/sayfa ayırıcıları. Çok sözcüklü bir kuralın sözcükleri arasında
#: köprü olamazlar; ``\s`` bunları boşluk saydığı için ayrıca elenirler.
SATIR_AYIRICILARI = frozenset("\n\r\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029")


def satir_ayirici_var(metin: str) -> bool:
    """Metinde satır/sayfa ayırıcı bir karakter var mı?"""
    return any(harf in SATIR_AYIRICILARI for harf in metin)


_KOKLER: frozenset[str] = frozenset(
    set(sozluk.SAYI_SOZLERI)
    | set(sozluk.SIRA_OZEL)
    | set(sozluk.AYLAR)
    | set(sozluk.PARA_BIRIMLERI)
    | set(sozluk.BIRIMLER)
    | set(sozluk.DAKIKA_ONEKLERI)
)


@dataclass(frozen=True)
class Parca:
    metin: str
    tip: str
    bas: int


@dataclass(frozen=True)
class Kelime:
    """Bir sözcük parçasının çözümlenmiş hâli."""

    sira: int          # parça listesindeki indeks
    metin: str         # özgün metin
    kucuk: str         # küçültülmüş, ASCII düzeltmesi yapılmış hâli
    kok: str
    ek: str
    tuzak: bool = False

    @property
    def ekli_mi(self) -> bool:
        return bool(self.ek)


@dataclass(frozen=True)
class Eslesme:
    """Bir kuralın ürettiği değiştirme."""

    metin: str
    adet: int
    kural: str
    guven: float = 1.0
    aciklama: str = ""


class KelimeDizisi(Sequence[Kelime]):
    """Kelimeler + bir kez hesaplanmış kök listesi.

    Kurallar her sözcükte yeniden kök listesi üretmesin diye kullanılır.
    """

    __slots__ = ("_kelimeler", "koklar")

    def __init__(self, kelimeler_: list[Kelime]) -> None:
        self._kelimeler = kelimeler_
        self.koklar = [k.kok for k in kelimeler_]

    def __getitem__(self, indeks: int) -> Kelime:  # type: ignore[override]
        return self._kelimeler[indeks]

    def __len__(self) -> int:
        return len(self._kelimeler)

    def __iter__(self) -> Iterator[Kelime]:
        return iter(self._kelimeler)


def kucult(metin: str) -> str:
    return metin.translate(_TR_KUCUK).lower()


def ilk_buyuk(metin: str) -> str:
    """Türkçe kurallarına uygun ilk harf büyütme: "kasım" -> "Kasım"."""
    if not metin:
        return metin
    ilk = metin[0]
    buyuk = {"i": "İ", "ı": "I"}.get(ilk, ilk.upper())
    return buyuk + metin[1:]


def parcala(metin: str) -> list[Parca]:
    parcalar: list[Parca] = []
    for m in _PARCALAR.finditer(metin):
        parca = m.group(0)
        if parca.isspace():
            tip = BOSLUK
        elif parca[0].isalpha():
            tip = KELIME
        else:
            tip = DIGER
        parcalar.append(Parca(parca, tip, m.start()))
    return parcalar


def kelimeler(parcalar: list[Parca]) -> list[Kelime]:
    sonuc: list[Kelime] = []
    for sira, parca in enumerate(parcalar):
        if parca.tip != KELIME:
            continue
        kucuk = kucult(parca.metin)
        kucuk = sozluk.ASCII_DUZELTME.get(kucuk, kucuk)
        if kucuk in sozluk.SAYI_GIBI_TUZAKLAR:
            sonuc.append(Kelime(sira, parca.metin, kucuk, kucuk, "", True))
            continue
        cozum = ek_cozumle(kucuk, _KOKLER)
        if cozum is None:
            sonuc.append(Kelime(sira, parca.metin, kucuk, kucuk, ""))
        else:
            sonuc.append(Kelime(sira, parca.metin, kucuk, cozum.kok, cozum.ek))
    return sonuc


def koklar(ks: list[Kelime]) -> list[str]:
    return [k.kok for k in ks]
