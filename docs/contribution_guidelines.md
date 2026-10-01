# Contribution Guidelines

Thanks for wanting to help. FED-SPA is deliberately weird: no backend,
no third-party code, annual manual data refreshes. Most of these rules
exist to protect that.

## The three constraints (non-negotiable)

1. **No backend.** Static files only. If your change needs a server, an
   API, or a database, it will be declined. Client-side everything.
2. **No third-party anything.** No libraries, no frameworks, no CDNs, no
   web fonts, no analytics, no "just one tiny dependency". Python
   stdlib, Node built-ins, vanilla JS/CSS, platform SDKs (Android, iOS).
   If it isn't shipped with the platform, we don't use it.
3. **No tracking.** No accounts, no telemetry, no phoning home. Nothing
   leaves the device.

If your idea conflicts with one of these and you still think it's worth
it, open a Discussion first — don't write the code.

## Ways to contribute

### Data corrections (highest value)
Found a wrong record? Use the **Data correction** issue template. You
must check the MQA portal yourself and include what it showed plus the
date. Corrections ship annually (or as a hotfix for serious errors).

### Bugs and features
Use the issue templates. Features must fit the constraints — the
template asks you to confirm.

### Code
1. Fork, branch (`fix/…` or `feat/…`)
2. Make the change
3. Run the checks:
   ```bash
   python3 admin_scripts/validate_schema.py
   python3 admin_scripts/generate_public_files.py && git diff --exit-code
   node --check admin_scripts/encrypt_unlicensed.js
   ```
4. PR with the template filled out honestly

### Docs and community files
Typos and clarity fixes are always welcome. Keep the tone plain.

## Surface-specific notes

- **Web/extension**: vanilla JS (IIFE namespaces `FedSpaUI`,
  `FedSpaSearch`, `FedSpaCrypto`), vanilla CSS with shared design tokens
  (see `styles.css` at repo root and `web/css/style.css`). No build
  step, no bundler, no transpiler.
- **Android**: classic views + Kotlin, androidx core/appcompat only.
  No Compose, no Retrofit, no Gradle version catalogs.
- **iOS**: SwiftUI + Foundation + CryptoKit + CommonCrypto only. Zero
  SPM dependencies.
- **Crypto**: the envelope format is a cross-platform contract. Any
  change must update ALL FIVE implementations in the same PR (Node
  encryptor, web, extension, Android, iOS) plus the schema docs. The PR
  template has the checklist.

## Data contribution rules

- Never commit `data/private/unlicensed.plain.json` (it's gitignored;
  CI would catch it, but don't make us find out)
- Never paste subscriber-tier content into issues, PRs, or discussions
- Every licensed record needs `data_as_of` + `last_checked`
- The validator (`admin_scripts/validate_schema.py`) is the gate; it
  must pass with zero warnings

## Code style

- Comments explain *why*, especially around crypto and the no-backend
  decisions. Future maintainers need the reasoning, not the mechanics.
- Python: stdlib idioms, `dataclasses`/`json`/`re`, no comprehension
  soup
- Kotlin: explicit types on public APIs, no clever operators
- Swift: `swift-format` defaults, no force unwraps
- JS: no async/await chains where a promise is clearer; no optional
  chaining cascades that hide errors

## Release cadence

Data ships annually. Code ships when it's ready. Both are tagged
(`data-<year>`, `v<semver>`).
