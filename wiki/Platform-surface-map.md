# Platform surface map

Which capability exists on which surface. "✅" shipped, "—" deliberately
not shipped (with the reason — these are product decisions, not TODOs).

| Capability | Web PWA | Extension | Android | Auto | Watch | iOS |
|---|---|---|---|---|---|---|
| Licensed list + search | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Status filter | ✅ | ✅ | ✅ | — | — | ✅ |
| Detail view | ✅ modal | ✅ | ✅ dialog | — | — | ✅ |
| Expiring-soon chip (≤180d) | ✅ | ✅ | — | — | — | — |
| Subscriber tier decrypt | ✅ | ✅ | ✅ | — | — | ✅ |
| Remember code opt-in | — sessionStorage | ✅ storage | ✅ prefs | — | — | ✅ defaults |
| Offline operation | ✅ SW | ✅ bundled | ✅ bundled | ✅ bundled | ✅ bundled | ✅ bundled |
| Deep links | — | — | ✅ fedspa:// | — | — | — |
| Voice search | — | — | — | ✅ | — (query handoff) | — |
| MQA portal page enhancer | — | ✅ content script | — | — | — | — |
| Home-screen widget | ✅ installable | ✅ toolbar badge | ✅ widget | — | — | — |
| Install / store | ✅ PWA | ✅ Chrome Web Store | ✅ APK | ✅ via phone app | ✅ via phone app | ✅ App Store |

## The deliberate "—" decisions

- **Auto has no subscriber tier**: entering a code while driving is
  hostile UX and watching unlicensed parlors at 70mph is not the use
  case. Data minimization behind the wheel.
- **Watch has no subscriber tier**: same reasoning, smaller screen.
- **Watch/Auto have no status filter or detail view**: glanceable
  verification only — name, city, status color.
- **Web keeps the code in sessionStorage only** (cleared on browser
  close): the web surface is the one most likely used on shared
  machines; it errs toward forgetting.
- **Extension options carry a remember opt-in**: extensions live on
  personal machines, and the MQA content script needs the stored code
  to annotate the portal page automatically.

## Where the code lives

| Surface | Location |
|---|---|
| Web | `web/` (vanilla JS, IIFE namespaces FedSpaUI/Search/Crypto) |
| Extension | `extension/` (Manifest V3, service worker background) |
| Android | `android/` (Kotlin, classic views, javax.crypto) |
| Android Auto | `android_auto/` (Kotlin, giant-target car UI) |
| Watch | `watch/` (Kotlin, Wear-sized UI) |
| iOS | `ios/` (SwiftUI, CryptoKit + CommonCrypto) |

All six read the same fan-out copies produced by
`admin_scripts/generate_public_files.py` from the single source of truth
in `data/`.
