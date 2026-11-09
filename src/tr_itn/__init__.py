"""tr-itn: Türkçe konuşma metni için ters metin normalleştirme.

>>> from tr_itn import cevir
>>> cevir("yüzde on sekiz kdv")
'%18 kdv'
"""

from __future__ import annotations

from .akis import Akis
from .alan import AlanSozlugu
from .altyazi import srt_cevir, vtt_cevir
from .motor import KuralIzi, Sonuc, acikla, cevir, cevir_ayrintili
from .sayi import Deger
from .stil import Stil

__version__ = "0.1.0"
__all__ = [
    "Akis",
    "AlanSozlugu",
    "Deger",
    "KuralIzi",
    "Sonuc",
    "Stil",
    "__version__",
    "acikla",
    "cevir",
    "cevir_ayrintili",
    "srt_cevir",
    "vtt_cevir",
]
