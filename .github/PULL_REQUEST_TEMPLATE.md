# Pull request

## What does this change?

<!-- One or two sentences. Link the issue if there is one: "Closes #12". -->

## Before / after

```
input:    ...
before:   ...
after:    ...
```

## Type of change

- [ ] Bug fix (wrong or missing conversion)
- [ ] New rule / unit / style option
- [ ] Documentation
- [ ] Tests or tooling (no behavior change)
- [ ] Refactor (no behavior change)

## Tests

- [ ] Added at least one hand-checked vector or unit test that fails without this change
- [ ] Negative controls still pass (`tests/vektorler/olumsuz.jsonl`)
- [ ] `bash scripts/check.sh` exits 0 locally (ruff + mypy + pytest, coverage >= 85%)

## Checklist

- [ ] No new runtime dependency (or the reason is explained and agreed in an issue)
- [ ] Public behavior change is noted in `CHANGELOG.md` under `[Unreleased]`
- [ ] README.md and README.tr.md stay in sync
- [ ] No personal data, real-looking secrets or network calls added
- [ ] Library code still never raises on plain text input
