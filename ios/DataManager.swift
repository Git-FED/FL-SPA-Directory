import Foundation
import SwiftUI

/**
 * Loads the bundled datasets and owns app state.
 *
 * Sources (both filled by admin_scripts/generate_public_files.py):
 *   Resources/Data/licensed.json              - public tier
 *   Resources/Data/unlicensed.encrypted.json  - subscriber envelope
 *
 * The remembered code lives in UserDefaults (standard) - same trade-off
 * as chrome.storage.local / SharedPreferences on other platforms:
 * local-only, unencrypted on device, user opt-in, clearly labeled.
 */
@MainActor
final class DataManager: ObservableObject {

    // published state
    @Published var licensed: [LicensedParlor] = []
    @Published var unlicensed: [UnlicensedParlor] = []
    @Published var unlocked = false
    @Published var unlockError: String?
    @Published var asOf: String = ""
    @Published var version: Int = 0
    @Published var rememberCode = UserDefaults.standard.bool(forKey: "fedspa.rememberCode")

    private var envelope: [String: Any]?
    private(set) var rememberKey = "fedspa.rememberCode"
    private(set) var savedCodeKey = "fedspa.savedCode"

    // ------------------------------------------------------------------
    // boot
    // ------------------------------------------------------------------
    init() {
        loadLicensed()
        loadEnvelope()
        tryAutoUnlock()
    }

    private func loadLicensed() {
        guard let url = Bundle.main.url(forResource: "licensed", withExtension: "json"),
              let raw = try? Data(contentsOf: url),
              let doc = try? JSONDecoder().decode(LicensedDocument.self, from: raw)
        else { return }
        licensed = doc.parlors
        asOf = doc.asOf
        version = doc.version
    }

    private func loadEnvelope() {
        guard let url = Bundle.main.url(forResource: "unlicensed.encrypted", withExtension: "json"),
              let raw = try? Data(contentsOf: url),
              let obj = try? JSONSerialization.jsonObject(with: raw) as? [String: Any]
        else { return }
        // Skip the empty placeholder envelope (data == "").
        if let dataField = obj["data"] as? String, dataField.isEmpty { return }
        envelope = obj
    }

    // ------------------------------------------------------------------
    // unlock flow
    // ------------------------------------------------------------------
    private func tryAutoUnlock() {
        guard rememberCode,
              let saved = UserDefaults.standard.string(forKey: savedCodeKey),
              let env = envelope else { return }
        do {
            let doc = try CryptoManager.decryptDocument(envelope: env, code: saved)
            unlicensed = doc.parlors
            unlocked = true
        } catch {
            // stale/incorrect stored code: wipe and ignore silently
            UserDefaults.standard.removeObject(forKey: savedCodeKey)
        }
    }

    func unlock(code: String) {
        guard let env = envelope else {
            unlockError = "No watchlist file is bundled with this build."
            return
        }
        do {
            let doc = try CryptoManager.decryptDocument(envelope: env, code: code)
            unlicensed = doc.parlors
            unlocked = true
            unlockError = nil
            if rememberCode {
                UserDefaults.standard.set(code, forKey: savedCodeKey)
            }
        } catch {
            unlockError = "That code didn't decrypt the watchlist."
        }
    }

    func lock() {
        unlocked = false
        unlicensed = []
        UserDefaults.standard.removeObject(forKey: savedCodeKey)
        UserDefaults.standard.set(false, forKey: rememberKey)
        rememberCode = false
    }

    func setRemember(_ on: Bool) {
        rememberCode = on
        UserDefaults.standard.set(on, forKey: rememberKey)
        if !on {
            UserDefaults.standard.removeObject(forKey: savedCodeKey)
        }
    }

    // ------------------------------------------------------------------
    // search
    // ------------------------------------------------------------------
    /// All search terms must match somewhere in name/license/city/county/street/notes.
    func searchLicensed(_ query: String, status: String? = nil) -> [LicensedParlor] {
        let terms = query.lowercased()
            .split(whereSeparator: { $0.isWhitespace })
            .map(String.init)
        return licensed.filter { p in
            if let status, status != p.status { return false }
            guard !terms.isEmpty else { return true }
            let haystack = [
                p.businessName, p.licenseNumber, p.address.city, p.county,
                p.address.street, p.notes ?? ""
            ].joined(separator: " ").lowercased()
            return terms.allSatisfy { haystack.contains($0) }
        }
    }

    func searchUnlicensed(_ query: String, status: String? = nil) -> [UnlicensedParlor] {
        let terms = query.lowercased()
            .split(whereSeparator: { $0.isWhitespace })
            .map(String.init)
        return unlicensed.filter { p in
            if let status, status != p.status { return false }
            guard !terms.isEmpty else { return true }
            let haystack = [
                p.businessName, p.address.city, p.county,
                p.address.street, p.reason
            ].joined(separator: " ").lowercased()
            return terms.allSatisfy { haystack.contains($0) }
        }
    }

    /// Status color used by badges on every platform.
    static func statusColor(_ status: String) -> Color {
        switch status.lowercased() {
        case "clear", "active":
            return Color(red: 0x2D / 255, green: 0xD4 / 255, blue: 0xA7 / 255)
        case "delinquent", "probation":
            return Color(red: 0xF2 / 255, green: 0xC1 / 255, blue: 0x4E / 255)
        case "expired", "revoked", "no_license_found":
            return Color(red: 0xFF / 255, green: 0x5F / 255, blue: 0x6D / 255)
        default:
            return Color(red: 0x9A / 255, green: 0xA4 / 255, blue: 0xB5 / 255)
        }
    }
}
