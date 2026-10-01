package ai.ninjatech.fedspa.auto

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
 * FED-SPA on the car screen (and tablet-sized dashboard displays).
 *
 * Car UI rules baked into this screen:
 *   - huge touch targets (min 64dp rows)
 *   - high contrast, no subtle grays
 *   - minimal chrome: one search field, one list, that's it
 *
 * The subscriber tier is intentionally NOT available here - data
 * minimization while driving. assets/licensed.json only.
 */
class CarActivity : AppCompatActivity() {

    private lateinit var searchInput: EditText
    private lateinit var listContainer: LinearLayout
    private lateinit var emptyView: TextView
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
        setContentView(R.layout.activity_car)

        searchInput = findViewById(R.id.carSearch)
        listContainer = findViewById(R.id.carList)
        emptyView = findViewById(R.id.carEmpty)
        countView = findViewById(R.id.carCount)

        load()
        render()

        searchInput.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, a: Int, b: Int, c: Int) {}
            override fun onTextChanged(s: CharSequence?, a: Int, b: Int, c: Int) {}
            override fun afterTextChanged(s: Editable?) { render() }
        })
    }

    // ------------------------------------------------------------------
    // bundled data (licensed only)
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

        countView.text = "${rows.size} licensed"
        listContainer.removeAllViews()
        val inflater = LayoutInflater.from(this)

        if (rows.isEmpty()) {
            emptyView.visibility = android.view.View.VISIBLE
            listContainer.visibility = android.view.View.GONE
        } else {
            emptyView.visibility = android.view.View.GONE
            listContainer.visibility = android.view.View.VISIBLE
            for (r in rows) {
                val row = inflater.inflate(R.layout.car_row, listContainer, false)
                row.findViewById<TextView>(R.id.rowName).text = r.name
                row.findViewById<TextView>(R.id.rowMeta).text = "${r.license} · ${r.city}"
                row.findViewById<TextView>(R.id.rowStatus).text =
                    r.status.replaceFirstChar { it.uppercase(Locale.US) }
                listContainer.addView(row)
            }
        }
    }
}
