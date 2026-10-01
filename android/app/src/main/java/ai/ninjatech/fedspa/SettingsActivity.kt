package ai.ninjatech.fedspa

import android.content.Context
import android.content.SharedPreferences
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.CompoundButton
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONObject

/**
 * Settings screen.
 *
 * Two jobs:
 *   1. Remember-subscriber-code opt-in (SharedPreferences). When ON, the
 *      code is kept locally so the watchlist unlocks without retyping.
 *      When OFF, the stored value is wiped immediately.
 *   2. "About data" block: version, as-of date, counts, source link.
 *
 * No backend means no accounts, no auth, no telemetry - this is purely
 * local state, and the UI says so.
 */
class SettingsActivity : AppCompatActivity() {

    private lateinit var rememberToggle: CompoundButton
    private lateinit var codeField: android.widget.EditText
    private lateinit var dataBody: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_settings)

        rememberToggle = findViewById(R.id.rememberToggle)
        codeField = findViewById(R.id.codeField)
        dataBody = findViewById(R.id.dataBody)

        loadState()
        wire()
        renderDataInfo()
    }

    // ------------------------------------------------------------------
    // SharedPreferences contract (used by MainActivity too)
    // ------------------------------------------------------------------
    companion object {
        private const val PREFS = "fedspa_prefs"
        private const val KEY_REMEMBER = "remember_code"
        private const val KEY_CODE = "saved_code"

        fun prefs(context: Context): SharedPreferences =
            context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)

        fun shouldRemember(context: Context): Boolean =
            prefs(context).getBoolean(KEY_REMEMBER, false)

        fun savedCode(context: Context): String? =
            prefs(context).getString(KEY_CODE, null)

        fun saveCode(context: Context, code: String) {
            prefs(context).edit().putString(KEY_CODE, code).apply()
        }

        fun clearRememberedCode(context: Context) {
            prefs(context).edit()
                .remove(KEY_CODE)
                .remove(KEY_REMEMBER)
                .apply()
        }
    }

    // ------------------------------------------------------------------
    // UI
    // ------------------------------------------------------------------
    private fun loadState() {
        rememberToggle.isChecked = shouldRemember(this)
        savedCode(this)?.let { code ->
            codeField.hint = "Saved: ${"\u2022".repeat(minOf(24, code.length))}"
        }
    }

    private fun wire() {
        val saveBtn = findViewById<Button>(R.id.saveBtn)
        val clearBtn = findViewById<Button>(R.id.clearBtn)

        rememberToggle.setOnCheckedChangeListener { _, checked ->
            if (!checked) {
                clearRememberedCode(this)
                Toast.makeText(this, R.string.settings_wiped, Toast.LENGTH_SHORT).show()
            }
        }

        saveBtn.setOnClickListener {
            val remember = rememberToggle.isChecked
            val code = codeField.text.toString().trim()
            if (remember && code.isEmpty() && savedCode(this) == null) {
                Toast.makeText(this, R.string.settings_need_code, Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            prefs(this).edit()
                .putBoolean(KEY_REMEMBER, remember)
                .putString(KEY_CODE, if (remember) code else null)
                .apply()
            codeField.text.clear()
            Toast.makeText(this, R.string.settings_saved, Toast.LENGTH_SHORT).show()
        }

        clearBtn.setOnClickListener {
            clearRememberedCode(this)
            rememberToggle.isChecked = false
            codeField.hint = getString(R.string.settings_code_hint)
            codeField.text.clear()
            Toast.makeText(this, R.string.settings_wiped, Toast.LENGTH_SHORT).show()
        }
    }

    private fun renderDataInfo() {
        val doc: JSONObject = NetworkHelper.dataInfo(this) ?: run {
            dataBody.text = getString(R.string.settings_no_data)
            return
        }
        dataBody.text = buildString {
            appendLine(getString(R.string.settings_data_version, doc.optInt("version")))
            appendLine(getString(R.string.settings_data_as_of, doc.optString("as_of")))
            appendLine(getString(R.string.settings_data_count, doc.optJSONArray("parlors")?.length() ?: 0))
            appendLine(getString(R.string.settings_data_freq))
        }
    }
}
