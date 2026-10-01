# Prompt: Verify a Record Against the MQA Portal

> Copy everything below the line into your assistant. Fill in the bracketed parts before sending.

---

You are helping me verify a single Florida massage establishment record for **FED-SPA**, a no-backend static directory of licensed massage establishments, verified against the Florida DOH MQA portal at https://mqa-internet.doh.state.fl.us/MQASearchServices/HealthCareProviders

Constraints that apply to this task: no backend, no third-party tools, and the data refreshes once a year. I did the portal lookup myself — you are helping me turn what I saw into a correctly-shaped record, not doing the verification for me.

**What I saw on the portal:**

- Business name shown: [exact name]
- Search terms I used: [name / address / license number]
- License number: [e.g. MM41109]
- License status: [Clear / Active / Delinquent / Expired / Inactive / Probation / not found]
- Issue date: [YYYY-MM-DD or unknown]
- Expiration date: [YYYY-MM-DD or unknown]
- Street address: [as shown]
- City, state, ZIP: [as shown]
- Discipline on file: [Yes / No]
- Public complaint: [Yes / No]
- Date I performed this search: [YYYY-MM-DD]

**What I want from you:**

1. Produce a record in exact `data/meta/schema.json` shape for `data/public/licensed.json` — correct field names, ISO dates, `verified_by` set to the MQA portal URL, `last_checked` set to my search date, and `data_as_of` set to the release date.
2. If what I described doesn't cleanly map to a licensed status — for example the search returned zero matches, or the license shows expired/revoked — say so explicitly and draft it as a **watchlist** record instead, with a `status_note` that captures exactly what I searched, when, and what came back. "No license found" must never be softened into "unlicensed."
3. Point out anything suspicious in my transcription: a ZIP that doesn't match the city, a license number that doesn't fit the MM pattern, an expiry more than ~2 years out, a status word that isn't in the taxonomy. Ask me to re-check the portal rather than guessing.
4. Do not add fields that aren't in the schema. Do not add ratings, reviews, phone numbers, or "helpful" extras — the schema is deliberately minimal.

**Hard rules:**

- Never fabricate or assume any portal value. Every field must trace to something I gave you above; if it's missing, ask.
- If the result is a watchlist entry, remind me that it will be encrypted via the annual workflow (`SCRAPE=0` path in `admin_scripts/merge_and_encrypt.sh`) and that the plaintext must never be committed.
- If I haven't given you a search date, refuse to produce a final record — the check date is the load-bearing field of the whole project.

**The licensed status taxonomy:** Clear · Active · Delinquent · Expired · Inactive · Probation
**The watchlist status taxonomy:** no_license_found · expired · inactive · revoked · delinquent
**Status color mapping (identical on every surface):** clear/active → green; delinquent/probation → yellow; expired/revoked/no_license_found → red; anything else → gray.
