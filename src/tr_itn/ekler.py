"""Türkçe ek çözümleme ve ünlü uyumu.

ASR çıktısında sayı sözleri ek alabilir: "on dörtte", "otuzunda", "yirmi
altıya". Bu modül, bir sözcükten sayı kökünü ve eki ayırır; ek gerçekten
Türkçe ünlü uyumuna ve ünsüz sertleşmesine uyuyorsa kabul eder. Böylece
"altında" (alt+ında) yanlışlıkla "6'nda" olmaz.

Kurallar küçük harfli girdiyle çalışır; büyük/küçük harf çevrimi çağıranın
işidir.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

SESLILER = "aeıioöuü"
SERT_UNSUZLER = "pçtkfhsş"

# 4'lü uyum: son ünlü -> eklenecek ünlü
_DORTLU = {
    "a": "ı",
    "ı": "ı",
    "o": "u",
    "u": "u",
    "e": "i",
    "i": "i",
    "ö": "ü",
    "ü": "ü",
}

# 2'li uyum: son ünlü -> eklenecek ünlü
_IKILI = {
    "a": "a",
    "ı": "a",
    "o": "a",
    "u": "a",
    "e": "e",
    "i": "e",
    "ö": "e",
    "ü": "e",
}


def son_sesli(kelime: str) -> str | None:
    """Sözcüğün son ünlüsünü döndürür; hiç ünlü yoksa ``None``."""
    for harf in reversed(kelime):
        if harf in SESLILER:
            return harf
    return None


def unlu_ikili(kelime: str) -> str:
    """2'li ünlü uyumuna göre eklenecek ünlü ('a' veya 'e')."""
    v = son_sesli(kelime)
    return _IKILI.get(v, "e") if v else "e"


def unlu_dortlu(kelime: str) -> str:
    """4'lü ünlü uyumuna göre eklenecek ünlü ('ı','i','u','ü')."""
    v = son_sesli(kelime)
    return _DORTLU.get(v, "i") if v else "i"


def sert_mi(kelime: str) -> bool:
    """Sözcük sert ünsüzle mi bitiyor? (-da/-ta seçimi için)."""
    return bool(kelime) and kelime[-1] in SERT_UNSUZLER


def _d(kelime: str) -> str:
    return "t" if sert_mi(kelime) else "d"


def _sesli_mi(kelime: str) -> bool:
    return bool(kelime) and kelime[-1] in SESLILER


@dataclass(frozen=True)
class EkCozum:
    """Bir sözcüğün sayı kökü ve eki."""

    kok: str
    ek: str

    def __str__(self) -> str:  # pragma: no cover - kolaylık
        return f"{self.kok}+{self.ek}"


# --- Ek üretimi --------------------------------------------------------------
#
# Ekler sırayla eklenir: çoğul -> iyelik -> hâl -> koşaç. Her adım, o ana
# kadarki biçimin son sesine göre uyumlu biçimleri üretir.


def _hal_bicimleri(govde: str, iyelikten_sonra: bool = False) -> set[str]:
    """Hâl ekleri. ``iyelikten_sonra`` ise kaynaştırma 'n' biçimleri de üretilir.

    Kaynaştırma 'n' yalnızca iyelikten sonra geçerlidir: "yüzünde"
    (yüz+ü+nde) doğrudur, "altına" ise "alt" sözcüğüdür; bu yüzden çıplak
    köke 'n'li biçim eklenmez.
    """
    a2 = unlu_ikili(govde)
    a4 = unlu_dortlu(govde)
    d = _d(govde)
    n = "n" if (iyelikten_sonra and _sesli_mi(govde)) else ""
    return {
        d + a2,              # bulunma: -da/-de/-ta/-te
        n + d + a2,          # iyelikten sonra: -nda/-nde
        d + a2 + "n",        # ayrılma: -dan/-den
        n + d + a2 + "n",
        a2,                  # yönelme: -a/-e
        "y" + a2,
        n + a2,
        a4,                  # belirtme: -ı/-i/-u/-ü
        "y" + a4,
        n + a4,
        a4 + "n",            # tamlayan: -ın/-in
        n + a4 + "n",
        "l" + a2,            # vasıta: -la/-le
        "yl" + a2,
    }


def _iyelik_bicimleri(govde: str) -> set[str]:
    a4 = unlu_dortlu(govde)
    sesli = _sesli_mi(govde)
    s = "s" if sesli else ""
    bicimler = {
        s + a4,              # 3. tekil: -sı/-si/-sü
        "m",   # 1. tekil: -(ı)m / -m
        "n",   # 2. tekil: -(ı)n / -n
        ("" if sesli else a4) + "m" + a4 + "z",
        ("" if sesli else a4) + "n" + a4 + "z",
        "m" + a4 + "z",
        "n" + a4 + "z",
    }
    # Ünlüyle biten köke çıplak "m"/"n" eklenmez: "altı"+"n" -> "altın"
    # (altın madeni) yanlış çözümüne yol açar.
    if sesli:
        bicimler.discard("m")
        bicimler.discard("n")
    return bicimler


def _kosc_bicimleri(govde: str) -> set[str]:
    a4 = unlu_dortlu(govde)
    d = _d(govde)
    y = "y" if _sesli_mi(govde) else ""
    return {
        d + a4 + "r",        # -dır/-dir
        y + d + a4 + "r",
        y + d + a4,          # -ydı/-di (geçmiş)
        d + a4,
        y + "ken",           # -ken
        "ken",
        "ki",                # -ki
    }


def gecerli_ekler(kok: str) -> set[str]:
    """Bir köke eklenebilecek, uyum denetiminden geçmiş ekler.

    Dönen küme, tek ekler ve en çok üç parçalı zincirleri içerir
    ("da", "ndaki", "sındaydı" gibi).
    """
    tek: set[str] = set()
    tek |= _hal_bicimleri(kok)
    tek |= _iyelik_bicimleri(kok)
    tek |= _kosc_bicimleri(kok)
    tek.add("l" + unlu_ikili(kok) + "r")  # çoğul: -lar/-ler

    tum = set(tek)
    # çoğul + iyelik + hâl zincirleri
    for cogul in ("l" + unlu_ikili(kok) + "r",):
        govde = kok + cogul
        for iye in _iyelik_bicimleri(govde):
            g2 = govde + iye
            tum.add(cogul + iye)
            for hal in _hal_bicimleri(g2, iyelikten_sonra=True):
                tum.add(cogul + iye + hal)
                for kos in _kosc_bicimleri(g2 + hal):
                    tum.add(cogul + iye + hal + kos)
    # iyelik + hâl (+ koşaç)
    for iye in _iyelik_bicimleri(kok):
        g2 = kok + iye
        for hal in _hal_bicimleri(g2, iyelikten_sonra=True):
            tum.add(iye + hal)
            for kos in _kosc_bicimleri(g2 + hal):
                tum.add(iye + hal + kos)
    # hâl + koşaç / -ki
    for hal in _hal_bicimleri(kok):
        g2 = kok + hal
        for kos in _kosc_bicimleri(g2):
            tum.add(hal + kos)
    return {e for e in tum if e}


# Önbellek: aynı kök için ek kümesi tekrar tekrar üretilmesin.
_EK_ONBELLEK: dict[str, set[str]] = {}


def ekler(kok: str) -> set[str]:
    if kok not in _EK_ONBELLEK:
        _EK_ONBELLEK[kok] = gecerli_ekler(kok)
    return _EK_ONBELLEK[kok]


def ek_cozumle(kelime: str, kokler: frozenset[str] | set[str] | dict[str, object]) -> EkCozum | None:
    """``kelime``yi kök + ek olarak çözer; kök ``kokler`` içinde olmalı.

    En kısa ekten başlar; böylece "otuzunda" -> ("otuz", "unda") bulunurken
    "altında" gibi sayı olmayan sözcükler çözülmez.
    """
    if not kelime:
        return None
    if kelime in kokler:
        return EkCozum(kelime, "")
    for n in range(1, min(9, len(kelime))):
        kok = kelime[:-n]
        if kok not in kokler:
            continue
        ek = kelime[-n:]
        if ek in ekler(kok):
            return EkCozum(kok, ek)
    return None


def ekle_yaz(metin: str, ek: str) -> str:
    """Yazıya çevrilmiş sayıya eki kesme işaretiyle ekler: 14:30 + da -> 14:30'da."""
    if not ek:
        return metin
    return f"{metin}'{ek}"


# --- Ek türü ve yeniden üretim ----------------------------------------------
#
# Kısaltma ve semboller yazıldığı gibi değil, okunduğu gibi ek alır:
# "kilometreye" -> "km'ye", "liraya" -> "TL'ye". Bunun için ekin dilbilgisel
# türünü bulup hedef okunuşa göre yeniden üretiyoruz.

def _a2(k: str) -> str:
    return unlu_ikili(k)


def _a4(k: str) -> str:
    return unlu_dortlu(k)


def _y(k: str) -> str:
    return "y" if _sesli_mi(k) else ""


def _n(k: str) -> str:
    return "n" if _sesli_mi(k) else ""


#: tür -> (tek biçim üreteci, sınıflandırma için ek biçimler)
_EK_URETICILER: dict[str, tuple[Callable[[str], str], Callable[[str], set[str]]]] = {
    "loc": (lambda k: _d(k) + _a2(k), lambda k: {_d(k) + _a2(k), "n" + _d(k) + _a2(k)}),
    "abl": (lambda k: _d(k) + _a2(k) + "n", lambda k: {_d(k) + _a2(k) + "n"}),
    "dat": (lambda k: _y(k) + _a2(k), lambda k: {_a2(k), _y(k) + _a2(k)}),
    "acc": (lambda k: _y(k) + _a4(k), lambda k: {_a4(k), _y(k) + _a4(k)}),
    "gen": (lambda k: _n(k) + _a4(k) + "n", lambda k: {_a4(k) + "n", _n(k) + _a4(k) + "n"}),
    "ins": (lambda k: _y(k) + "l" + _a2(k), lambda k: {"l" + _a2(k), _y(k) + "l" + _a2(k)}),
    "plu": (lambda k: "l" + _a2(k) + "r", lambda k: {"l" + _a2(k) + "r"}),
    "poss3": (lambda k: ("s" if _sesli_mi(k) else "") + _a4(k), lambda k: {_a4(k), "s" + _a4(k)}),
    "poss1s": (lambda k: ("m" if _sesli_mi(k) else _a4(k) + "m"), lambda k: {"m", _a4(k) + "m"}),
    "poss1p": (
        lambda k: ("m" if _sesli_mi(k) else _a4(k) + "m") + _a4(k) + "z",
        lambda k: {"m" + _a4(k) + "z", _a4(k) + "m" + _a4(k) + "z"},
    ),
    "dir": (lambda k: _d(k) + _a4(k) + "r", lambda k: {_d(k) + _a4(k) + "r", _y(k) + _d(k) + _a4(k) + "r"}),
    "ydi": (lambda k: _y(k) + _d(k) + _a4(k), lambda k: {_d(k) + _a4(k), _y(k) + _d(k) + _a4(k)}),
    "ki": (lambda k: "ki", lambda k: {"ki"}),
}


def ek_turu(kok: str, ek: str) -> str | None:
    """Ekin dilbilgisel türünü bulur: "lira"+"ya" -> "dat"."""
    for tur, (_, bicimler) in _EK_URETICILER.items():
        if ek in bicimler(kok):
            return tur
    return None


def ek_uret(kok: str, tur: str) -> str:
    """Verilen kök ve tür için uyumlu tek eki üretir: ("tele","dat") -> "ye"."""
    giris = _EK_URETICILER.get(tur)
    if giris is None:
        return ""
    return str(giris[0](kok))
