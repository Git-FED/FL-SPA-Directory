# Crypto Envelope Spec

**Status: frozen.** This is the byte-level contract shared by every implementation in the repo. Five implementations depend on it: the Node encryptor, the Web Crypto code in the web app, the Web Crypto code in the browser extension, `javax.crypto` on Android / Android Auto / watch, and CommonCrypto + CryptoKit on iOS. Change any field of this spec and all five must change in lockstep — or one platform silently fails to decrypt.

**If you change this spec, you must re-run the full decrypt-compatibility matrix in `.github/workflows/build.yml` and bump the envelope `v` field.**

## 1. The envelope object

```json
{
  "v": 1,
  "kdf": "PBKDF2-SHA256",
  "iterations": 310000,
  "salt":     "<base64, 16 bytes>",
  "iv":       "<base64, 12 bytes>",
  "data":     "<base64, AES-256-GCM ciphertext + 16-byte auth tag APPENDED>"
}
```

| Field | Type | Meaning |
|---|---|---|
| `v` | int | Envelope format version. Currently `1`. Bump on any incompatible change. |
| `kdf` | string | Always `"PBKDF2-SHA256"`. A future envelope may name another KDF; readers must reject unknown values. |
| `iterations` | int | PBKDF2 iteration count. Currently `310000` (OWASP 2023 guidance for PBKDF2-SHA256). |
| `salt` | base64 | 16 random bytes, one per envelope, generated fresh at encrypt time. |
| `iv` | base64 | 12 random bytes — the AES-GCM nonce. One per envelope. Never reused with the same key. |
| `data` | base64 | Ciphertext immediately followed by the 16-byte GCM auth tag. No separator. No length field. |

## 2. Deriving the key

The passphrase is the shared subscriber code, treated as raw UTF-8 bytes — no normalization, no trimming. (The UI may trim whitespace on entry, but the crypto functions receive exactly what the user typed.)

```
key = PBKDF2-SHA256(password = code_utf8, salt = salt_16B, iterations = 310000, dkLen = 32)
```

- The derived key is **32 bytes** — a full AES-256 key.
- dkLen is fixed by the spec. Do not derive other lengths.
- `iterations` comes from the envelope so a future release can raise the cost without a format break; readers use the envelope value, not a hardcoded constant. (The Node encryptor also reads it from the envelope when re-encrypting.)

## 3. Encrypting

```
plaintext   = UTF-8 JSON of the watchlist document  (see §5)
salt        = random(16)
iv          = random(12)
key         = PBKDF2-SHA256(code, salt, iterations, 32)
ciphertext  = AES-256-GCM(key, iv, plaintext)  ->  ciphertext || tag(16)
data        = base64(ciphertext || tag)
```

**The auth tag is APPENDED to the ciphertext, not stored separately.** This is the single most load-bearing decision in the spec, because each platform's default concatenation order differs:

| Platform | Library call | Why appended works there |
|---|---|---|
| Node (encryptor) | `crypto.createCipheriv('aes-256-gcm', key, iv)` then `cipher.getAuthTag()` | Encryptor explicitly appends `getAuthTag()` to the final buffer before base64. |
| Web / Extension | Web Crypto `AES-GCM` | Web Crypto always returns ciphertext-with-appended-tag — the native format. |
| Android / Auto / Watch | `Cipher.getInstance("AES/GCM/NoPadding")` + `GCMParameterSpec(128, iv)` | javax produces cipher-then-tag when the tag isn't set separately; decryptors split it back out. |
| iOS | CryptoKit `AES.GCM.SealedBox` | `combined` representation is ciphertext-then-tag; we build the box manually as `nonce:ciphertext:tag:` from the split parts. |

Decryption on every platform therefore follows the same two steps: base64-decode `data` into `raw`, take `raw[0 .. raw.count - 16]` as ciphertext and `raw[raw.count - 16 .. raw.count]` as the tag, then authenticate-and-decrypt with `(key, iv)`.

## 4. Plaintext document format

The decrypted plaintext is always a UTF-8 JSON document of shape:

```json
{
  "as_of": "2026-09-07",
  "version": "2026.1",
  "records": [
    {
      "name": "Example Business",
      "status": "no_license_found",
      "status_note": "MQA search 2026-09-07, business name + address, 0 matches",
      "last_checked": "2026-09-07",
      "verified_by": "https://mqa-internet.doh.state.fl.us/MQASearchServices/HealthCareProviders",
      "address": { "street": "1 Main St", "city": "Orlando", "state": "FL", "zip": "32801" }
    }
  ]
}
```

Rules:

- `as_of` / `version` mirror the licensed file's fields and must be kept in sync at release time.
- `status` values for the watchlist tier: `no_license_found` | `expired` | `inactive` | `revoked` | `delinquent`.
- `status_note` is mandatory on every watchlist record — it carries the observation ("0 matches for name+address on date X"), which is the entire honesty of this tier.
- The `data` in the repo today is a placeholder (`records: []`); the envelope exists so the machinery is real and tested even while the watchlist is empty.

## 5. Error contract

All implementations surface the same three failure classes, so the UI can render the same message everywhere:

1. **bad envelope** — JSON parse failed, missing fields, wrong `v`, wrong `kdf`, or salt/iv not base64/expected length. Cause: corrupt file or incompatible format change.
2. **key derivation failure** — platform KDF call errored. Should never happen on a good envelope.
3. **wrong code** — GCM authentication failed (bad tag). The classic symptom: the passphrase is wrong. On Web Crypto this surfaces as the generic `OperationError` and must be re-labeled "wrong code" in the catch block; javax throws `AEADBadTagException`; CryptoKit throws `CryptoKitError.authenticationFailure`.

A successful decrypt returns the parsed document. A failed decrypt **never** returns partial plaintext — AES-GCM is all-or-nothing by design.

## 6. Implementation map

| Implementation | File | Notes |
|---|---|---|
| Encryptor (source of truth) | `admin_scripts/encrypt_unlicensed.js` | Node native `crypto` only. Writes `data/private/unlicensed.encrypted.json`. |
| Web app reader | `web/js/crypto.js` | Web Crypto, runs in the PWA page. |
| Extension reader | `extension/popup/popup.js` + shared logic | Web Crypto, runs in the popup/options context. |
| Android app | `android/.../CryptoHelper.kt` | javax.crypto; byte-identical result. |
| Android Auto | reads via the app's helper pattern | Auto is licensed-only today; the helper stays for the future tier. |
| Watch | `watch/.../CryptoHelper.kt` | Same javax implementation; watch is licensed-only today, helper kept and tested. |
| iOS | `ios/CryptoManager.swift` | CommonCrypto `CCKeyDerivation` for PBKDF2, CryptoKit `AES.GCM` for the cipher. |

## 7. Compatibility tests

The CI workflow (`.github/workflows/build.yml`) runs an envelope round-trip self-test: it derives a key with `pbkdf2Sync`, encrypts with `createCipheriv` + `setAuthTag` on the appended-tag layout, and verifies the exact byte layout this spec defines. Before any release that touches crypto, the annual workflow's **verify** step decrypts the shipped envelope with the correct code and asserts `AEADBadTagException` behavior with a wrong code.

If you add a new surface, the acceptance test is simple: it must decrypt an envelope produced by `admin_scripts/encrypt_unlicensed.js` using only its platform's first-party crypto, with zero dependencies.

## 8. Why not [library X]?

Because of constraint two: no third-party code on any surface. That constraint is the reason this spec exists in writing — normally a library would hide these details; here the spec *is* the library. The choices inside it (PBKDF2 over Argon2, 310k iterations, appended tag) are conservative picks that every first-party crypto stack already supports natively, which is exactly what a five-platform, no-dependency project needs.
