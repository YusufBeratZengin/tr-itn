# Security policy

## Supported versions

| Version | Supported |
| ------- | --------- |
| 0.1.x   | yes       |

## Reporting a vulnerability

Please **do not open a public issue** for a security problem. Use GitHub's private
vulnerability reporting: repository → *Security* → *Report a vulnerability*
(https://github.com/YusufBeratZengin/tr-itn/security/advisories/new).

If that is unavailable, open an issue that says only "security report — please contact me"
and a maintainer will arrange a private channel. Do not include exploit details, personal
data, or credentials in a public issue.

You can expect an acknowledgement within 7 days and a status update within 30 days. Please
give us a reasonable window to ship a fix before any public disclosure.

## Scope

`tr-itn` is a pure-Python text transformer:

- it performs **no network access** at runtime and in tests,
- it reads only the files it is explicitly given on the command line,
- it does not execute input, evaluate expressions, load remote code, or write files,
- it has **zero runtime dependencies**, so there is no third-party code in the installed
  package.

Reports that are in scope include: unbounded resource consumption on adversarial input,
crashes that leak the contents of other files, incorrect handling of invalid UTF-8 that
could corrupt downstream pipelines, and any way to make the CLI write outside its stdout.

## Known non-issues

- The converter is not a sanitizer. It does not remove personal data, profanity or prompt
  injection from text; it only rewrites numerals. Do not rely on it for redaction.
- Very large inputs are processed in memory; a multi-hundred-megabyte file will use
  comparable memory. Stream with `Akis` or split input if that matters to you.
- Output is text, not HTML. Escaping for a specific downstream format is the caller's job.

## Dependency and secret hygiene

- No secrets are used by this project. Nothing is read from the environment except the
  optional `PYTHON` variable used by `scripts/check.sh` to pick an interpreter.
- Example data in `ornekler/` and `tests/vektorler/` is synthetic; phone-like digit strings
  are invented and do not belong to anyone.
- Dependabot is enabled for pip and GitHub Actions.
