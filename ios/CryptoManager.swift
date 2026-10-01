import Foundation
import CryptoKit
import CommonCrypto

/**
 * FED-SPA subscriber-envelope decryptor (iOS).
 *
 * Byte-compatible with every other platform:
 *   - admin_scripts/encrypt_unlicensed.js  (Node, encrypts)
 *   - web/js/crypto.js                     (Web Crypto)
 *   - extension/popup/popup.js             (Web Crypto inline)
 *   - android CryptoHelper.kt              (javax.crypto)
 *
 * Envelope:
 *   { v:1, kdf:"PBKDF2-SHA256", iterations:310000,
 *     salt, iv, data }  all base64; data = ciphertext || 16-byte tag.
 *
 * PBKDF2 comes from CommonCrypto (CryptoKit has no PBKDF2 yet);
 * AES-GCM comes from CryptoKit (seal/open with the appended tag).
 */
enum CryptoManager {

    static let keyBits = 256
    static let tagLength = 16

    enum CryptoError: Error {
        case badEnvelope
        case wrongCode
        case keyDerivationFailed
    }

    /// Decrypt the subscriber envelope -> raw JSON data.
    static func decrypt(envelope: [String: Any], code: String) throws -> Data {
        guard let v = envelope["v"] as? Int, v == 1,
              let kdf = envelope["kdf"] as? String, kdf == "PBKDF2-SHA256",
              let iterations = envelope["iterations"] as? Int, iterations > 0,
              let saltB64 = envelope["salt"] as? String,
              let ivB64 = envelope["iv"] as? String,
              let dataB64 = envelope["data"] as? String
        else { throw CryptoError.badEnvelope }

        guard let salt = Data(base64Encoded: saltB64), salt.count == 16,
              let iv = Data(base64Encoded: ivB64), iv.count == 12,
              let payload = Data(base64Encoded: dataB64), payload.count > tagLength
        else { throw CryptoError.badEnvelope }

        // ---- PBKDF2-SHA256 -> 32-byte key (CommonCrypto) ----
        let keyData = try pbkdf2(password: code, salt: salt, iterations: iterations, keyLength: keyBits / 8)

        // ---- AES-256-GCM open (CryptoKit, tag = last 16 bytes) ----
        let key = SymmetricKey(data: keyData)
        let nonce = try AES.GCM.Nonce(data: iv)
        let ciphertext = payload.prefix(payload.count - tagLength)
        let tag = payload.suffix(tagLength)

        do {
            let box = try AES.GCM.SealedBox(nonce: nonce, ciphertext: ciphertext, tag: tag)
            return try AES.GCM.open(box, using: key)
        } catch {
            throw CryptoError.wrongCode
        }
    }

    /// Convenience: decrypt + decode the watchlist document.
    static func decryptDocument(envelope: [String: Any], code: String) throws -> UnlicensedDocument {
        let raw = try decrypt(envelope: envelope, code: code)
        return try JSONDecoder().decode(UnlicensedDocument.self, from: raw)
    }

    /// PBKDF2-SHA256 via CommonCrypto.
    private static func pbkdf2(password: String, salt: Data, iterations: Int, keyLength: Int) throws -> Data {
        var derived = Data(repeating: 0, count: keyLength)
        let passwordArray = Array(password.utf8)
        let result = derived.withUnsafeMutableBytes { derivedPtr in
            salt.withUnsafeBytes { saltPtr in
                CCKeyDerivation(
                    CCPBKDFAlgorithm(kCCPBKDF2),
                    password, passwordArray.count,
                    saltPtr.bindMemory(to: UInt8.self).baseAddress, salt.count,
                    CCPseudoRandomAlgorithm(kCCPRFHmacAlgSHA256),
                    UInt32(iterations),
                    derivedPtr.bindMemory(to: UInt8.self).baseAddress, keyLength
                )
            }
        }
        guard result == kCCSuccess else { throw CryptoError.keyDerivationFailed }
        return derived
    }
}
