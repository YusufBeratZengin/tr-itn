"""Alan sözlüğü: finans, tıp, hukuk gibi alanlara özel kısaltmalar.

Sözlük kuralları varsayılan davranışı ezer: "kdv" -> "KDV", "tl" -> "TL".
Çakışan (aynı girdiye iki farklı çıktı veren) kurallar yükleme anında hata
verir; yerleşik sayı sözcükleriyle çakışan kurallar ``cakismalar`` ile
bildirilir.

Dosya biçimleri::

    # JSON
    {"ad": "finans", "kurallar": {"kdv": "KDV", "tl": "TL"}}

    # Basit YAML alt kümesi (yalnız "girdi: çıktı" satırları ve # yorumları)
    kdv: KDV
    tl: TL
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path

from . import sozluk as _sozluk

#: Eşleştirmede aynı sınıfa giren Türkçe i ailesi.
_I_AILEYI = "iİIı"


def _turkce_kucult(metin: str) -> str:
    """Türkçe'ye duyarlı küçültme: ``İ`` -> ``i``, ``I`` -> ``ı``.

    ``str.lower()`` Türkçe değildir: ``"İ".lower()`` iki karakterli
    ``"i̇"`` üretir ve sözlük anahtarıyla eşleşmez. Ayrıca ayrışık
    (combining) yazımları da NFC ile birleştirip artık noktayı atarız.
    """
    metin = unicodedata.normalize("NFC", metin)
    metin = metin.replace("İ", "i").replace("I", "ı")
    metin = unicodedata.normalize("NFC", metin.lower())
    return metin.replace("\u0307", "")


def _ascii_kucult(metin: str) -> str:
    """Eşleştirme yedeği: i ailesinin tamamını ``i`` yapar.

    Türkçe küçültmede ``I`` -> ``ı`` olur; ASCII büyük ``I`` ile yazılmış
    bir sözcük (``ISTANBUL``) bu yüzden ``istanbul`` anahtarına ulaşamaz.
    Aynı yüzeyin ikinci okunuşu budur; anahtar araması ikisini de dener.
    """
    metin = unicodedata.normalize("NFC", metin)
    for harf in _I_AILEYI:
        metin = metin.replace(harf, "i")
    metin = unicodedata.normalize("NFC", metin.lower())
    return metin.replace("\u0307", "")


def _anahtar_adaylari(yuzey: str) -> tuple[str, ...]:
    """Bir eşleşmenin sözlükte aranacağı anahtar biçimleri (öncelik sırasıyla)."""
    turkce = _turkce_kucult(yuzey)
    ascii_ = _ascii_kucult(yuzey)
    if turkce == ascii_:
        return (turkce,)
    return (turkce, ascii_)


@dataclass
class AlanSozlugu:
    """Sıralı, en uzun eşleşmeyi tercih eden sözcük değiştirici."""

    ad: str = "alan"
    kurallar: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        temiz: dict[str, str] = {}
        for girdi, cikti in self.kurallar.items():
            anahtar = _turkce_kucult(girdi.strip())
            if not anahtar:
                raise ValueError("boş sözlük girdisi")
            if anahtar in temiz and temiz[anahtar] != cikti:
                raise ValueError(f"çakışan kural: {anahtar!r}")
            temiz[anahtar] = cikti
        self.kurallar = temiz
        self._desen = self._derle()

    def _derle(self) -> re.Pattern[str]:
        if not self.kurallar:
            return re.compile(r"(?!x)x")  # hiçbir şeyle eşleşmez
        anahtarlar = sorted(self.kurallar, key=len, reverse=True)
        govde = "|".join(re.escape(k) for k in anahtarlar)
        return re.compile(rf"(?<![^\W\d_])({govde})(?![^\W\d_])", re.IGNORECASE)

    def _cikti(self, yuzey: str) -> str | None:
        """Eşleşen yüzeyin sözlük çıktısı; hiçbir aday tutmazsa ``None``."""
        for aday in _anahtar_adaylari(yuzey):
            if aday in self.kurallar:
                return self.kurallar[aday]
        # Karışık i/ı ve Unicode harf çiftlerini desenle aynı kuralla çöz.
        for anahtar, cikti in self.kurallar.items():
            if re.fullmatch(re.escape(anahtar), yuzey, re.IGNORECASE):
                return cikti
        return None

    @property
    def cakismalar(self) -> list[str]:
        """Yerleşik sayı/tarih sözcükleriyle çakışan girdiler."""
        yerlesik = (
            set(_sozluk.SAYI_SOZLERI)
            | set(_sozluk.AYLAR)
            | set(_sozluk.PARA_BIRIMLERI)
            | set(_sozluk.BIRIMLER)
            | set(_sozluk.SIRA_OZEL)
        )
        return sorted(k for k in self.kurallar if k in yerlesik)

    def uygula(self, metin: str) -> str:
        if not self.kurallar:
            return metin

        def _degistir(eslesme: re.Match[str]) -> str:
            cikti = self._cikti(eslesme.group(1))
            return eslesme.group(0) if cikti is None else cikti

        return self._desen.sub(_degistir, metin)

    def uygula_korumali(self, metin: str) -> tuple[str, dict[str, str]]:
        """Değiştirir ve çıktıları yer tutucuyla korur.

        Sözlük çıktısı daha sonra sayı kuralına takılmasın diye geçici
        işaretler kullanılır; ``geri_yukle`` ile asıl metne dönülür.
        """
        if not self.kurallar:
            return metin, {}
        yer: dict[str, str] = {}

        def _degistir(eslesme: re.Match[str]) -> str:
            cikti = self._cikti(eslesme.group(1))
            if cikti is None:
                return eslesme.group(0)
            anahtar = f"\ue000{len(yer)}\ue001"
            yer[anahtar] = cikti
            return anahtar

        return self._desen.sub(_degistir, metin), yer

    @staticmethod
    def geri_yukle(metin: str, yer: dict[str, str]) -> str:
        for anahtar, deger in yer.items():
            metin = metin.replace(anahtar, deger)
        return metin

    def __len__(self) -> int:
        return len(self.kurallar)

    # --- yükleme ---------------------------------------------------------

    @classmethod
    def sozlukten(cls, veri: Mapping[str, object], ad: str = "alan") -> AlanSozlugu:
        kurallar = veri.get("kurallar", veri)
        if not isinstance(kurallar, Mapping):
            raise ValueError("'kurallar' bir nesne olmalı")
        ad = str(veri.get("ad", ad)) if "kurallar" in veri else ad
        return cls(ad=ad, kurallar={str(k): str(v) for k, v in kurallar.items()})

    @classmethod
    def dosyadan(cls, yol: str | Path) -> AlanSozlugu:
        yol = Path(yol)
        ham = yol.read_text(encoding="utf-8")
        if yol.suffix.lower() == ".json":
            return cls.sozlukten(json.loads(ham), ad=yol.stem)
        return cls(ad=yol.stem, kurallar=_basit_yaml(ham))

    @classmethod
    def kurallardan(cls, ciftler: Iterable[tuple[str, str]], ad: str = "alan") -> AlanSozlugu:
        return cls(ad=ad, kurallar=dict(ciftler))


def _basit_yaml(ham: str) -> dict[str, str]:
    """YAML'in yalnız ``anahtar: değer`` alt kümesini okur."""
    kurallar: dict[str, str] = {}
    for satir in ham.splitlines():
        s = satir.strip()
        if not s or s.startswith("#") or ":" not in s:
            continue
        anahtar, deger = s.split(":", 1)
        anahtar, deger = anahtar.strip().strip('"'), deger.strip().strip('"')
        if anahtar:
            kurallar[anahtar] = deger
    return kurallar
