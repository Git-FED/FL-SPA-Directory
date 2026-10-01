# Prompt: Annual Refresh Walkthrough

> Copy everything below the line into your assistant. Fill in the bracketed parts before sending.

---

You are helping me run the annual data refresh for **FED-SPA**, a no-backend static directory of licensed Florida massage establishments. The project has three non-negotiable constraints — repeat them back to me before we start so I know you understand:

1. **No backend**: static files only. No servers, no APIs, no databases. Data ships as JSON files.
2. **No third-party**: no external libraries, SDKs, services, or analytics on any surface. Python stdlib only, Node's native crypto only, vanilla JS/CSS only, androidx core + appcompat only, SwiftUI + CryptoKit + CommonCrypto only.
3. **Annual cadence**: this refresh happens once per year. Solutions that assume live data are wrong for this project.

The refresh workflow is documented in `docs/annual_update_workflow.md` in the repo. The steps are: **discover → edit sources → validate → encrypt → fan-out → ship and tag**. The one-command runner is `admin_scripts/merge_and_encrypt.sh` (set `SCRAPE=0` for the manual path, `SCRAPE=1` to run the portal fetch helper).

My context for this year:

- Release version I'm building: [e.g. 2027.1]
- Today's date: [YYYY-MM-DD]
- New/corrected records I gathered manually this year: [paste records here, or "none yet — help me plan the checklist first"]

What I want from you:

1. Walk me through the workflow one step at a time, in order, waiting for me to confirm each step is done before moving to the next.
2. At the **edit sources** step, help me write the records in exact `data/meta/schema.json` shape — field names, date formats (ISO `YYYY-MM-DD`), and the required `status_note` for any watchlist entry.
3. At the **validate** step, remind me what `admin_scripts/validate_schema.py` checks and what to do if it fails.
4. At the **encrypt** step, remind me of the envelope contract (PBKDF2-SHA256, 310,000 iterations, AES-256-GCM, appended tag) and that the plaintext file `data/private/unlicensed.plain.json` must never be committed — `.gitignore` covers it, but verify before pushing.
5. At the **fan-out** step, remind me that `admin_scripts/generate_public_files.py` writes to six destinations and that CI's drift check will fail the build if I forget to re-run it after editing source data.
6. At the **ship** step, help me write the changelog entry, the wiki Annual-refresh-log row, and the `data-<year>` tag.

Rules for you during this session:

- If I propose anything that needs a server, a cron job, a service, or a third-party library, stop me and say why it violates the constraints.
- If I'm about to commit plaintext watchlist data, stop me immediately.
- Never invent an MQA portal result. If a record lacks a real check date from me, treat it as unfinished, not as verified.
- You may draft record JSON and changelog text, but the final go/no-go on each record is mine, because I'm the one who actually looked at the portal.
