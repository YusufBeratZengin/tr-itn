"""Komut satırı arayüzü.

Kullanım::

    tr-itn metin.txt
    echo "yüzde on sekiz kdv" | tr-itn
    tr-itn --explain ornek.txt
    tr-itn --json - < ornek.txt
"""

from __future__ import annotations

import argparse
import contextlib
import json
import sys
from pathlib import Path

from . import __version__
from .alan import AlanSozlugu
from .motor import Sonuc, cevir_ayrintili
from .stil import Stil


def _stil(args: argparse.Namespace) -> Stil:
    binlik = {"yok": None, "nokta": ".", "virgul": ",", "bosluk": " "}[args.binlik]
    return Stil(
        ondalik_ayirici=args.ondalik,
        binlik_ayirici=binlik,
        para_sembolu=not args.para_adi,
        bir_baglami=args.bir,
        saat_kipi=args.saat_kipi,
        rakam_dizisi=args.rakam_dizisi,
        esik=args.esik,
    )


def _json_cikti(sonuc: Sonuc) -> str:
    return json.dumps(
        {
            "metin": sonuc.metin,
            "kurallar": [
                {
                    "kural": iz.kural,
                    "girdi": iz.girdi,
                    "cikti": iz.cikti,
                    "konum": list(iz.konum),
                    "guven": iz.guven,
                    "aciklama": iz.aciklama,
                }
                for iz in sonuc.izler
            ],
        },
        ensure_ascii=False,
        indent=2,
    )


def _aciklama(sonuc: Sonuc) -> str:
    satirlar = [sonuc.metin.rstrip(chr(10)), ""]
    if not sonuc.izler:
        satirlar.append("(dönüşüm yok)")
        return "\n".join(satirlar)
    satirlar.append(f"{'kural':<14}{'güven':<8}girdi -> çıktı")
    for iz in sonuc.izler:
        satirlar.append(f"{iz.kural:<14}{iz.guven:<8.2f}{iz.girdi} -> {iz.cikti}")
    return "\n".join(satirlar)


def _oku(kaynak: str) -> str:
    veri = sys.stdin.buffer.read() if kaynak == "-" else Path(kaynak).read_bytes()
    return veri.decode("utf-8", errors="replace")


def kur() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tr-itn",
        description="Türkçe ASR metnindeki sayı, tarih, saat, para ve birimleri yazı biçimine çevirir.",
    )
    p.add_argument("dosyalar", nargs="*", help="Girdi dosyaları; '-' veya boş = stdin")
    p.add_argument("--explain", action="store_true", help="kural izlerini de yazdır")
    p.add_argument("--json", action="store_true", help="JSON çıktı ver")
    p.add_argument("--ondalik", choices=[",", "."], default=",", help="ondalık ayırıcı")
    p.add_argument(
        "--binlik",
        choices=["yok", "nokta", "virgul", "bosluk"],
        default="yok",
        help="binlik ayırıcı",
    )
    p.add_argument("--para-adi", action="store_true", help="para birimini sembol yerine adla yaz")
    p.add_argument("--bir", choices=["siki", "gevsek"], default="siki", help='"bir" bağlam kipi')
    p.add_argument("--saat-kipi", action="store_true", help="bağlam olmadan da saat oku")
    p.add_argument("--rakam-dizisi", action="store_true", help="rakam dizisi kipi (telefon)")
    p.add_argument("--esik", type=int, default=0, help="bu değerden küçük sayıları çevirme")
    p.add_argument("--alan", metavar="DOSYA", help="alan sözlüğü (JSON veya basit YAML)")
    p.add_argument("--surum", "--version", action="version", version=f"tr-itn {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    for akis in (sys.stdout, sys.stderr):
        if hasattr(akis, "reconfigure"):
            with contextlib.suppress(ValueError, OSError):  # pragma: no cover - kapalı akış
                # newline="" stops the text layer from turning a CRLF in the input into CR CR LF.
                akis.reconfigure(encoding="utf-8", newline="")  # type: ignore[union-attr]
    args = kur().parse_args(argv)
    stil = _stil(args)
    alan: AlanSozlugu | None = None
    if args.alan:
        try:
            alan = AlanSozlugu.dosyadan(args.alan)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"tr-itn: {args.alan}: {exc}", file=sys.stderr)
            return 1
        for cakisma in alan.cakismalar:
            print(f"tr-itn: uyarı: '{cakisma}' yerleşik kuralı eziyor", file=sys.stderr)
    kaynaklar = args.dosyalar or ["-"]
    cikti: list[str] = []
    for kaynak in kaynaklar:
        try:
            metin = _oku(kaynak)
        except OSError as exc:
            print(f"tr-itn: {kaynak}: {exc}", file=sys.stderr)
            return 1
        sonuc = cevir_ayrintili(metin, stil, alan)
        if args.json:
            cikti.append(_json_cikti(sonuc))
        elif args.explain:
            cikti.append(_aciklama(sonuc))
        else:
            cikti.append(sonuc.metin)
    if len(cikti) == 1:
        sys.stdout.write(cikti[0])
    else:
        sys.stdout.write("\n".join(p.rstrip("\n") for p in cikti) + "\n")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
