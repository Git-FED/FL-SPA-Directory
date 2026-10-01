# Data statistics

Counts per refresh. Update this page at every annual release (it's part
of the ship checklist in `annual_update_workflow.md`).

## Current release — as of 2026-09-07

| Metric | Count |
|---|---|
| Licensed establishments | 1 |
| Counties covered | 1 (Palm Beach) |
| Licensed statuses represented | 1 (Clear) |
| Unlicensed watchlist entries | 0 (tier ships empty until first subscriber release) |

### The seed record

The current dataset is the verified seed entry — one establishment,
hand-checked against the MQA portal on 2027 dates listed in the record:

- **Halo Asian Spa, Inc** — MM41109, Clear, expires 2027-08-31,
  Boynton Beach (Palm Beach County)

It exists to prove the pipeline end-to-end: schema, validator, encryptor,
fan-out to all six platforms, decryption on every client. The next
refresh grows the list from here.

## Historical releases

| Tag | As-of date | Licensed | Unlicensed | Notes |
|---|---|---|---|---|
| data-2026 | 2026-09-07 | 1 | 0 | Initial seed release |

## Status taxonomy

Licensed tier statuses (from the MQA portal):

`Clear · Active · Delinquent · Expired · Inactive · Probation`

Unlicensed tier reasons:

`no_license_found · expired · inactive · revoked · delinquent`

## County coverage ambitions

Palm Beach is covered (seed). The refresh procedure targets statewide
coverage — Miami-Dade, Broward, Orange, Hillsborough first (highest
establishment counts per DOH annual reports).
