"""Dönüşüm motoru: metni tarar, kuralları sırayla dener.

Sıra önemlidir: daha özgül kurallar (yüzde, saat, tarih, para, birim, sıra
sayısı) genel kardinal kuralından önce gelir. Bir kural eşleşmezse sözcük
olduğu gibi bırakılır; hiçbir durumda girdi bozulmaz.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from . import birim, para, saat, sayi, sozluk, tarih
from .alan import AlanSozlugu
from .baglam import baglam_ipucu, ikileme_uzunlugu, sayi_devami, tuzak_mi
from .metin import BOSLUK, Eslesme, KelimeDizisi, Parca, kelimeler, parcala, satir_ayirici_var
from .stil import VARSAYILAN, Stil


@dataclass(frozen=True)
class KuralIzi:
    """Tek bir dönüşümün açıklaması."""

    kural: str
    girdi: str
    cikti: str
    konum: tuple[int, int]
    guven: float
    aciklama: str = ""


@dataclass
class Sonuc:
    metin: str
    izler: list[KuralIzi] = field(default_factory=list)


def _rakam_dizisi(ks: KelimeDizisi, i: int, stil: Stil) -> Eslesme | None:
    if not (stil.rakam_dizisi or baglam_ipucu(ks, i, sozluk.RAKAM_IPUCLARI)):
        return None
    j = i
    rakamlar: list[str] = []
    while (
        j < len(ks)
        and ks[j].kok in sozluk.BIRLER
        and not ks[j].ek
        and not tuzak_mi(ks[j])
    ):
        rakamlar.append(str(sozluk.BIRLER[ks[j].kok]))
        j += 1
    if len(rakamlar) < 4:
        return None
    return Eslesme(metin="".join(rakamlar), adet=len(rakamlar), kural="rakam_dizisi", guven=0.9)


def _dene(ks: KelimeDizisi, i: int, stil: Stil) -> Eslesme | None:
    for kural in (
        _rakam_dizisi,
        sayi.yuzde_esle,
        saat.coz,
        tarih.coz,
        para.coz,
        birim.coz,
        sayi.sira_esle,
        sayi.kardinal_esle,
    ):
        eslesme = kural(ks, i, stil)
        if eslesme is not None:
            return eslesme
    return None


def _uygula(parcalar: list[Parca], ks: KelimeDizisi, i: int, adet: int, metin: str) -> None:
    ilk = ks[i].sira
    son = ks[i + adet - 1].sira
    parcalar[ilk] = replace(parcalar[ilk], metin=metin)
    for idx in range(ilk + 1, son + 1):
        parcalar[idx] = replace(parcalar[idx], metin="")


def _boslukla_ayrili(parcalar: list[Parca], ks: KelimeDizisi, i: int, adet: int) -> bool:
    """Eşleşen sözcükler arasında yalnız boşluk mu var?

    Çok sözcüklü bir kural, araya giren rakamı, noktalamayı ya da satır
    sonunu göremez; böyle bir aralığı dönüştürmek veri kaybına yol açar.
    Yalnızca boşluk (satır/sayfa ayırıcıları hariç) köprüsü olan eşleşmeler
    güvenlidir.
    """
    for k in range(adet - 1):
        a = ks[i + k].sira
        b = ks[i + k + 1].sira
        for idx in range(a + 1, b):
            parca = parcalar[idx]
            if parca.tip != BOSLUK or satir_ayirici_var(parca.metin):
                return False
    return True


def cevir_ayrintili(
    metin: str, stil: Stil | None = None, alan: AlanSozlugu | None = None
) -> Sonuc:
    """Metni dönüştürür ve kural izlerini döndürür.

    ``alan`` verilirse önce alan sözlüğü uygulanır; izlerdeki konumlar bu
    ön geçişten sonraki metne göredir.
    """
    if not isinstance(metin, str):
        raise TypeError("metin str olmalı")
    s = stil if stil is not None else VARSAYILAN
    yer: dict[str, str] = {}
    if alan is not None:
        metin, yer = alan.uygula_korumali(metin)
    parcalar = parcala(metin)
    ks = KelimeDizisi(kelimeler(parcalar))
    izler: list[KuralIzi] = []
    i = 0
    while i < len(ks):
        atla = ikileme_uzunlugu(ks, i)
        if atla:
            i += atla
            continue
        if tuzak_mi(ks[i]) and not baglam_ipucu(ks, i, sozluk.SAAT_IPUCLARI):
            i += 1
            continue
        eslesme = _dene(ks, i, s)
        if eslesme is not None and (
            sayi_devami(ks[i + eslesme.adet] if i + eslesme.adet < len(ks) else None)
            or not _boslukla_ayrili(parcalar, ks, i, eslesme.adet)
        ):
            eslesme = None
        if eslesme is None:
            # Eşleşmeyen bitişik sayı sözleri ("on dört otuz") yarım
            # dönüştürülmesin: dizinin tamamı olduğu gibi bırakılır.
            if ks[i].kok in sozluk.SAYI_SOZLERI:
                while i + 1 < len(ks) and ks[i + 1].kok in sozluk.SAYI_SOZLERI:
                    i += 1
            i += 1
            continue
        ilk = ks[i].sira
        son = ks[i + eslesme.adet - 1].sira
        bas = parcalar[ilk].bas
        bitis = parcalar[son].bas + len(parcalar[son].metin)
        izler.append(
            KuralIzi(
                kural=eslesme.kural,
                girdi=metin[bas:bitis],
                cikti=eslesme.metin,
                konum=(bas, bitis),
                guven=eslesme.guven,
                aciklama=eslesme.aciklama,
            )
        )
        _uygula(parcalar, ks, i, eslesme.adet, eslesme.metin)
        i += eslesme.adet
    son_metin = "".join(p.metin for p in parcalar)
    if yer:
        son_metin = AlanSozlugu.geri_yukle(son_metin, yer)
        izler = [
            replace(
                iz,
                girdi=AlanSozlugu.geri_yukle(iz.girdi, yer),
                cikti=AlanSozlugu.geri_yukle(iz.cikti, yer),
            )
            for iz in izler
        ]
    return Sonuc(metin=son_metin, izler=izler)


def cevir(metin: str, stil: Stil | None = None, alan: AlanSozlugu | None = None) -> str:
    """ASR metnini yazı biçimine çevirir.

    Kapsam dışı ya da çözülemeyen girdi olduğu gibi döner; işlev fırlatmaz.
    """
    try:
        return cevir_ayrintili(metin, stil, alan).metin
    except TypeError:
        raise
    except Exception:  # pragma: no cover - güvenlik ağı
        return metin


def acikla(metin: str, stil: Stil | None = None, alan: AlanSozlugu | None = None) -> list[KuralIzi]:
    """Yalnızca kural izlerini döndürür."""
    return cevir_ayrintili(metin, stil, alan).izler
