# Annual Update Workflow

FED-SPA refreshes its dataset **once a year**. This document is the
complete, from-scratch procedure. Total time: an afternoon.

## Why annual

- The FL DOH MQA portal is the authority; licenses change slowly
  (2-year cycles, e.g. MM41109 expires 2027-08-31)
- No backend means no auto-refresh; shipping a new dataset means
  shipping new static files
- Annual cadence keeps the manual verification workload sane for a
  small maintainer team

## Prerequisites

- Python 3.11+ (stdlib only — no pip installs needed)
- Node 20+ (for the encryptor)
- The subscriber distribution password (see `password_distribution.md`)

## The six steps

Run everything from the repo root.

### 1. Scrape (optional assist — human verification is the real step)

```bash
python3 admin_scripts/scrape_mqa.py discover
python3 admin_scripts/scrape_mqa.py scrape --file queries.txt
```

`queries.txt` is one business name (or license number) per line. Output
lands in `data/meta/raw/scrape_<date>.json`. **Never trust it blindly** —
open each hit on the MQA portal in a browser and confirm the fields. The
scraper exists to save typing, not to replace eyeballs.

If the portal's form fields changed, `discover` prints what it sees so
`SEARCH_FORM` in the script can be updated (that's why it's regex +
stdlib: easy to read, easy to fix).

### 2. Edit the two source files

- `data/public/licensed.json` — the public tier. Every record carries
  `data_as_of` and `last_checked`; bump the top-level `as_of` too.
- `data/private/unlicensed.plain.json` — the subscriber tier (gitignored,
  never committed).

Record shape requirements are enforced by the next step.

### 3. Validate

```bash
python3 admin_scripts/validate_schema.py
```

Checks required fields, status enums (`Clear/Active/Delinquent/Expired/
Inactive/Probation` for licensed; `no_license_found/expired/inactive/
revoked/delinquent` for unlicensed), Florida-only addresses, ZIP format,
license-number format `^[A-Z]{2}[0-9]{4,8}$`. Exits non-zero on any
violation. Fix and repeat until clean.

### 4. Encrypt the subscriber tier

```bash
node admin_scripts/encrypt_unlicensed.js \
     data/private/unlicensed.plain.json \
     data/private/unlicensed.encrypted.json
```

Prompts for the password (or `FEDSPA_PASSWORD` env var). Runs a built-in
round-trip self-check before writing. The output envelope is
`{v, kdf, iterations, salt, iv, data}` — the exact format every client
decrypts.

### 5. Fan out to all six platforms

```bash
python3 admin_scripts/generate_public_files.py
```

Copies `licensed.json` + the encrypted envelope into `web/data/`,
`extension/data/`, android assets, android_auto assets, watch assets,
and iOS Resources — stripping admin-only fields (`verified_by`) from
public copies. Commit the generated diffs (CI re-runs this and fails on
drift).

### 6. Ship it

```bash
./admin_scripts/merge_and_encrypt.sh          # runs steps 3-5 in order
git checkout -b data/2027-refresh
git commit -am "Data refresh: as of <date>"
# open PR, let CI validate, merge, tag: git tag data-2027 && git push --tags
```

Then update the distribution (next doc) and post the release notes in
Announcements.

## One-command version

```bash
SCRAPE=0 ./admin_scripts/merge_and_encrypt.sh
```

runs validate → encrypt → fan-out. Set `SCRAPE=1` to also run the
scraper first.

## After shipping

- Bump `data/meta/changelog.md`
- Version the release tag `data-<year>`
- Announce in Discussions → Announcements
- Update `wiki/` data-stats page if counts changed materially
