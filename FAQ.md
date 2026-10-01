# FAQ — The Root Edition

The wiki has the long [FAQ](wiki/FAQ.md); this root version is the fast one — the ten questions that decide whether you use, fork, or argue with FED-SPA, answered without a click-through. When this page and the wiki disagree, the wiki wins and this page gets fixed.

## Is the data current?

It's current **as of its check dates**. Every record shows when it was last verified against the MQA portal, and every surface shows the release's `data as of` date. The project refreshes **once a year** — between refreshes, a license can expire or be revoked without our knowledge. The portal is the live authority; FED-SPA is the organized snapshot of it. Verify there before acting on anything: https://mqa-internet.doh.state.fl.us/MQASearchServices/HealthCareProviders

## Is this official?

No. Independent, volunteer-run, unaffiliated with the State of Florida or any agency — see [NOTICE.md](NOTICE.md). What it *is*: public records, checked by hand, with the check dates attached.

## What does the subscriber code unlock?

The **watchlist tier** — establishments where a documented portal search found no license match. It decrypts on your device only. It does **not** unlock anything else; the licensed list is and stays free, plaintext, and auditable.

## Is "no license found" the same as "unlicensed"?

**No, and this is the most important answer on the page.** It means our search — the terms we used, on the date we recorded — returned zero matches. Name mismatches, relocations, and renewals lapsed after our check all look identical from the outside. Every watchlist record carries its search details in `status_note`. It's a prompt to ask questions, never a verdict.

## Why is there no backend?

Because a backend would make us a data processor: codes to store, logs to keep, an attack surface, an uptime promise, a bill. Static files make the project free to run, trivially rollback-able, and exactly what they claim to be. The costs (no accounts, no live data) are the design. Full argument: [README](README.md) → the three constraints, and ADR-001.

## Why no third-party libraries?

Because dependencies rot, and this project is built to run for a decade on volunteer weekends. Six surfaces with zero dependencies is more work up front (the crypto envelope exists five times, per [wiki/Crypto-envelope-spec.md](wiki/Crypto-envelope-spec.md)) and near-zero work afterward. CI uses only GitHub's own actions for the same reason.

## Why is Android Auto / my watch licensed-only?

Data minimization. A car needs glanceable answers, and a watch screen can't render the context that makes watchlist records honest. The full decision matrix: [wiki/Platform-surface-map.md](wiki/Platform-surface-map.md).

## How do I get my business corrected / removed?

The same way any record changes: the **Data correction** issue template with what the MQA portal shows now and your re-check date. If our search missed a license, showing it fixes the record — that's the pipeline working. We're not a listing service or a takedown service; the portal is the source of record either way. See [SUPPORT.md](SUPPORT.md).

## Can I fork this for another state?

Yes — that's the design. The structure (schema, workflow, envelope, six surfaces) is portable; keep the three constraints if you want it to stay this cheap to run. The dataset is ODbL ([COPYING.md](COPYING.md)), the code is MIT ([LICENSE](LICENSE)), and `prompts/new-surface.md` is the porting checklist in prompt form.

## Why does it cost anything at all?

The licensed list is free forever. The watchlist tier has a one-time code to keep the tier from being a free ammunition list — priced to cover nothing but the annual checking weekend. It's a tip-jar economy, not a business: [PRICING.md](PRICING.md).

## Still stuck?

[SUPPORT.md](SUPPORT.md) is the routing table — data corrections, bugs, questions, and the requests that will never merge. The deep versions of every answer here live in the [wiki FAQ](wiki/FAQ.md), and the standing invitation is real: if you think the constraints are wrong, Discussions — General is where that argument belongs.
