# FED-SPA Pull Request

## What does this PR do?

<!-- One or two sentences. -->

## Surface(s) touched
- [ ] Web (web/)
- [ ] Extension (extension/)
- [ ] Android (android/)
- [ ] Android Auto (android_auto/)
- [ ] Watch (watch/)
- [ ] iOS (ios/)
- [ ] Data (data/)
- [ ] Admin scripts (admin_scripts/)
- [ ] Docs/community (.github/, docs/, root files)

## The three constraints (must all be checked)

- [ ] **No backend** — everything stays static files; no server code added
- [ ] **No third-party anything** — no new libraries, services, CDNs, fonts, or references to other projects
- [ ] **No tracking/accounts/telemetry** — nothing phones home

## Data changes (delete if N/A)

- [ ] I ran `python3 admin_scripts/validate_schema.py` — passes
- [ ] I ran `python3 admin_scripts/generate_public_files.py` — all six platform copies updated
- [ ] The subscriber plaintext (`data/private/unlicensed.plain.json`) is NOT in this diff

## Crypto changes (delete if N/A)

If the envelope format changed, I updated ALL of:
- [ ] `admin_scripts/encrypt_unlicensed.js` (Node encryptor)
- [ ] `web/js/crypto.js` + `extension/popup/popup.js` (Web Crypto)
- [ ] `android/.../CryptoHelper.kt` + `watch/.../CryptoHelper.kt` (javax.crypto)
- [ ] `ios/CryptoManager.swift` (CommonCrypto + CryptoKit)
- [ ] `data/meta/schema.json` envelope documentation

## Checklist
- [ ] I tested the change on at least one surface
- [ ] Docs updated if behavior changed
- [ ] `CHANGELOG.md` entry added
