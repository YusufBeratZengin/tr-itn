"""Komut satırı arayüzü testleri (gerçek alt süreç ile)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parents[1]


def _calistir(*args: str, girdi: bytes = b"") -> subprocess.CompletedProcess[bytes]:
    ortam = dict(os.environ)
    ortam["PYTHONPATH"] = str(KOK / "src")
    ortam["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, "-m", "tr_itn", *args],
        input=girdi,
        capture_output=True,
        env=ortam,
        cwd=KOK,
        timeout=120,
    )


def _metin(sonuc: subprocess.CompletedProcess[bytes]) -> str:
    """Alt sürecin stdout metni, satır sonları olduğu gibi (normalleştirme yok)."""
    return sonuc.stdout.decode("utf-8")


def test_stdin() -> None:
    sonuc = _calistir(girdi="yüzde on sekiz kdv\n".encode())
    assert sonuc.returncode == 0
    assert _metin(sonuc) == "%18 kdv\n"


def test_tire_stdin() -> None:
    sonuc = _calistir("-", girdi="üçüncü\n".encode())
    assert sonuc.returncode == 0
    assert _metin(sonuc) == "3.\n"


def test_dosya(tmp_path: Path) -> None:
    dosya = tmp_path / "girdi.txt"
    dosya.write_text(
        "toplantı iki kasım iki bin yirmi altı saat on dört otuzda\n",
        encoding="utf-8",
        newline="\n",
    )
    sonuc = _calistir(str(dosya))
    assert sonuc.returncode == 0
    assert _metin(sonuc) == "toplantı 2 Kasım 2026 saat 14:30'da\n"


def test_iki_dosya(tmp_path: Path) -> None:
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("üç\n", encoding="utf-8", newline="\n")
    b.write_text("beş\n", encoding="utf-8", newline="\n")
    sonuc = _calistir(str(a), str(b))
    assert sonuc.returncode == 0
    assert _metin(sonuc) == "3\n5\n"


def test_explain() -> None:
    sonuc = _calistir("--explain", girdi="yüzde on sekiz kdv\n".encode())
    cikti = _metin(sonuc)
    assert sonuc.returncode == 0
    assert "%18 kdv" in cikti
    assert "yuzde" in cikti


def test_explain_donusum_yok() -> None:
    sonuc = _calistir("--explain", girdi=b"merhaba\n")
    assert "(dönüşüm yok)" in _metin(sonuc)


def test_json() -> None:
    sonuc = _calistir("--json", girdi="üçüncü\n".encode())
    veri = json.loads(_metin(sonuc))
    assert veri["metin"] == "3.\n"
    assert veri["kurallar"][0]["kural"] == "sira"
    assert veri["kurallar"][0]["guven"] > 0


def test_olmayan_dosya() -> None:
    sonuc = _calistir("yok-boyle-bir-dosya.txt")
    assert sonuc.returncode == 1
    assert b"tr-itn:" in sonuc.stderr


def test_surum() -> None:
    sonuc = _calistir("--surum")
    assert sonuc.returncode == 0
    assert b"0.1.0" in sonuc.stdout


def test_esik_secenegi() -> None:
    sonuc = _calistir("--esik", "10", girdi="beş kişi ve on kişi\n".encode())
    assert _metin(sonuc) == "beş kişi ve 10 kişi\n"


def test_binlik_secenegi() -> None:
    sonuc = _calistir("--binlik", "nokta", girdi="iki bin yirmi altı\n".encode())
    assert _metin(sonuc) == "2.026\n"


def test_ondalik_secenegi() -> None:
    sonuc = _calistir("--ondalik", ".", girdi="üç virgül beş\n".encode())
    assert _metin(sonuc) == "3.5\n"


def test_rakam_dizisi_secenegi() -> None:
    metin = "sıfır beş üç iki bir iki üç dört\n"
    sonuc = _calistir("--rakam-dizisi", girdi=metin.encode())
    assert _metin(sonuc) == "05321234\n"


def test_saat_kipi_secenegi() -> None:
    sonuc = _calistir("--saat-kipi", girdi="on dört otuz\n".encode())
    assert _metin(sonuc) == "14:30\n"


def test_para_adi_secenegi() -> None:
    sonuc = _calistir("--para-adi", girdi="yüz elli lira\n".encode())
    assert _metin(sonuc) == "150 lira\n"


def test_bir_gevsek_secenegi() -> None:
    sonuc = _calistir("--bir", "gevsek", girdi="bir gün gelecek\n".encode())
    assert _metin(sonuc) == "1 gün gelecek\n"


def test_bos_girdi() -> None:
    sonuc = _calistir(girdi=b"")
    assert sonuc.returncode == 0
    assert sonuc.stdout == b""


def test_gecersiz_bayrak() -> None:
    sonuc = _calistir("--boyle-bir-bayrak-yok")
    assert sonuc.returncode == 2


def test_bozuk_utf8(tmp_path: Path) -> None:
    dosya = tmp_path / "bozuk.txt"
    dosya.write_bytes(b"\xff\xfe\x00bozuk")
    sonuc = _calistir(str(dosya))
    assert sonuc.returncode == 0


@pytest.mark.parametrize("bayrak", ["--explain", "--json"])
def test_uzun_metin(bayrak: str) -> None:
    metin = ("iki kasım iki bin yirmi altı saat on dört otuzda " * 200).encode()
    sonuc = _calistir(bayrak, girdi=metin)
    assert sonuc.returncode == 0
    assert sonuc.stdout


def test_alan_sozlugu_uygulanir() -> None:
    sonuc = _calistir("--alan", "ornekler/alan_finans.json", "ornekler/toplanti.txt")
    assert sonuc.returncode == 0
    cikti = _metin(sonuc)
    assert "2 Kasım 2026 saat 14:30'da" in cikti
    assert "%18 KDV" in cikti
    # Yerleşik sözcükle çakışan kural sessizce uygulanmaz, bildirilir.
    assert b"uyar" in sonuc.stderr.lower()
    assert b"tl" in sonuc.stderr


def test_alan_yaml_sozlugu(tmp_path: Path) -> None:
    sozluk = tmp_path / "tip.yaml"
    sozluk.write_text("# yorum\nmr: MR\n", encoding="utf-8", newline="\n")
    sonuc = _calistir("--alan", str(sozluk), girdi="mr çekildi\n".encode())
    assert sonuc.returncode == 0
    assert _metin(sonuc) == "MR çekildi\n"


def test_alan_bozuk_json(tmp_path: Path) -> None:
    dosya = tmp_path / "bozuk.json"
    dosya.write_text("{bu json degil", encoding="utf-8", newline="\n")
    sonuc = _calistir("--alan", str(dosya), girdi="üç\n".encode())
    assert sonuc.returncode == 1
    assert b"bozuk.json" in sonuc.stderr


def test_alan_olmayan_dosya() -> None:
    sonuc = _calistir("--alan", "yok-boyle-bir-sozluk.json", girdi="üç\n".encode())
    assert sonuc.returncode == 1
    assert b"tr-itn:" in sonuc.stderr


@pytest.mark.parametrize("girdi", ["ISTANBUL üç", "İstanbul üç", "istanbul üç"])
def test_alan_turkce_buyuk_harf_cli(tmp_path: Path, girdi: str) -> None:
    """İ/I içeren alan sözlüğü CLI'yi KeyError ile düşürmemeli."""
    sozluk = tmp_path / "alan.json"
    sozluk.write_text(
        json.dumps({"kurallar": {"istanbul": "X"}}, ensure_ascii=False), encoding="utf-8"
    )
    sonuc = _calistir("--alan", str(sozluk), girdi=f"{girdi}\n".encode())
    assert sonuc.returncode == 0
    assert _metin(sonuc) == "X 3\n"


def test_crlf_girdi_stdin_cr_cr_lf_uretmez() -> None:
    """CRLF girdi CRLF çıktı verir; Windows'ta CR CR LF üretilmemeli."""
    sonuc = _calistir(girdi="yüzde on sekiz kdv\r\niki bin\r\n".encode())
    assert sonuc.returncode == 0
    assert sonuc.stdout == b"%18 kdv\r\n2000\r\n"


def test_crlf_girdi_dosya_cr_cr_lf_uretmez(tmp_path: Path) -> None:
    dosya = tmp_path / "crlf.txt"
    dosya.write_bytes("yüzde on sekiz kdv\r\niki bin\r\n".encode())
    sonuc = _calistir(str(dosya))
    assert sonuc.returncode == 0
    assert sonuc.stdout == b"%18 kdv\r\n2000\r\n"
    assert b"\r\r" not in sonuc.stdout
