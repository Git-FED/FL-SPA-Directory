package ai.ninjatech.fedspa.watch

import android.content.Context
import org.json.JSONObject
import java.io.InputStream

/**
 * AES-256-GCM envelope helper for the watch.
 *
 * NOTE: the subscriber tier is not packaged on the watch (see
 * WatchActivity docs), so this helper is a thin stub kept for
 * symmetry + future use. If a future build ships the envelope to the
 * wrist, this is the byte-compatible implementation (PBKDF2-SHA256
 * 310k -> AES-256-GCM, tag appended - same as CryptoHelper.kt in the
 * phone app).
 */
object CryptoHelper {

    private const val KEY_BITS = 256
    private const val TAG_BITS = 128

    /** True when a subscriber envelope is bundled in this build. */
    fun hasEnvelope(context: Context): Boolean = try {
        context.assets.open("unlicensed.encrypted.json").use { it.read() > 0 }
    } catch (e: Exception) {
        false
    }

    /**
     * Decrypt helper, byte-compatible with every other platform.
     * Currently unused on the wrist by design; wired for the future.
     */
    fun decrypt(envelope: JSONObject, code: String): ByteArray {
        require(envelope.optInt("v", -1) == 1) { "Unsupported envelope version" }
        val salt = android.util.Base64.decode(envelope.optString("salt"), android.util.Base64.DEFAULT)
        val iv = android.util.Base64.decode(envelope.optString("iv"), android.util.Base64.DEFAULT)
        val data = android.util.Base64.decode(envelope.optString("data"), android.util.Base64.DEFAULT)

        val factory = javax.crypto.SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256")
        val spec = javax.crypto.spec.PBEKeySpec(code.toCharArray(), salt, envelope.optInt("iterations"), KEY_BITS)
        val key = javax.crypto.spec.SecretKeySpec(factory.generateSecret(spec).encoded, "AES")

        val cipher = javax.crypto.Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(javax.crypto.Cipher.DECRYPT_MODE, key, javax.crypto.spec.GCMParameterSpec(TAG_BITS, iv))
        return cipher.doFinal(data)
    }

    private fun InputStream.read(): Int {
        var total = 0
        val buf = ByteArray(4096)
        while (true) {
            val n = read(buf)
            if (n < 0) break
            total += n
        }
        close()
        return total
    }
}
