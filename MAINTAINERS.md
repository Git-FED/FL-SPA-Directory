# MAINTAINERS

Who maintains FED-SPA, what they own, and how to reach the right person. For how decisions are made, see [GOVERNANCE.md](GOVERNANCE.md); for conduct enforcement escalation, see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Current maintainers

| Name | Role | Owns | Contact |
|---|---|---|---|
| _[YOUR NAME / HANDLE]_ | Founder & maintainer | everything, until someone shares it | _[GitHub profile / email]_ |

> **This table is meant to be edited.** Fill in your handle on fork/adoption, and add a row per new maintainer. Roles below describe how the load divides when there's more than one person carrying it.

## The maintainer jobs

The annual cycle needs one person per job; one person can hold several (today: all of them). None of these are lifetime appointments — [GOVERNANCE.md](GOVERNANCE.md) covers the two-cycle emeritus rule.

**Data lead.** Runs the annual refresh end-to-end: the portal checklist, record edits, validation, encryption, fan-out, and the `data-<year>` tag. Owns the Data correction issue queue. This is the project's heartbeat; if only one job is staffed, it's this one.

**Crypto owner.** Guards the envelope contract ([wiki/Crypto-envelope-spec.md](wiki/Crypto-envelope-spec.md)). Any PR touching crypto routes through this role; all five implementations change together or not at all. Owns the CI round-trip gate.

**Surface owners** (one per platform, when staffed): **web**, **extension**, **android**, **android_auto**, **watch**, **ios**. Each owns their surface's bug queue, its design-token fidelity ([ADR-008](ADR.md)), and its store/package presence (signing keys, listings, review responses).

**Community lead.** Tends Discussions, triages the issue templates, and handles first-line conduct enforcement per the Code of Conduct. Escalates conflicts of interest to a different maintainer.

**Code distributor.** Owns the subscriber code rotation and distribution channels per [docs/password_distribution.md](docs/password_distribution.md), and the Ko-fi tip jar bookkeeping (which is to say: watching it exist). Bound by the one money rule in [GOVERNANCE.md](GOVERNANCE.md): money never buys a data decision.

## Response expectations (set by the annual cadence)

Volunteers, once-a-year project: there is no SLA, and this page should never imply one. Practical norms — issues triaged within a week or two; data corrections batched toward the refresh window, with obviously-wrong data (bad address, wrong expiry) prioritized whenever seen; Discussions answered as time allows. If a maintainer is mid-burnout, the correct behavior is silence, not guilt — the cadence is designed to survive that.

## Succession & handoff checklist

Transferring a role (or the whole project) privately, maintainer-to-maintainer:

1. Repo access and the maintainer table above updated.
2. For surface owners: the platform signing key/keystore (`*.keystore`/`*.jks` are gitignored by design) and store listing access.
3. For the code distributor: the subscriber-code distribution channel and the Ko-fi account.
4. For the data lead: the current annual checklist state and any in-flight corrections.
5. A note in [wiki/Annual-refresh-log.md](wiki/Annual-refresh-log.md) if a refresh was mid-flight at handoff.

If nobody takes over: [GOVERNANCE.md](GOVERNANCE.md) — the project rests gracefully, the README gets "unmaintained since <year>," and the data's check dates stay honest forever. That outcome is designed for, not feared.

## Emeritus

| Name | Served | Note |
|---|---|---|
| _—_ | | _First entries appear here when maintainers step back._ |

Emeritus maintainers keep credit in [AUTHORS.md](AUTHORS.md), hold no obligations, and are welcome back anytime the annual cycle calls.
