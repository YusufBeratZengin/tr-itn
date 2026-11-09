"""CLI'nin süreç içi (kapsam ölçülebilir) testleri."""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from tr_itn import cli


def _stdin(metin: str, monkeypatch: pytest.MonkeyPatch) -> None:
    sahte = SimpleNamespace(buffer=io.BytesIO(metin.encode("utf-8")))
    monkeypatch.setattr(sys, "stdin", sahte)


def test_main_stdin(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _stdin("üç kilometre\n", monkeypatch)
    assert cli.main([]) == 0
    assert capsys.readouterr().out == "3 km\n"


def test_main_dosya(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    dosya = tmp_path / "g.txt"
    dosya.write_text("yüzde elli\n", encoding="utf-8", newline="\n")
    assert cli.main([str(dosya)]) == 0
    assert capsys.readouterr().out == "%50\n"


def test_main_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    dosya = tmp_path / "g.txt"
    dosya.write_text("ikinci\n", encoding="utf-8", newline="\n")
    assert cli.main(["--json", str(dosya)]) == 0
    veri = json.loads(capsys.readouterr().out)
    assert veri["metin"] == "2.\n"
    assert veri["kurallar"][0]["kural"] == "sira"


def test_main_explain(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    dosya = tmp_path / "g.txt"
    dosya.write_text("üçüncü\n", encoding="utf-8", newline="\n")
    assert cli.main(["--explain", str(dosya)]) == 0
    assert "kural" in capsys.readouterr().out


def test_main_explain_donusum_yok(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    dosya = tmp_path / "g.txt"
    dosya.write_text("bir gün gelecek\n", encoding="utf-8", newline="\n")
    assert cli.main(["--explain", str(dosya)]) == 0
    cikti = capsys.readouterr().out
    assert "(dönüşüm yok)" in cikti


def test_main_olmayan_dosya(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["/yok/boyle/dosya.txt"]) == 1
    assert "tr-itn:" in capsys.readouterr().err


def test_main_iki_dosya(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("iki\n", encoding="utf-8", newline="\n")
    b.write_text("üç", encoding="utf-8", newline="\n")
    assert cli.main([str(a), str(b)]) == 0
    assert capsys.readouterr().out == "2\n3\n"


def test_main_binlik_bosluk(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    dosya = tmp_path / "g.txt"
    dosya.write_text("iki bin\n", encoding="utf-8", newline="\n")
    assert cli.main(["--binlik", "bosluk", str(dosya)]) == 0
    assert capsys.readouterr().out == "2 000\n"


def test_main_binlik_virgul(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    dosya = tmp_path / "g.txt"
    dosya.write_text("iki bin\n", encoding="utf-8", newline="\n")
    assert cli.main(["--binlik", "virgul", str(dosya)]) == 0
    assert capsys.readouterr().out == "2,000\n"


def test_surum_exit() -> None:
    with pytest.raises(SystemExit) as hata:
        cli.main(["--surum"])
    assert hata.value.code == 0


def test_kur_nesnesi() -> None:
    assert cli.kur().prog == "tr-itn"


def test_main_alan_ozet(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    sozluk = tmp_path / "sozluk.json"
    sozluk.write_text('{"ad": "test", "kurallar": {"kdv": "KDV"}}', encoding="utf-8", newline="\n")
    dosya = tmp_path / "g.txt"
    dosya.write_text("yüzde on sekiz kdv\n", encoding="utf-8", newline="\n")
    assert cli.main(["--alan", str(sozluk), str(dosya)]) == 0
    assert capsys.readouterr().out == "%18 KDV\n"


def test_main_alan_cakisma_uyarisi(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sozluk = tmp_path / "sozluk.json"
    sozluk.write_text('{"kurallar": {"tl": "TL"}}', encoding="utf-8", newline="\n")
    dosya = tmp_path / "g.txt"
    dosya.write_text("üç\n", encoding="utf-8", newline="\n")
    assert cli.main(["--alan", str(sozluk), str(dosya)]) == 0
    assert "yerleşik kuralı eziyor" in capsys.readouterr().err


def test_main_alan_bozuk(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    bozuk = tmp_path / "bozuk.json"
    bozuk.write_text("{bozuk", encoding="utf-8", newline="\n")
    assert cli.main(["--alan", str(bozuk)]) == 1
    assert "bozuk.json" in capsys.readouterr().err


def test_main_alan_yok(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["--alan", "/yok/sozluk.json"]) == 1
    assert "tr-itn:" in capsys.readouterr().err
