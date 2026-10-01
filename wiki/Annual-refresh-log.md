# Annual Refresh Log

Every data release, newest first. This page is the human history of the dataset — what was checked, what changed, what went wrong. The machine-readable counterpart is `data/meta/changelog.md`.

When a release ships, a maintainer appends a row here and to `data/meta/changelog.md`. The wiki never edits history; corrections get a follow-up note, never a silent rewrite.

| Release | Date shipped | Licensed records | Watchlist records | Notes |
|---|---|---|---|---|
| `2026.1` | 2026-09-07 | 1 | 0 | First public release. Seed record Halo Asian Spa (MM41109) verified against the MQA portal on 2026-09-07. Watchlist tier ships as an empty, encrypted placeholder — the machinery is live, the list is empty. |

## 2026.1 — 2026-09-07

**What shipped**

- The public licensed list (`data/public/licensed.json`) with the seed record: Halo Asian Spa, Inc — license MM41109, status Clear, issued 2020-12-14, expires 2027-08-31, 975 West Gateway Blvd Suite 105, Boynton Beach FL 33426. Discipline on file: No. Public complaint: No. Data as of 2026-09-07.
- The encrypted watchlist envelope (`data/private/unlicensed.encrypted.json`), v1, PBKDF2-SHA256 @ 310,000 iterations, AES-256-GCM. Records: 0 — a deliberate empty placeholder so the subscriber unlock path is exercised end-to-end on every surface without exposing any business to an empty-tier bug.
- All six surface builds (web, extension, Android, Android Auto, watch, iOS) generated from the single source via `admin_scripts/generate_public_files.py`.

**Coverage at release:** 1 licensed record, Palm Beach County only.

**What we learned doing it**

- The MQA portal renders name/address search well but the establishment (MM) search space is large; manual per-record verification is the only method that matches our constraints. The workflow is documented in [docs/annual_update_workflow.md](../docs/annual_update_workflow.md) and it takes minutes per record, not seconds — which is the real reason the cadence is annual.
- License numbers are stable; names and statuses change. Every record carries `last_checked` so a reader can judge freshness themselves.

**Deferred to next cycle**

- Broaden coverage beyond Palm Beach County. Priorities tracked as feature requests, not promises.
- First watchlist entries. The bar for entry on the watchlist is deliberately high: a documented search (what terms, what date, zero matches) recorded in `status_note`. See the [FAQ](FAQ.md) on why "no license found" is not "unlicensed."
- Re-verify the seed record's 2027-08-31 expiry — it lands inside the 2027 window, so it appears in the "expiring soon" filter before the next release unless an interim correction lands first.

## Pre-release history

| Date | Event |
|---|---|
| 2025 (project structured) | Directory skeleton, three constraints locked (no backend, no third-party, annual cadence). |
| 2026-09-07 | Seed record verified; `2026.1` release built and shipped. |

## How to add a release row

1. Run the annual workflow (`docs/annual_update_workflow.md`) start to finish — including the verify step that decrypts the shipped envelope with the correct code.
2. Bump `version` in both `data/public/licensed.json` and the unlicensed plaintext source before encrypting (e.g. `2027.1`).
3. Append a row to the table above with shipped date and counts.
4. Append the machine-readable entry to `data/meta/changelog.md`.
5. Tag the commit `data-<year>` (e.g. `data-2026`) per the workflow's ship step.
