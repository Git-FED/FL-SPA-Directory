package ai.ninjatech.fedspa.watch

import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.LayoutInflater
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONArray
import org.json.JSONObject
import java.util.Locale

/**
 * FED-SPA on the wrist.
 *
 * Design rules for a 1.4-1.8" round screen:
 *   - one search field, one list, nothing else
 *   - big status colors (glanceable: green/red at arm's length)
 *   - no subscriber tier - entering a code on a watch is hostile UX
 *
 * Data: assets/licensed.json, bundled at build time by
 * generate_public_files.py. No network.
 */
class WatchActivity : AppCompatActivity() {

    private lateinit var searchInput: EditText
    private lateinit var listContainer: LinearLayout
    private lateinit var countView: TextView

    private var parlors: List<Row> = emptyList()

    data class Row(
        val license: String,
        val name: String,
        val city: String,
        val status: String
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_watch)

        searchInput = findViewById(R.id.watchSearch)
        listContainer = findViewById(R.id.watchList)
        countView = findViewById(R.id.watchCount)

        load()
        render()

        searchInput.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, a: Int, b: Int, c: Int) {}
            override fun onTextChanged(s: CharSequence?, a: Int, b: Int, c: Int) {}
            override fun afterTextChanged(s: Editable?) { render() }
        })

        // companion handoff: pre-filled query from the phone
        intent.getStringExtra("voice_query")?.let {
            searchInput.setText(it)
        }
    }

    // ------------------------------------------------------------------
    // bundled data
    // ------------------------------------------------------------------
    private fun load() {
        parlors = try {
            val text = assets.open("licensed.json").bufferedReader().readText()
            parse(JSONObject(text))
        } catch (e: Exception) {
            emptyList()
        }
    }

    private fun parse(doc: JSONObject): List<Row> {
        val out = mutableListOf<Row>()
        val arr: JSONArray = doc.optJSONArray("parlors") ?: return out
        for (i in 0 until arr.length()) {
            val o = arr.optJSONObject(i) ?: continue
            out.add(
                Row(
                    license = o.optString("license_number"),
                    name = o.optString("business_name"),
                    city = o.optJSONObject("address")?.optString("city") ?: "",
                    status = o.optString("status")
                )
            )
        }
        return out
    }

    // ------------------------------------------------------------------
    // render
    // ------------------------------------------------------------------
    private fun render() {
        val q = searchInput.text.toString().trim().lowercase(Locale.US)
        val rows = parlors.filter { r ->
            q.isEmpty() || listOf(r.name, r.license, r.city)
                .joinToString(" ").lowercase(Locale.US).contains(q)
        }

        countView.text = "${rows.size}"
        listContainer.removeAllViews()
        val inflater = LayoutInflater.from(this)

        for (r in rows) {
            val row = inflater.inflate(R.layout.watch_row, listContainer, false)
            row.findViewById<TextView>(R.id.watchRowName).text = r.name
            row.findViewById<TextView>(R.id.watchRowStatus).text =
                r.status.replaceFirstChar { it.uppercase(Locale.US) }
            row.findViewById<TextView>(R.id.watchRowStatus).setTextColor(statusColor(r.status))
            listContainer.addView(row)
        }
    }

    companion object {
        fun statusColor(status: String): Int = when (status.lowercase(Locale.US)) {
            "clear", "active" -> 0xFF2DD4A7.toInt()
            "delinquent", "probation" -> 0xFFF2C14E.toInt()
            "expired", "revoked" -> 0xFFFF5F6D.toInt()
            else -> 0xFF9AA4B5.toInt()
        }
    }
}
