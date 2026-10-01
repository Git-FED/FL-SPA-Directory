package ai.ninjatech.fedspa

import android.content.Context
import android.util.Base64
import org.json.JSONObject
import java.io.InputStream

/**
 * Bundled-asset loader. No network, no Retrofit, no OkHttp - the app never
 * holds the INTERNET permission, so "NetworkHelper" is deliberately a
 * misnomer kept for symmetry with the platform skeleton: it exists to make
 * the no-network architecture explicit and greppable.
 *
 * generate_public_files.py drops into app/src/main/assets/:
 *   licensed.json              (public tier)
 *   unlicensed.encrypted.json  (subscriber tier envelope)
 */
object NetworkHelper {

    private const val LICENSED = "licensed.json"
    private const val ENCRYPTED = "unlicensed.encrypted.json"

    /** Load the public licensed dataset. Returns null if the asset is missing/corrupt. */
    fun loadLicensed(context: Context): JSONObject? =
        readAsset(context, LICENSED)?.let { runCatching { JSONObject(it) }.getOrNull() }

    /** Load the subscriber envelope. Returns null when no watchlist is packaged. */
    fun loadEnvelope(context: Context): JSONObject? =
        readAsset(context, ENCRYPTED)?.let { runCatching { JSONObject(it) }.getOrNull() }

    /** License count for the widget / launcher badge. */
    fun licensedCount(context: Context): Int =
        loadLicensed(context)?.optJSONArray("parlors")?.length() ?: 0

    /** Data version metadata for SettingsActivity's "About data" block. */
    fun dataInfo(context: Context): JSONObject? = loadLicensed(context)

    private fun readAsset(context: Context, name: String): String? = try {
        context.assets.open(name).use { stream: InputStream ->
            stream.bufferedReader().use { it.readText() }
        }
    } catch (e: Exception) {
        null
    }

    /** base64 helper shared by CryptoHelper (kept here for the widget path). */
    fun b64(s: String): ByteArray = Base64.decode(s, Base64.DEFAULT)
}
