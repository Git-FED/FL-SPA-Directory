package ai.ninjatech.fedspa

import android.util.Base64
import org.json.JSONObject
import javax.crypto.Cipher
import javax.crypto.SecretKeyFactory
import javax.crypto.spec.GCMParameterSpec
import javax.crypto.spec.PBEKeySpec
import javax.crypto.spec.SecretKeySpec

/**
 * AES-256-GCM subscriber-envelope decryptor.
 *
 * MUST stay byte-compatible with the other platform implementations:
 *   - admin_scripts/encrypt_unlicensed.js  (Node, encrypts)
 *   - web/js/crypto.js                     (Web Crypto)
 *   - extension/popup/popup.js             (Web Crypto, inline)
 *   - ios/CryptoManager.swift              (CommonCrypto / CryptoKit)
 *
 * Envelope format (all base64):
 *   {
 *     "v": 1,
 *     "kdf": "PBKDF2-SHA256",
 *     "iterations": 310000,
 *     "salt": "...",   16 bytes
 *     "iv":   "...",   12 bytes
 *     "data": "..."    ciphertext || 16-byte GCM tag (tag appended!)
 *   }
 *
 * javax.crypto's AES/GCM/NoPadding expects the tag appended to the
 * ciphertext, which is exactly the layout the Node encryptor writes.
 */
object CryptoHelper {

    private const val CIPHER = "AES/GCM/NoPadding"
    private const val KEY_BITS = 256
    private const val TAG_BITS = 128

    /**
     * Decrypt the envelope. Returns the plaintext bytes (UTF-8 JSON).
     * Throws GeneralSecurityException-family exceptions on wrong code
     * or tampered data - callers surface a friendly message.
     */
    fun decrypt(envelope: JSONObject, code: String): ByteArray {
        require(envelope.optInt("v", -1) == 1) { "Unsupported envelope version" }
        val kdf = envelope.optString("kdf")
        require(kdf == "PBKDF2-SHA256") { "Unsupported KDF: $kdf" }

        val iterations = envelope.optInt("iterations")
        val salt = b64(envelope.optString("salt"))
        val iv = b64(envelope.optString("iv"))
        val data = b64(envelope.optString("data"))

        require(salt.size == 16) { "Bad salt length" }
        require(iv.size == 12) { "Bad IV length" }

        // ---- PBKDF2-SHA256 -> 256-bit key ----
        val factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256")
        val spec = PBEKeySpec(code.toCharArray(), salt, iterations, KEY_BITS)
        val keyBytes = factory.generateSecret(spec).encoded
        val key = SecretKeySpec(keyBytes, "AES")

        // ---- AES-256-GCM decrypt (tag is the tail of `data`) ----
        val cipher = Cipher.getInstance(CIPHER)
        cipher.init(Cipher.DECRYPT_MODE, key, GCMParameterSpec(TAG_BITS, iv))
        return cipher.doFinal(data)
    }

    /** Convenience: decrypt + hand back the parsed JSON document. */
    fun decryptJson(envelope: JSONObject, code: String): JSONObject =
        JSONObject(String(decrypt(envelope, code), Charsets.UTF_8))

    private fun b64(s: String): ByteArray =
        Base64.decode(s, Base64.DEFAULT)
}
