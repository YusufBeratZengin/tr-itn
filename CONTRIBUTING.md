# Contributing to tr-itn

Thanks for taking the time to contribute. This project is small on purpose: one pure-Python
package, no runtime dependencies, and a test suite that is the specification. Contributions
that keep it that way are very welcome.

## Ways to help

- Report a wrong or missing conversion (the most valuable contribution — see below).
- Add or fix a hand-checked test vector.
- Add a unit or currency that is missing from `src/tr_itn/sozluk.py`.
- Improve the documentation or the Turkish wording of error messages.
- Review pull requests, especially ones that touch suffix harmony.

## Reporting a wrong conversion

Open a bug report with:

1. the exact input string (copy-paste, UTF-8),
2. what came out, and what you expected,
3. the rule name from `tr-itn --explain` (or `acikla(metin)`), if any,
4. a one-line justification of the Turkish rule involved.

Please do not paste real personal data (names, phone numbers, addresses, customer text) into
an issue. Synthesize a comparable example instead. Phone-like digit strings in this repo are
invented.

## Development setup

```bash
git clone https://github.com/YusufBeratZengin/tr-itn.git
cd tr-itn
python -m pip install -e ".[dev]"
bash scripts/check.sh
```

`scripts/check.sh` runs `ruff`, `mypy --strict` and `pytest` with a coverage gate of 85%.
It exits 0 only when everything passes; that is the same command CI runs. If the dev tools are
missing it creates a local `.venv` and installs `.[dev]` there first (disable with
`TR_ITN_KURULUM=0`), so `bash scripts/check.sh` also works on a fresh clone with one command.

Requirements: Python 3.10+, no network access needed for the test suite.

## Project layout

```
src/tr_itn/
  sozluk.py    word lists, month/day names, units, cue words
  sayi.py      cardinal parser, decimals, percentages, ordinals
  tarih.py     dates
  saat.py      clock times (buçuk / çeyrek)
  para.py      money
  birim.py     units
  ekler.py     Turkish suffix harmony and apostrophe forms
  baglam.py    context cues and ambiguity guards
  motor.py     the rule engine (order matters) and the public API
  stil.py      output style options
  alan.py      domain dictionary loader
  akis.py      streaming/chunked mode
  altyazi.py   SRT/VTT filters
  cli.py       command line interface
tests/
  vektorler/   hand-checked JSONL vectors (input, expected output, rule name)
```

## Adding test vectors

Vectors live in `tests/vektorler/*.jsonl`, one JSON object per line:

```json
{"id": "sayi-101", "girdi": "kırk iki", "beklenen": "42", "kural": "kardinal"}
```

Rules:

- Every line must be **checked by hand** against a grammar reference or native intuition.
  Do not generate vectors from the implementation — that only tests the implementation
  against itself.
- `girdi` and `beklenen` must be exact strings (no trimming surprises).
- `kural` is the rule that must appear in the trace (`acikla(girdi)`); use `"yok"` for
  negative controls, where `beklenen == girdi` and no conversion may happen.
- Keep `id` unique within a file, and keep the existing prefixes (`sayi-`, `tarih_saat-`,
  `para_yuzde_birim-`, `sira_ek-`, `olumsuz-`).
- If your vector is a negative control, explain in the PR why converting it would be wrong.

## Changing rules

- Add the failing vector first, watch the test fail (`pytest tests/test_vektorler.py -q`),
  then change the rule. The suite must be red before the fix and green after.
- Never trade a negative control for a positive one. If a rule change makes
  `"ikinci el araba"` convert, the change is wrong even if it fixes ten other cases.
- Suffix forms must follow vowel harmony and consonant assimilation. When in doubt, read
  `src/tr_itn/ekler.py` and add unit tests there.
- Keep public API changes additive; this project follows semver.

## Style

- Formatted and linted by `ruff` (line length 110, target Python 3.10).
- Fully typed; `mypy --strict` must stay clean.
- Identifiers and docstrings are Turkish (matching the domain), public documentation is
  English + Turkish. Please keep both READMEs in sync when behavior changes.
- No new runtime dependencies. If you think one is unavoidable, open an issue first with the
  reason — "zero dependencies, works on Windows" is the main reason this package exists.
- No network calls in library code or tests.

## Pull requests

1. One topic per PR; keep diffs focused.
2. Include the test that proves the change (new vector or unit test).
3. Update `CHANGELOG.md` under `[Unreleased]` for user-visible changes.
4. Make sure `bash scripts/check.sh` exits 0 locally.
5. Describe the before/after output in the PR body.

Maintainers may ask for a second opinion on suffix-heavy changes; that is normal and not a
judgement on the contribution.

## Commit messages

Short imperative English subject line, for example:

```
fix: keep "üç buçuk" unchanged without a unit
feat: add "kuruş" as a money unit
test: add 8 negative vectors for "yüz"
```

## License

By contributing you agree that your contribution is licensed under the MIT license of this
repository.
