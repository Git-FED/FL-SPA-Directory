# County Sweep 2026.2 — Fort Pierce → Homestead

The working record of the project's first county sweep: what was checked,
how, what made the cut, and what was left out on purpose. Companion pages:
[Data-statistics.md](Data-statistics.md) (the counts), [Annual-refresh-log.md](Annual-refresh-log.md)
(the release history). The machine that turns the sweep spreadsheet into the
repo's data files is `admin_scripts/xlsx_to_fedspa.py`.

## The corridor

US-1 / Federal Highway from Fort Pierce (St. Lucie County) south to
Homestead (Miami-Dade County): 5 counties, 112 municipalities listed in
[locations.md](locations.md). The corridor was chosen because it is one
continuous commercial artery — the directory lists businesses that sit on
it or within a short jog of it, which keeps the sweep walkable in a way a
whole-county grab would not be.

Verification dates: **2026-09-09, 2026-09-10, 2026-09-11**, all against the
[FL DOH MQA Verification Portal](https://mqa-internet.doh.state.fl.us/MQASearchServices/HealthCareProviders).

## What the sweep processed

| Row type | Rows | Working colors |
|---|---|---|
| Establishment listings (from the corridor directory) | 372 | 12 GREEN · 22 BLUE · 42 YELLOW · 13 RED · 283 not checked |
| License-record evidence (DOH records surfaced during verification) | 27 | 3 GREEN · 2 YELLOW · 22 RED |

The sweep spreadsheet's working colors are *working* colors — a triage
taxonomy, not the repo's data tiers. The two must not be conflated: GREEN
means "checked, license confirmed active, no issues"; it does not mean
"licensed tier" until the license-status column corroborates it.

## The tier mapping (the inclusion bars)

Implemented in `admin_scripts/xlsx_to_fedspa.py`; every rule below exists
because a real row forced it.

**Licensed tier — 47 records.** A record ships publicly only when a
maintainer verified a *current, active* license on the MQA portal with
license number, expiration, issue date, and Address of Record on file:

- GREEN / BLUE establishment rows with license status Clear (BLUE marks a
  zero-issue history — nothing ever filed against the license).
- YELLOW rows whose license status is Clear. The yellow is about
  *predecessor-license history* (an older license under the same or similar
  name, now void/relinquished). The license itself is real and active, so
  the record ships — with the predecessor caveat carried verbatim in notes
  (e.g. the seed record, Halo Asian Spa MM41109, ships with predecessor
  MM34578's voluntary relinquishment in its notes).
- GREEN evidence rows with an Address of Record — DOH license records that
  surfaced during verification of *other* listings, with no directory
  listing of their own. Three qualified (Green Massage of Plantation
  MM43835, ZHANG CORPORATION MM45534, HEALTH SPA FLORIDA LLC MM41565);
  they are real, verified, located businesses, so they belong in the
  directory.

**Watchlist tier — 44 entries.** The subscriber tier's bar (per the
[FAQ](FAQ.md)): a *documented portal search* that found no active license
for the listed business at the listed address. Every entry carries what
was searched and what was found, in its reason field:

- RED rows — license revoked (3, with board case numbers where the portal
  shows them), null-and-void (mapped to `expired`), relinquished in the
  face of discipline or pending board action (mapped to `inactive`).
- YELLOW "No Match Found" rows — a documented search that returned zero
  matches (the largest single bucket: 30 entries map to
  `no_license_found`).
- YELLOW "Multiple Candidates — Unconfirmed" — same-named licenses exist
  but none can be address-confirmed; the ambiguity is recorded verbatim
  rather than resolved by guesswork.
- YELLOW "Closed" — DOH license status Closed, name-matched.

**Excluded from both tiers — 308 rows.** Honesty over volume:

- 283 establishment rows nobody has checked yet. They stay out until
  someone looks at them.
- 1 row colored YELLOW but never actually checked (the sweep's own
  inconsistency; excluded rather than trusted).
- 24 evidence rows that are pure predecessor-license documentation — their
  content already lives inside the parent record's notes/history fields.

## Address handling

The licensed tier uses the DOH **Address of Record** when the portal shows
one (all 47 records have one) — it is the authoritative location for the
license, and where the directory listing and the AOR disagreed (the seed
record: directory said 975 E Gateway Blvd, portal says 975 West Gateway
Blvd Suite 105), the AOR wins and the discrepancy is noted.

Portal AORs needed real parsing care, all fixed in the converter:

- Suites in their own comma part ("131 North 2nd St, Ste# 220-222, Fort
  Pierce, FL 34950") — parsed from the `, ST ZIP` tail, so the suite can
  never displace the city again (it did for 7 records in the converter's
  first draft).
- All-caps portal spellings normalized to official municipality names:
  FT LAUDERDALE → Fort Lauderdale, GREEN ACRES → Greenacres, PORT SAINT
  LUCIE → Port St. Lucie.
- Superseded municipality names: LAKE WORTH → Lake Worth Beach (renamed
  2019, as [locations.md](locations.md) documents).
- ZIP is carried only when the source shows one, never guessed (schema
  allows `zip: null`).

## Watchlist disambiguation

The validator requires unique business names in each tier. Two same-named
pairs at *different* addresses are distinct locations, not duplicates —
they ship with their street in the name for disambiguation: "Hand & Stone
Massage and Facial Spa (9144 S Federal Hwy, East Port, at Walton Rd)" and
"Oriental Massage & Spa (5140 Coconut Creek Pkwy)". Same name *and* same
street is a true duplicate and is dropped.

## What's next

The unchecked 283 are the next cycle's first cut (a second pass on the
same corridor), then the interior counties (Wellington, Coral Springs,
Miami interior). Licenses expiring 2027-08-31 age into the "expiring soon"
filter before the next annual release and need re-verification. The 44
watchlist entries need re-search on their documented terms — a renewal
moves an entry out of the watchlist.
