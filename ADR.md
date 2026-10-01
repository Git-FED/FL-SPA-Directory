# ADR — Architecture Decision Records

The decisions that made FED-SPA what it is, recorded so future contributors (and future maintainers, and the future *you*) can tell deliberate design from accident. Each record states the context, the decision, and the reasoning — the constraints are permanent; the decisions within them can be revisited, but only through a new ADR, never a quiet rewrite.

Format is deliberately lightweight: number, status, and the three sections that matter.

---

## ADR-001: No backend. Static files only.

**Status:** Accepted — permanent constraint.

**Context:** FED-SPA needs to publish a verified directory to six surfaces (web, extension, Android, Android Auto, watch, iOS) with no budget, no staff, and a maintenance cadence of one weekend per year.

**Decision:** There is no server anywhere in the project. All data ships as static files bundled with each surface. The "backend" is `admin_scripts/` run once a year by a maintainer.

**Reasoning:** A backend makes us a data processor: subscriber codes to store, requests to log, an attack surface to defend, an uptime promise to break, and a bill. Static files make the project infinitely cheap, instantly rollback-able (the previous tag), and honest — what you download is what runs. The costs are real and accepted: no live data, no accounts, no per-subscriber access control. Every downstream decision in this file exists to make those costs livable.

---

## ADR-002: No third-party code, on any surface.

**Status:** Accepted — permanent constraint.

**Context:** Six platforms means six runtimes; the temptation is one shared library or framework per platform to unify them.

**Decision:** Only first-party platform code: Python stdlib, Node's native `crypto`, vanilla JS/CSS (no framework, no build step), androidx core-ktx + appcompat only, SwiftUI + CryptoKit + CommonCrypto with zero SPM dependencies. CI uses only GitHub-owned actions.

**Reasoning:** Dependencies are the thing that rots. A six-surface, decade-lifespan project held together by pinned third-party libraries is a maintenance mortgage — security patches you don't control, API churn you didn't cause, and a bus factor made of other people's repos. The cost is duplication: the crypto envelope exists five times (see ADR-004), and every UI is hand-rolled. We pay it consciously, because the alternative is paying a subscription forever in volunteer time.

---

## ADR-003: Two tiers — public licensed list, encrypted watchlist.

**Status:** Accepted.

**Context:** The licensed list is public record, free to publish. The watchlist (no-license-found observations) is different: publicizing it as plaintext invites scraping, rehosting without dates/context, and targeting campaigns against named businesses.

**Decision:** Two data tiers. The licensed list ships as plaintext JSON, committed and auditable. The watchlist ships as a client-side-encrypted envelope, decrypted in-app with a shared subscriber code. Android Auto and the watch ship licensed-only.

**Reasoning:** The encryption is an **access tier, not a security system** — a shared symmetric code is a speed bump, not a vault ([SECURITY.md](SECURITY.md) states this openly). What it buys: a token price for honest access, a friction layer against casual rehosting, and a distribution channel that carries the context (dates, search notes) with the data. What it costs: no real secrecy against a determined code-holder, accepted per [COPYING.md](COPYING.md) — the data itself is ODbL once accessed; the encryption is not a protection measure and never claimed to be. Auto/watch being licensed-only is data minimization on constrained surfaces (ADR-007).

---

## ADR-004: The crypto envelope is a frozen, five-implementation byte contract.

**Status:** Accepted — frozen at v1.

**Context:** With no shared runtime across the surfaces, the envelope must be decryptable by Web Crypto (web + extension), `javax.crypto` (Android/Auto/watch), CommonCrypto + CryptoKit (iOS), and produced by Node's native crypto — with no library shared between any of them.

**Decision:** The envelope is specified byte-by-byte in [wiki/Crypto-envelope-spec.md](wiki/Crypto-envelope-spec.md): PBKDF2-SHA256 at 310,000 iterations (read from the envelope), 16-byte salt, 12-byte IV, AES-256-GCM, **auth tag appended to ciphertext**, all fields base64 in `{v, kdf, iterations, salt, iv, data}`. Any crypto change requires all five implementations to change in lockstep and the envelope `v` to bump.

**Reasoning:** Cross-platform crypto drift fails silently — one platform's "can't decrypt" looks like a wrong code to the user, and debugging it means guessing which implementation drifted. A written, frozen spec plus CI's round-trip self-test (which proves the appended-tag layout on every push) turns that class of silent failure into a build failure. The specific choices (PBKDF2 over Argon2, appended tag) are the conservative picks that every first-party crypto stack supports natively — exactly what ADR-002 demands.

---

## ADR-005: One source of truth, fanned out by a script.

**Status:** Accepted.

**Context:** Six surfaces each bundling their own data copy is six chances to disagree about reality.

**Decision:** `data/public/licensed.json` (plus the encrypted envelope) is the single source. `admin_scripts/generate_public_files.py` writes every surface's bundled copy, stripping maintainer-internal fields. CI's drift check re-runs the fan-out and fails on any difference.

**Reasoning:** The failure mode of a multi-surface directory is surfaces showing different `as_of` dates for the same record — user trust dies there. Single-source + generated copies + a CI drift check makes that failure mode structurally impossible instead of procedurally avoided. The fan-out also handles per-surface needs (the `verified_by` field is stripped from bundled copies; each surface gets the fields it renders).

---

## ADR-006: Annual cadence, stated plainly everywhere.

**Status:** Accepted.

**Context:** Manual, per-record verification against the MQA portal is minutes-per-record work that a volunteer does once a year. Pretending otherwise (auto-refresh, update nagging) would misrepresent the data's freshness.

**Decision:** One data release per year, tagged `data-<year>`. Every surface displays the release date and record count. No refresh mechanism, no polling, no "update available" UI. The workflow is documented ([docs/annual_update_workflow.md](docs/annual_update_workflow.md)) and every release is logged ([wiki/Annual-refresh-log.md](wiki/Annual-refresh-log.md)).

**Reasoning:** Honesty about freshness *is* the product — the record's check date is the most load-bearing field in the dataset. A live-feeling UI over year-old data would be a lie with better animation. The surfaces instead surface the date prominently and link to the portal for anything that matters, making "verify before you act" the standing instruction on every surface.

---

## ADR-007: Constrained surfaces ship licensed-only.

**Status:** Accepted.

**Context:** Android Auto and smart watches can technically run the decrypt logic (the watch even carries a byte-compatible `CryptoHelper.kt`), but the surfaces themselves are wrong for the subscriber tier: a car is for glanceable answers, a watch screen can't render the context that makes watchlist records honest.

**Decision:** Auto and watch ship the licensed tier only. The crypto helpers remain in their codebases, tested and byte-compatible, for the future.

**Reasoning:** Data minimization is the honest rule: don't ship the sensitive tier to a surface that can't treat it responsibly. The decision matrix with per-surface reasoning is [wiki/Platform-surface-map.md](wiki/Platform-surface-map.md) — including the flip side: a surface that *can* support both tiers properly (web, extension, Android, iOS) does.

---

## ADR-008: Status colors and design tokens are cross-surface contracts.

**Status:** Accepted.

**Context:** Six hand-rolled UIs (no shared framework, per ADR-002) could each develop their own idea of what "Delinquent" looks like.

**Decision:** A single token set (background `#0b0e14` / raised `#131824` / inset `#0d1117`, border `#263042`, text `#e6e9ef` / muted `#9aa4b5` / faint `#6b7687`, accent `#2dd4a7`, danger `#ff5f6d`, warning `#f2c14e`) and a single status-color mapping (clear/active → green; delinquent/probation → yellow; expired/revoked/no_license_found → red; else → gray) apply identically on every surface. The mapping is documented in the [platform map](wiki/Platform-surface-map.md) and `styles.css`.

**Reasoning:** A directory's credibility is partly visual: if the same status renders different colors on the phone and the watch, the user stops trusting both. The tokens are duplicated per-platform (the no-third-party cost again) but they are *duplicated*, not *reinterpreted* — and a PR that "fixes" one surface's token is a defect, not an improvement.

---

## ADR-009: Errors are never silent; records are never rewritten.

**Status:** Accepted.

**Context:** A data directory's worst failure is quiet wrongness — a record that looks fine and isn't, or history that pretends it never erred.

**Decision:** Three honest fields on every record (`verified_by`, `last_checked`, `data_as_of`); a mandatory `status_note` documenting the search on every watchlist record; crypto failures surface as exactly three named classes (bad envelope / key derivation failure / wrong code) on every platform; the changelog and refresh log append, never rewrite — corrections get follow-up entries.

**Reasoning:** This project's entire value is that its claims are auditable. A record without a check date is unverifiable; an edited history is unauditable; a silent crypto failure is indistinguishable from wrong data. The extra fields and the append-only logs are cheap; the trust they buy is the product.

---

*New ADRs append below this line. Statuses move (Accepted → Superseded, with a pointer to the successor record); records are never deleted.*
