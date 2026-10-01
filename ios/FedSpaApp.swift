import SwiftUI

/**
 * FED-SPA iOS entry point.
 *
 * Architecture mirrors every other surface:
 *   - bundled licensed.json (public tier)
 *   - bundled unlicensed.encrypted.json (subscriber tier)
 *   - AES-256-GCM unlock via CryptoManager (CommonCrypto under SwiftUI)
 *   - no network, no accounts, no telemetry
 *
 * The app ships as a single target; Resources/Data is filled by
 * admin_scripts/generate_public_files.py.
 */
@main
struct FedSpaApp: App {
    @StateObject private var data = DataManager()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(data)
                .preferredColorScheme(.dark) // brand default, matches web
        }
    }
}
