# Subscriber Password Distribution

The unlicensed watchlist tier is encrypted with a single shared password
(a "subscriber code"). This doc explains the model, the trade-offs, and
the mechanics of getting the code to subscribers without a backend.

## The model

- **One code, all subscribers.** The envelope
  (`data/private/unlicensed.encrypted.json`) is AES-256-GCM encrypted;
  every subscriber's code is the same key.
- **No accounts, no auth server.** FED-SPA has no backend by design, so
  there's nothing to log into. Possession of the code *is* the subscription.
- **The code never travels with the data.** The encrypted envelope is
  public in the repo; the code is distributed out-of-band. Someone
  cloning the repo gets ciphertext and nothing else.

## Threat model (be honest about this)

A shared password means:

1. One leaked code leaks for everyone until the next annual refresh.
2. Nothing stops a subscriber from sharing the code. We accept this —
   the tier exists to inform, not to run a DRM business.
3. Anyone who obtains the code can decrypt past AND future envelopes
   unless the password rotates.

Rotation (below) is the mitigation.

## Distribution channels (pick per cohort)

| Channel | Good for | Notes |
|---|---|---|
| Email to verified supporters | Ko-fi subscribers | Send on annual refresh day |
| DM on the platform they subscribed from | small cohorts | Manual but fine at this scale |
| Printed card / QR at in-person events | local outreach | Code on the flip side |

What we never do: paste the code in a public repo file, a public
discussion, a wiki page, or any CI log.

## Annual rotation procedure

At each data refresh (see `annual_update_workflow.md`):

1. Generate a new code — e.g. `python3 -c "import secrets; print(secrets.token_urlsafe(12))"`
2. Encrypt the new envelope with it (step 4 of the workflow)
3. Send the new code to current subscribers through their chosen channel
4. Retire the old code — it simply stops decrypting the new envelope;
   clients show "That code didn't decrypt the watchlist."

Because rotation happens yearly with the data, a leaked code has a
maximum useful life of one refresh cycle.

## Client behavior on wrong/old codes

All surfaces show the same message ("that code didn't decrypt") because
AES-GCM authentication fails identically on wrong key and tampered
ciphertext. No oracle, no partial reveals.

## What's stored on devices

- Web: code in `sessionStorage` only while the tab session lives (gone
  on browser close)
- Extension: `chrome.storage.local` **only** if the user opted into
  "remember my code"
- Android: `SharedPreferences` only with opt-in
- iOS: `UserDefaults` only with opt-in

Every settings UI states this in plain language. Auto/Wear don't ship
the subscriber tier at all.
