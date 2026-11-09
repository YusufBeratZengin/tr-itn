#!/usr/bin/env bash
# Lint + tip kontrolü + testler + kapsam. Yalnızca hepsi geçerse 0 döner.
#
# Geliştirme araçları eksikse betik kendi yerel .venv'ini kurup oradan devam eder;
# böylece temiz bir klonda `bash scripts/check.sh` tek komutla çalışır.
# Kurulumu kapatmak için: TR_ITN_KURULUM=0 bash scripts/check.sh
set -euo pipefail

KOK="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$KOK"

PY="${PYTHON:-python3}"
if ! command -v "$PY" >/dev/null 2>&1; then
  echo "check: hata: '$PY' bulunamadı (PYTHON=... ile belirtin)" >&2
  exit 2
fi

eksik_araclar() {
  "$1" - <<'PYEOF'
import importlib.util
adlar = ["pytest", "pytest_cov", "ruff", "mypy"]
print(" ".join(a for a in adlar if importlib.util.find_spec(a) is None))
PYEOF
}

kurulum_onerisi() {
  echo "check: kurulum: $PY -m pip install -e '.[dev]'" >&2
}

EKSIK="$(eksik_araclar "$PY")"
if [ -n "$EKSIK" ]; then
  if [ "${TR_ITN_KURULUM:-1}" = "0" ]; then
    echo "check: hata: eksik araçlar: $EKSIK (TR_ITN_KURULUM=0)" >&2
    kurulum_onerisi
    exit 2
  fi

  VENV="$KOK/.venv"
  if [ -x "$VENV/bin/python" ]; then
    VPY="$VENV/bin/python"
  elif [ -x "$VENV/Scripts/python.exe" ]; then
    VPY="$VENV/Scripts/python.exe"
  else
    echo "check: eksik araçlar: $EKSIK — yerel .venv oluşturuluyor" >&2
    if ! "$PY" -m venv "$VENV" >/dev/null 2>&1; then
      echo "check: hata: .venv oluşturulamadı ('python3-venv' kurulu mu?)" >&2
      kurulum_onerisi
      exit 2
    fi
    if [ -x "$VENV/bin/python" ]; then
      VPY="$VENV/bin/python"
    else
      VPY="$VENV/Scripts/python.exe"
    fi
  fi

  if ! "$VPY" -m pip install -q --disable-pip-version-check -e '.[dev]'; then
    echo "check: hata: geliştirme bağımlılıkları kurulamadı (ağ erişimi gerekli)" >&2
    echo "check: kurulum: $VPY -m pip install -e '.[dev]'" >&2
    exit 2
  fi

  EKSIK="$(eksik_araclar "$VPY")"
  if [ -n "$EKSIK" ]; then
    echo "check: hata: kurulumdan sonra hâlâ eksik araçlar: $EKSIK" >&2
    exit 2
  fi
  PY="$VPY"
fi

export PYTHONPATH="$KOK/src${PYTHONPATH:+:$PYTHONPATH}"

echo "== ruff (lint) =="
"$PY" -m ruff check src tests scripts

echo "== mypy (tipler) =="
"$PY" -m mypy

echo "== pytest (testler + kapsam) =="
"$PY" -m pytest tests/ -q --cov=tr_itn --cov-fail-under=85 --cov-report=term-missing

echo "check: TÜM KONTROLLER GEÇTİ"
