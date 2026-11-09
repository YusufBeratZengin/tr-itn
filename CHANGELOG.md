# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- On Windows, input with CRLF line endings produced CR CR LF in the output; line endings
  are now written exactly as read.

### Changed

- `scripts/check.sh` now bootstraps a local `.venv` and installs `.[dev]` when the dev tools
  are missing, so the documented gate runs on a fresh clone with a single command
  (`TR_ITN_KURULUM=0` disables automatic installation). Documented in both READMEs and
  CONTRIBUTING.

### Planned

- Distributive numerals (`birer`, `ikişer`) and `-lık` / `-ce` suffixed numerals.
- Possessive date forms (`"kasımın üçü"`).
- Optional comparison script against NVIDIA NeMo ITN output (measurement only).

## [0.1.0] - 2026-11-03

First public release.

### Added

- `tr_itn.cevir()` — converts spoken Turkish numerals in ASR text to written form:
  cardinals from 0 to the billions, decimals (`"üç virgül beş"` → `3,5`), percentages
  (`"yüzde on sekiz"` → `%18`), ordinals (`"üçüncü"` → `3.`), clock times including
  `buçuk` / `çeyrek` (`"saat üç buçuk"` → `saat 3:30`), dates
  (`"iki kasım iki bin yirmi altı"` → `2 Kasım 2026`), money
  (`"yüz elli lira"` → `150 TL`, `"iki bin dolar"` → `$2000`), common units
  (`"üç kilometre"` → `3 km`) and digit sequences after phone/number cue words.
- Suffix-aware output: Turkish vowel harmony decides the apostrophe form
  (`"on dörtte"` → `14'te`, `"altıda"` → `6'da`, `"yüz elli liraya"` → `150 TL'ye`).
- `tr_itn.acikla()` / `cevir_ayrintili()` — rule trace with rule name, input, output,
  character span and confidence for every conversion.
- Conservative ambiguity policy: bare `bir` / `yüz`, idioms (`"ikinci el"`, `"yüz yüze"`),
  unmarked two-part numerals (`"on dört otuz"`) and `"üç buçuk"` are left unchanged unless
  the context (unit, suffix, cue word) or an opt-in style says otherwise.
- `Stil` options: decimal separator, thousands separator, money as symbol or name,
  `bir_baglami` (`siki` / `gevsek`), `saat_kipi`, `rakam_dizisi`, month capitalization,
  and numeric thresholds (`esik`, `ust_sinir`).
- `tr_itn.Akis` — chunked/streaming mode that buffers a numeral split across ASR chunks.
- `tr_itn.srt_cevir()` / `vtt_cevir()` — subtitle filters that convert text lines only and
  leave cue numbers, timestamps and `WEBVTT` headers untouched.
- `AlanSozlugu` — domain dictionary loader (JSON or minimal YAML) that overrides built-in
  rules, protects its own output and reports conflicts instead of applying them silently.
- CLI `tr-itn` with `--explain`, `--json`, style flags, `--alan`, stdin/`-`/multi-file input
  and documented exit codes. The converter never raises on text; unknown input is echoed.
- `scripts/wer.py` — "normalized WER" measurement demo on a synthetic dataset.
- `scripts/bench.py` — 1 MiB throughput measurement.
- 300 hand-checked test vectors (100 numeral, 60 date/time, 60 money/percent/unit,
  40 ordinal/suffix, 40 negative controls), a 10,000-number round-trip test, CLI error-path
  tests and a 93% branch-coverage gate.
- Documentation in English and Turkish, CI for Linux/Windows/macOS, Dependabot, issue and
  pull-request templates.

### Notes

- Zero runtime dependencies; the package imports only the standard library.
- No network access at runtime or in tests.
- Example data (meeting notes, subtitles, WER set, phone-like digit strings) is synthetic.

[Unreleased]: https://github.com/YusufBeratZengin/tr-itn/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/YusufBeratZengin/tr-itn/releases/tag/v0.1.0
