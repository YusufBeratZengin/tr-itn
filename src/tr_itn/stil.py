"""Çıktı biçimi ayarları.

Varsayılanlar güvenli taraftadır: "bir" yalnızca açık sayı bağlamında
dönüştürülür (``bir_baglami="siki"``), binlik ayırıcı kullanılmaz, ondalık
ayırıcı Türkçe yazımdaki gibi virgüldür.
"""

from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Stil:
    """Dönüşüm davranışını belirleyen ayarlar."""

    #: Ondalık ayırıcı: "," (Türkçe) veya "."
    ondalik_ayirici: str = ","
    #: Binlik ayırıcı: None, "." veya " " (boşluk)
    binlik_ayirici: str | None = None
    #: Para birimi sembolü kullan ("150 TL", "$150"); False ise ad yazılır.
    para_sembolu: bool = True
    #: "siki": "bir" yalnızca açık sayı bağlamında; "gevsek": her yerde.
    bir_baglami: str = "siki"
    #: Bağlam sözcüğü olmadan da saat okuması yap ("on dört otuz" -> 14:30).
    saat_kipi: bool = False
    #: Rakam dizisi kipi ("sıfır beş üç..." -> 053...).
    rakam_dizisi: bool = False
    #: Ay adlarını büyük harfle yaz ("2 Kasım").
    ay_buyuk_harf: bool = True
    #: Bu değerden küçük sayılar yazı olarak bırakılır (0 = hepsi dönüşür).
    esik: int = 0
    #: Bu değerden büyük sayılar yazı olarak bırakılır (None = sınır yok).
    ust_sinir: int | None = None

    def __post_init__(self) -> None:
        if self.ondalik_ayirici not in (",", "."):
            raise ValueError("ondalik_ayirici ',' veya '.' olmalı")
        if self.binlik_ayirici not in (None, ".", ",", " "):
            raise ValueError("binlik_ayirici None, '.', ',' veya ' ' olmalı")
        if self.bir_baglami not in ("siki", "gevsek"):
            raise ValueError("bir_baglami 'siki' veya 'gevsek' olmalı")
        if self.esik < 0:
            raise ValueError("esik negatif olamaz")

    def ile(self, **degisiklikler: object) -> Stil:
        """Ayarların bir kopyasını değiştirerek döndürür."""
        return replace(self, **degisiklikler)  # type: ignore[arg-type]


VARSAYILAN = Stil()
