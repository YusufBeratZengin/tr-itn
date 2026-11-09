"""Ölçüm yardımcıları: normalize ederek WER.

ASR değerlendirmesinde ham WER, sayılar yazıyla geldiğinde olduğundan kötü
görünür ("14:30" yerine "on dört otuz"). Bu modül, ITN uygulanmış hipotez ile
referans arasındaki WER'i ham hâliyle karşılaştırır.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from .motor import cevir
from .stil import Stil


def duzenleme_mesafesi(a: list[str], b: list[str]) -> int:
    """Levenshtein mesafesi (kelime düzeyinde)."""
    if not a:
        return len(b)
    if not b:
        return len(a)
    onceki = list(range(len(b) + 1))
    for i, kelime_a in enumerate(a, 1):
        simdiki = [i]
        for j, kelime_b in enumerate(b, 1):
            maliyet = 0 if kelime_a == kelime_b else 1
            simdiki.append(
                min(onceki[j] + 1, simdiki[j - 1] + 1, onceki[j - 1] + maliyet)
            )
        onceki = simdiki
    return onceki[-1]


def wer(referans: str, hipotez: str) -> float:
    """Kelime hata oranı; referans boşsa 0.0 döner."""
    ref = referans.split()
    if not ref:
        return 0.0
    return duzenleme_mesafesi(ref, hipotez.split()) / len(ref)


@dataclass(frozen=True)
class WerRaporu:
    kayit_sayisi: int
    once: float
    sonra: float

    @property
    def fark(self) -> float:
        return self.once - self.sonra


def rapor(kayitlar: Iterable[Mapping[str, str]], stil: Stil | None = None) -> WerRaporu:
    """Kayıtlar üzerinde ham ve ITN sonrası ortalama WER."""
    once_toplam = 0.0
    sonra_toplam = 0.0
    adet = 0
    for kayit in kayitlar:
        referans = kayit["referans"]
        hipotez = kayit["hipotez"]
        once_toplam += wer(referans, hipotez)
        sonra_toplam += wer(referans, cevir(hipotez, stil))
        adet += 1
    if not adet:
        return WerRaporu(0, 0.0, 0.0)
    return WerRaporu(adet, once_toplam / adet, sonra_toplam / adet)
