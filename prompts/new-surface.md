# Prompt: Port FED-SPA to a New Platform Surface

> Copy everything below the line into your assistant. Fill in the bracketed parts before sending.

---

You are helping me port **FED-SPA** to a new platform surface. FED-SPA is a no-backend static directory of licensed Florida massage establishments: a public licensed list (plaintext JSON) plus a subscriber-only encrypted watchlist (decrypted in-app with a shared code). It currently ships to six surfaces — web PWA, browser extension, Android, Android Auto, smart watch, iOS — and I want to add another.

**Non-negotiable constraints for the port:**

1. **No backend** — the surface reads bundled static data only. No API calls, no sync, no accounts.
2. **No third-party** — only the platform's own first-party libraries and standard runtime. No package managers beyond what the platform itself requires, no analytics, no tracking SDKs.
3. **Annual cadence** — data is refreshed once a year by regenerating and re-shipping files. No live-data assumptions.
4. **Byte-compatible crypto** — if the surface supports the subscriber tier, it must decrypt the existing envelope with only first-party crypto. Spec: `wiki/Crypto-envelope-spec.md` (PBKDF2-SHA256 @ 310,000 iterations from the envelope field, 16-byte salt, 12-byte IV, AES-256-GCM, auth tag appended to ciphertext, base64 in `{v, kdf, iterations, salt, iv, data}`).

**My target platform:** [e.g. Android TV / WearOS square / a car head unit / a Linux desktop app]

**What the platform gives me to work with:** [language, UI toolkit, crypto APIs available, file-asset mechanism, screen size and input model]

**What I want from you:**

1. **A file tree for the new surface** in the same style as the existing ones (`android/`, `android_auto/`, `watch/`, `ios/`): module skeleton, entry activity/view, data asset folder, resources, and a README explaining the build.
2. **A data-loading plan** using the platform's own file APIs, mirroring how the Android surfaces read `assets/data/licensed.json` and how iOS reads `Resources/Data/`. The fan-out script `admin_scripts/generate_public_files.py` must gain this surface as a destination — tell me exactly what to add to its `DESTINATIONS` list.
3. **A crypto implementation** (only if the surface carries the subscriber tier) in the platform's first-party crypto, following the spec's derive-then-decrypt two steps and the appended-tag split (`ciphertext = raw[0 .. count-16]`, `tag = raw[count-16 .. count]`). If the platform's crypto can't do PBKDF2-SHA256 + AES-GCM natively, say so honestly and recommend the surface ship **licensed-only** like Android Auto and the watch do — that's an accepted pattern, not a failure.
4. **A UI plan** using the shared design tokens (bg `#0b0e14`, raised `#131824`, inset `#0d1117`, border `#263042`, text `#e6e9ef`, muted `#9aa4b5`, faint `#6b7687`, accent `#2dd4a7`, danger `#ff5f6d`, warning `#f2c14e`) and the identical status color mapping (clear/active → `#2dd4a7`; delinquent/probation → `#f2c14e`; expired/revoked/no_license_found → `#ff5f6d`; else → gray/muted). If the platform can't do dark-on-dark, adapt the tokens — don't invent a new palette.
5. **A capability decision table** like the one in `wiki/Platform-surface-map.md`: which tiers the surface carries, whether it has search, whether it remembers the code, and *why* — the "why" column is what makes the map useful.
6. **A CI addition** if the platform has a no-third-party build check available (GitHub-owned actions only — `actions/checkout`, `setup-python`, `setup-node`, `upload-artifact` are the allowed set in `.github/workflows/build.yml`).

**Rules for you:**

- If my platform description implies a server or a service, stop and re-ask.
- Never propose a third-party library as a shortcut, even a "tiny" one, even for "just icons."
- Licensed-only is a legitimate design for constrained surfaces — recommend it when crypto or input makes the subscriber tier a bad fit, and say why in one sentence.
- Keep the new surface's code style consistent with its siblings: IIFE/namespace pattern for JS, single-activity Kotlin with classic views, SwiftUI single-scene for Apple platforms.
- Remind me at the end to update `wiki/Platform-surface-map.md` and the fan-out script — a new surface that isn't in the map or the fan-out is half-shipped.
