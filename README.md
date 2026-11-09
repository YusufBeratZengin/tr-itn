# tr-itn

**Turkish inverse text normalization (ITN) for ASR output** — turn spoken numbers back into
written form (`"iki bin yirmi altı"` → `2026`, `"yüzde on sekiz"` → `%18`, `"on dört otuz"` →
`14:30`), with Turkish suffix harmony handled by rule.

Pure Python 3.10+, **zero runtime dependencies**, works on Windows, macOS and Linux.

```
$ echo "toplantı iki kasım iki bin yirmi altı saat on dört otuzda" | tr-itn
toplantı 2 Kasım 2026 saat 14:30'da
```

## Why

Speech recognizers disagree about numbers. Some emit digits (`14:30`), others spell them out
(`"on dört otuz"`). Subtitle, meeting-note and voice-bot pipelines need one consistent written
form, and Turkish is not just "concatenate words": the suffix has to follow vowel harmony —
`"on dörtte"` → `14'te`, `"yüz elli liraya"` → `150 TL'ye`, `"üç kilometreye"` → `3 km'ye`.

The established tool for this is NVIDIA NeMo-text-processing, which needs Pynini/OpenFST and
only ships wheels for Linux x86_64. `tr-itn` is the dependency-free alternative: `pip install
tr-itn`, one import, no compiler, no download at runtime.

## Install

```bash
pip install tr-itn
```

Nothing else is installed: the package imports only the standard library.

## 30-second example

```bash
$ tr-itn --explain <<< "yüzde on sekiz kdv"
%18 kdv

kural         güven   girdi -> çıktı
yuzde         0.98    yüzde on sekiz -> %18
```

```python
>>> from tr_itn import cevir, acikla
>>> cevir("toplantı iki kasım iki bin yirmi altı saat on dört otuzda")
"toplantı 2 Kasım 2026 saat 14:30'da"
>>> cevir("yüz elli liraya iki bin dolar")
"150 TL'ye $2000"
>>> acikla("üçüncü")[0].kural
'sira'
```

## What it converts

| Rule | Spoken | Written |
| --- | --- | --- |
| cardinal | `iki bin yirmi altı` | `2026` |
| cardinal + suffix | `otuzunda`, `dörtte` | `30'unda`, `4'te` |
| decimal | `üç virgül sıfır beş` | `3,05` |
| percent | `yüzde on sekiz kdv` | `%18 kdv` |
| ordinal | `yüz elli üçüncü`, `ikincisi` | `153.`, `2'ncisi` |
| time | `saat on dört otuz`, `on dört otuzda` | `saat 14:30`, `14:30'da` |
| time (half/quarter) | `saat üç buçuk`, `saat üç çeyrek` | `saat 3:30`, `saat 3:15` |
| date | `iki kasım iki bin yirmi altı` | `2 Kasım 2026` |
| date + suffix | `iki kasımda`, `2026 yılında` | `2 Kasım'da`, `2026 yılında` |
| money | `yüz elli lira`, `iki bin dolar` | `150 TL`, `$2000` |
| money + suffix | `yüz elli liraya` | `150 TL'ye` |
| units | `üç kilometreye`, `yirmi beş derece` | `3 km'ye`, `25°` |
| digit sequence | `sıfır beş üç iki …` (after "telefon"/"numara") | `0532…` |

Two things are deliberately *not* touched: punctuation/capitalization restoration and word-error
correction. Number-to-words (the other direction) is a different project.

## Ambiguity policy: when in doubt, do not convert

Turkish number words collide with ordinary words, so the default is conservative and every
decision is explainable:

| Input | Output | Why |
| --- | --- | --- |
| `bir gün gelecek` | unchanged | bare `bir` is not an explicit number |
| `yirmi bir` | `21` | inside a multi-word numeral |
| `bir lira` | `1 TL` | money context |
| `ikinci el araba` | unchanged | idiomatic "second-hand" |
| `yüz yüze` | unchanged | idiom; bare `yüz` needs numeric context |
| `onun arabası` | unchanged | pronoun, not `on` + suffix |
| `iki üç kişi` | unchanged | not a numeral ("two or three") |
| `on dört otuz` | unchanged | could be `1430` or a time — no context |
| `on dört otuzda` | `14:30'da` | locative suffix marks time |
| `üç buçuk` | unchanged | 3.5 or 3:30? |
| `üç buçuk kilo` | `3,5 kg` | unit marks a decimal |

If you *want* the aggressive reading, opt in:

```python
from tr_itn import cevir, Stil

cevir("bir gün gelecek", Stil(bir_baglami="gevsek"))   # "1 gün gelecek"
cevir("on dört otuz", Stil(saat_kipi=True))            # "14:30"
cevir("on dört otuz")                                  # "on dört otuz"
```

## Three real scenarios

**1. Subtitles.** Convert an ASR-generated SRT without touching cue numbers or timestamps:

```python
from pathlib import Path
from tr_itn import srt_cevir

p = Path("altyazi.srt")
p.write_text(srt_cevir(p.read_text(encoding="utf-8")), encoding="utf-8")
```

```
1
00:00:01,000 --> 00:00:04,000
toplantı 2 Kasım 2026 saat 14:30'da başlıyor

2
00:00:04,500 --> 00:00:07,000
%18 kdv dahil 150 TL
```

**2. Meeting transcript.** One command, with a finance dictionary for acronyms:

```bash
$ tr-itn --alan ornekler/alan_finans.json ornekler/toplanti.txt
tr-itn: uyarı: 'tl' yerleşik kuralı eziyor
Merhaba, bugünkü toplantı 2 Kasım 2026 saat 14:30'da başlıyor.
...
```

**3. Voice bot.** Digit strings after a cue word (numbers below are invented):

```bash
$ echo "telefon sıfır beş üç iki bir iki üç dört beş altı yedi" | tr-itn
telefon 05321234567
```

Use `acikla()` when you need to act only on a specific rule (for example, extract amounts
but leave times alone).

## CLI

```
tr-itn [DOSYA ...] [--explain] [--json]
       [--ondalik {,|.}] [--binlik {yok|nokta|virgul|bosluk}]
       [--para-adi] [--bir {siki|gevsek}] [--saat-kipi] [--rakam-dizisi]
       [--esik N] [--alan DOSYA] [--surum]
```

* no arguments or `-` reads stdin; several files are processed in order
* `--explain` prints the rule trace, `--json` prints `{"metin": ..., "kurallar": [...]}`
* exit codes: `0` success, `1` unreadable file / bad dictionary, `2` usage error
* input that no rule understands is echoed unchanged; the converter never raises on text

## Python API

```python
from tr_itn import cevir, cevir_ayrintili, acikla, Stil, AlanSozlugu, srt_cevir, Akis

cevir(metin, stil=None, alan=None)          -> str
cevir_ayrintili(metin, stil=None, alan=None) -> Sonuc(metin, izler)
acikla(metin, stil=None, alan=None)         -> list[KuralIzi]
```

`KuralIzi` carries `kural` (rule name), `girdi`, `cikti`, `konum` (character span),
`guven` (0–1 confidence) and `aciklama` (why the rule fired).

### Streaming (chunked ASR)

`Akis` buffers the trailing numeral and the trailing half-word, so a number split across
chunks stays one number:

```python
>>> a = Akis()
>>> a.besle("toplantı iki bin")
'toplantı '
>>> a.besle(" yirmi altı")
''
>>> a.bitir()
'2026'
```

### Subtitles (SRT / VTT)

Timestamps, cue numbers and `WEBVTT` headers are preserved; only text lines are converted.

```python
from tr_itn import srt_cevir
yeni = srt_cevir(open("altyazi.srt", encoding="utf-8").read())
```

### Domain dictionary

A JSON (or minimal `key: value` YAML) file overrides the defaults and protects its output from
further conversion. Conflicts with built-in words are reported, not silently applied.

```bash
$ tr-itn --alan ornekler/alan_finans.json ornekler/toplanti.txt
tr-itn: uyarı: 'tl' yerleşik kuralı eziyor
Merhaba, bugünkü toplantı 2 Kasım 2026 saat 14:30'da başlıyor.
Geçen ay %18 KDV dahil 150 TL birim fiyatla 2400 adet sattık.
```

### Measuring "normalized WER"

```bash
$ python scripts/wer.py ornekler/wer_ornek.jsonl
kayıt        : 5
WER (ham)    : 1.000
WER (ITN)    : 0.067
fark         : +0.933
```

The dataset in `ornekler/wer_ornek.jsonl` is **synthetic** and exists only to demonstrate the
measurement; it is not a benchmark.

## Style options

| Option | Default | Meaning |
| --- | --- | --- |
| `ondalik_ayirici` | `","` | decimal separator (`3,5` vs `3.5`) |
| `binlik_ayirici` | `None` | thousands separator (`2.026`, `2 026`) |
| `para_sembolu` | `True` | `150 TL` vs `150 lira` |
| `bir_baglami` | `"siki"` | strict / loose handling of bare `bir` |
| `saat_kipi` | `False` | read two-part numerals as times |
| `rakam_dizisi` | `False` | join digit words into a digit string |
| `ay_buyuk_harf` | `True` | `2 Kasım` vs `2 kasım` |
| `esik` / `ust_sinir` | `0` / `None` | leave numbers below/above these as words |

## Correctness

* **305 hand-checked vectors** in `tests/vektorler/*.jsonl` (input, expected output, rule name):
  101 numerals, 60 date/time, 60 money/percent/unit, 40 ordinal + suffix, 44 negative controls.
* **Zero false conversions** on the negative set (`bir gün gelecek`, `ikinci el`, `yüz yüze`,
  `onun`, `on dört otuz`, …).
* **Round trip**: 10,000 random numbers written as words and converted back give the same value
  (`tests/test_roundtrip.py`).
* **94% branch coverage**, `mypy --strict` clean, `ruff` clean, tests on Linux, Windows and macOS.

Measurements on this machine (Linux x86_64, Python 3.14, single core):

```
input      : 1.00 MiB (966511 chars)
output     : 586950 chars
time       : 1.9–2.0 s (best of 3)
throughput : 0.51–0.52 MiB/s
```

Reproduce with `python scripts/bench.py`.

## Limitations (read before shipping)

* Bare `bir` (1) and bare `yüz` (100) are **not** converted by default — say `bir lira`,
  `yüzde yüz`, `iki yüz` or use `bir_baglami="gevsek"`.
* `saat yirmi beş` is read as `20:05`, not "twenty-five o'clock"; clock idioms
  (`"üçü çeyrek geçe"`) are out of scope.
* `üç virgül beş yüz` becomes `3,500`; decimals are parsed as a number, so avoid trailing
  number words after the fractional part.
* Date forms with possessive morphology (`"kasımın üçü"`) are left untouched.
* `-lık` and `-ce` suffixes on numerals, distributive numerals (`birer`, `ikişer`) and
  letters-spelled acronyms are not handled.
* Text is assumed UTF-8; invalid bytes are replaced (CLI) rather than rejected.
* The library never invents values: it converts what is written and leaves everything else.

## Development

```bash
python -m pip install -e ".[dev]"
bash scripts/check.sh          # ruff + mypy + pytest (>=85% coverage)
```

`check.sh` exits 0 only when lint, types, tests and the coverage gate all pass. On a clean
checkout it bootstraps itself: if `pytest`/`pytest-cov`/`ruff`/`mypy` are missing it creates a
local `.venv`, installs `.[dev]` there and runs the gate with that interpreter. Set
`TR_ITN_KURULUM=0` to disable the automatic install and get the plain "missing tools" error.

## License

MIT © 2026 YusufBeratZengin. See [LICENSE](LICENSE).
