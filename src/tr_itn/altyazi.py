"""SRT/VTT altyazı filtresi.

Zaman damgalarına ve sıra numaralarına dokunmaz; yalnızca metin satırlarını
dönüştürür. Böylece ASR çıktısından üretilmiş bir altyazı dosyası tek
komutla okunur biçime gelir.
"""

from __future__ import annotations

from .motor import cevir
from .stil import Stil

_ATLANAN_ONEKLER = ("WEBVTT", "NOTE", "STYLE", "REGION", "X-TIMESTAMP")


def _cevrilecek_mi(satir: str, numara: bool) -> bool:
    s = satir.strip()
    if not s:
        return False
    if "-->" in s:
        return False
    if numara and s.isdigit():
        return False
    return not s.upper().startswith(_ATLANAN_ONEKLER)


def zaman_damgali_cevir(metin: str, stil: Stil | None = None) -> str:
    """SRT/VTT metnini satır satır çevirir; yapıyı korur."""
    satirlar = metin.splitlines(keepends=True)
    cikti: list[str] = []
    for i, satir in enumerate(satirlar):
        govde = satir.rstrip("\r\n")
        son = satir[len(govde) :]
        # SRT'de sıra numarası, kendisinden sonra zaman damgası gelen satırdır.
        numara = govde.strip().isdigit() and i + 1 < len(satirlar) and "-->" in satirlar[i + 1]
        if _cevrilecek_mi(govde, numara):
            cikti.append(cevir(govde, stil) + son)
        else:
            cikti.append(satir)
    return "".join(cikti)


def srt_cevir(metin: str, stil: Stil | None = None) -> str:
    """SRT dosyası için kısayol."""
    return zaman_damgali_cevir(metin, stil)


def vtt_cevir(metin: str, stil: Stil | None = None) -> str:
    """WebVTT dosyası için kısayol."""
    return zaman_damgali_cevir(metin, stil)
