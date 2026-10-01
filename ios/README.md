# FED-SPA iOS

SwiftUI app listing licensed massage establishments in Florida, plus the
subscriber-only unlicensed watchlist.

## Zero dependencies

No Swift Package Manager dependencies, no CocoaPods, no third-party code.
Everything is Apple frameworks: SwiftUI, Foundation, CryptoKit, CommonCrypto.

## Build

1. Open this `ios/` folder in Xcode → **File > New > Project > iOS App**
2. Product name `FedSpa`, bundle id `ai.ninjatech.fedspa`
3. Add the five sources, `Assets.xcassets`, and both files in
   `Resources/Data/` as target resources
4. Build (⌘B). That's it — the data ships inside the bundle.

`FedSpa.xcodeproj/project.json` documents the exact target layout; the
`.pbxproj` itself is machine-generated on first open.

## Data

| File | Tier | Filled by |
|------|------|-----------|
| `Resources/Data/licensed.json` | Public, plaintext | `admin_scripts/generate_public_files.py` |
| `Resources/Data/unlicensed.encrypted.json` | Subscriber, encrypted | `admin_scripts/generate_public_files.py` |

Refresh both once a year via the root `admin_scripts/merge_and_encrypt.sh`.

## Crypto envelope (must match every platform)

`PBKDF2-SHA256 (310,000 iterations, 16-byte salt) → AES-256-GCM
(12-byte IV, 16-byte tag appended to ciphertext)`, all fields base64 in
`{v, kdf, iterations, salt, iv, data}`. See `CryptoManager.swift`.

## Remember-code trade-off

The opt-in "remember my code" stores the code in `UserDefaults` —
local-only, unencrypted on device, exactly like `chrome.storage.local`
(extension) and `SharedPreferences` (Android). The settings UI says so
in plain language.
