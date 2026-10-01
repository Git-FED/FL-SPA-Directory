package ai.ninjatech.fedspa

import android.annotation.SuppressLint
import android.content.Intent
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.LayoutInflater
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.Spinner
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONObject
import java.io.InputStream
import java.util.Locale

/**
 * FED-SPA Android - main screen.
 *
 * Bundled-assets architecture (no network, no INTERNET permission):
 *   assets/licensed.json              - public tier, shipped in every build
 *   assets/unlicensed.encrypted.json  - subscriber tier, AES-256-GCM envelope
 *
 * The unlock flow mirrors web/js/crypto.js byte-for-byte:
 *   PBKDF2-SHA256, 310,000 iterations -> AES-256-GCM key.
 *   envelope { v, kdf, iterations, salt, iv, data } - all base64 fields.
 *   In the Node encryptor the 16-byte GCM tag is APPENDED to the
 *   ciphertext - javax.crypto expects exactly that layout, which is why
 *   this app, the web app, the extension and iOS all interoperate.
 */
class MainActivity : AppCompatActivity() {

    // views
    private lateinit var searchInput: EditText
    private lateinit var statusFilter: Spinner
    private lateinit var listContainer: LinearLayout
    private lateinit var emptyView: TextView
    private lateinit var dataAsOfView: TextView
    private lateinit var dataCountView: TextView
    private lateinit var unlockRow: LinearLayout
    private lateinit var codeInput: EditText
    private lateinit var unlockBtn: Button
    private lateinit var lockBtn: Button
    private lateinit var tabLicensed: TextView
    private lateinit var tabUnlicensed: TextView
    private lateinit var subscriberNotice: TextView

    // state
    private var licensed: List<Parlor> = emptyList()
    private var unlicensed: List<Parlor> = emptyList()
    private var envelope: JSONObject? = null
    private var unlocked = false
    private var showUnlicensed = false
    private var asOf: String = ""

    // ------------------------------------------------------------------
    // lifecycle
    // ------------------------------------------------------------------
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        wireViews()
        loadData()
        render()

        // fedspa://parlor/MM41109 -> jump straight to that record
        handleDeepLink(intent)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        handleDeepLink(intent)
    }

    private fun handleDeepLink(intent: Intent?) {
        val data = intent?.data ?: return
        if (data.scheme != "fedspa" || data.host != "parlor") return
        val license = data.lastPathSegment ?: return
        licensed.firstOrNull { it.licenseNumber.equals(license, ignoreCase = true) }
            ?.let { openDetail(it) }
    }

    // ------------------------------------------------------------------
    // view wiring
    // ------------------------------------------------------------------
    @SuppressLint("SetTextI18n")
    private fun wireViews() {
        searchInput = findViewById(R.id.searchInput)
        statusFilter = findViewById(R.id.statusFilter)
        listContainer = findViewById(R.id.listContainer)
        emptyView = findViewById(R.id.emptyView)
        dataAsOfView = findViewById(R.id.dataAsOf)
        dataCountView = findViewById(R.id.dataCount)
        unlockRow = findViewById(R.id.unlockRow)
        codeInput = findViewById(R.id.codeInput)
        unlockBtn = findViewById(R.id.unlockBtn)
        lockBtn = findViewById(R.id.lockBtn)
        tabLicensed = findViewById(R.id.tabLicensed)
        tabUnlicensed = findViewById(R.id.tabUnlicensed)
        subscriberNotice = findViewById(R.id.subscriberNotice)

        ArrayAdapter.createFromResource(
            this, R.array.status_filter_options, android.R.layout.simple_spinner_item
        ).also { adapter ->
            adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
            statusFilter.adapter = adapter
        }

        searchInput.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, a: Int, b: Int, c: Int) {}
            override fun onTextChanged(s: CharSequence?, a: Int, b: Int, c: Int) {}
            override fun afterTextChanged(s: Editable?) { render() }
        })

        statusFilter.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(p: AdapterView<*>?, v: View?, pos: Int, id: Long) { render() }
            override fun onNothingSelected(p: AdapterView<*>?) {}
        }

        tabLicensed.setOnClickListener {
            showUnlicensed = false; renderTabs(); render()
        }
        tabUnlicensed.setOnClickListener {
            if (unlocked) { showUnlicensed = true; renderTabs(); render() }
            else { subscriberNotice.text = getString(R.string.subscriber_locked_hint) }
        }

        unlockBtn.setOnClickListener { unlock() }
        lockBtn.setOnClickListener { lock() }

        findViewById<View>(R.id.settingsBtn).setOnClickListener {
            startActivity(Intent(this, SettingsActivity::class.java))
        }
    }

    // ------------------------------------------------------------------
    // data loading (bundled assets, zero network)
    // ------------------------------------------------------------------
    private fun loadData() {
        licensed = readJsonAsset("licensed.json")?.let(::parseLicensed) ?: emptyList()
        envelope = try {
            readJsonAsset("unlicensed.encrypted.json")
        } catch (e: Exception) {
            null
        }
        asOf = readJsonAsset("licensed.json")?.optString("as_of", "") ?: ""
    }

    private fun readJsonAsset(name: String): JSONObject? = try {
        assets.open(name).use { stream: InputStream ->
            JSONObject(stream.bufferedReader().readText())
        }
    } catch (e: Exception) {
        null
    }

    private fun parseLicensed(doc: JSONObject): List<Parlor> {
        val out = mutableListOf<Parlor>()
        val arr = doc.optJSONArray("parlors") ?: return out
        for (i in 0 until arr.length()) {
            val o = arr.optJSONObject(i) ?: continue
            val addr = o.optJSONObject("address") ?: JSONObject()
            out.add(
                Parlor(
                    licenseNumber = o.optString("license_number", ""),
                    businessName = o.optString("business_name", ""),
                    profession = o.optString("profession", ""),
                    status = o.optString("status", ""),
                    expirationDate = o.optString("expiration_date", ""),
                    originalIssueDate = o.optString("original_issue_date", ""),
                    street = addr.optString("street", ""),
                    city = addr.optString("city", ""),
                    state = addr.optString("state", "FL"),
                    zip = addr.optString("zip", ""),
                    county = o.optString("county", ""),
                    disciplineOnFile = o.optBoolean("discipline_on_file", false),
                    publicComplaint = o.optBoolean("public_complaint", false),
                    dataAsOf = o.optString("data_as_of", ""),
                    lastChecked = o.optString("last_checked", ""),
                    notes = if (o.isNull("notes")) null else o.optString("notes", null)
                )
            )
        }
        return out
    }

    private fun parseUnlicensed(doc: JSONObject): List<Parlor> {
        val out = mutableListOf<Parlor>()
        val arr = doc.optJSONArray("parlors") ?: return out
        for (i in 0 until arr.length()) {
            val o = arr.optJSONObject(i) ?: continue
            val addr = o.optJSONObject("address") ?: JSONObject()
            out.add(
                Parlor(
                    licenseNumber = "—",
                    businessName = o.optString("business_name", ""),
                    profession = "",
                    status = o.optString("status", ""),
                    expirationDate = "",
                    originalIssueDate = "",
                    street = addr.optString("street", ""),
                    city = addr.optString("city", ""),
                    state = addr.optString("state", "FL"),
                    zip = addr.optString("zip", ""),
                    county = o.optString("county", ""),
                    disciplineOnFile = false,
                    publicComplaint = false,
                    dataAsOf = "",
                    lastChecked = o.optString("last_checked", ""),
                    notes = o.optString("reason", "")
                )
            )
        }
        return out
    }

    // ------------------------------------------------------------------
    // subscriber unlock (AES-256-GCM, identical envelope to web/extension)
    // ------------------------------------------------------------------
    private fun unlock() {
        val pw = codeInput.text.toString()
        if (pw.isEmpty()) {
            subscriberNotice.text = getString(R.string.unlock_empty)
            return
        }
        val env = envelope
        if (env == null || env.optString("data").isEmpty()) {
            subscriberNotice.text = getString(R.string.no_envelope)
            return
        }
        try {
            val plain = CryptoHelper.decrypt(env, pw)
            unlicensed = parseUnlicensed(JSONObject(String(plain, Charsets.UTF_8)))
            unlocked = true
            codeInput.text.clear()
            saveRememberedCode(pw)
            renderTabs(); render()
        } catch (e: Exception) {
            subscriberNotice.text = getString(R.string.unlock_failed)
        }
    }

    private fun lock() {
        unlocked = false
        showUnlicensed = false
        unlicensed = emptyList()
        SettingsActivity.clearRememberedCode(this)
        renderTabs(); render()
    }

    @SuppressLint("ApplySharedPref")
    private fun saveRememberedCode(pw: String) {
        if (SettingsActivity.shouldRemember(this)) {
            SettingsActivity.saveCode(this, pw)
        }
    }

    // ------------------------------------------------------------------
    // rendering
    // ------------------------------------------------------------------
    private fun renderTabs() {
        val active = 0xFF2DD4A7.toInt()
        val inactive = 0xFF9AA4B5.toInt()
        tabLicensed.setBackgroundColor(if (showUnlicensed) 0x00000000 else active)
        tabLicensed.setTextColor(if (showUnlicensed) inactive else 0xFF06251B.toInt())
        tabUnlicensed.setBackgroundColor(if (showUnlicensed) active else 0x00000000)
        tabUnlicensed.setTextColor(if (showUnlicensed) 0xFF06251B.toInt() else inactive)
        tabUnlicensed.isEnabled = true
    }

    @SuppressLint("SetTextI18n")
    private fun render() {
        val query = searchInput.text.toString().trim().lowercase(Locale.US)
        val statusSel = statusFilter.selectedItemPosition
        val source = if (showUnlicensed && unlocked) unlicensed else licensed

        dataAsOfView.text = if (asOf.isNotEmpty()) "Data as of $asOf" else ""
        dataCountView.text = "${source.size} establishments"

        val filtered = source.filter { p ->
            (statusSel == 0 || statusLabel(statusSel) == p.status) &&
            (query.isEmpty() || matches(p, query))
        }

        listContainer.removeAllViews()
        val inflater = LayoutInflater.from(this)

        if (filtered.isEmpty()) {
            emptyView.visibility = View.VISIBLE
            listContainer.visibility = View.GONE
        } else {
            emptyView.visibility = View.GONE
            listContainer.visibility = View.VISIBLE
            for (p in filtered) {
                val card = inflater.inflate(R.layout.parlor_card, listContainer, false)
                card.findViewById<TextView>(R.id.cardName).text = p.businessName
                card.findViewById<TextView>(R.id.cardLicense).text =
                    if (p.licenseNumber == "—") "Unlicensed" else "License ${p.licenseNumber}"
                card.findViewById<TextView>(R.id.cardCity).text = "${p.city}, ${p.state}"
                val badge = card.findViewById<TextView>(R.id.cardStatus)
                badge.text = p.status.replaceFirstChar { it.uppercase(Locale.US) }
                badge.setBackgroundColor(statusColor(p.status))
                card.setOnClickListener { openDetail(p) }
                listContainer.addView(card)
            }
        }

        unlockRow.visibility = if (unlocked) View.GONE else View.VISIBLE
        lockBtn.visibility = if (unlocked) View.VISIBLE else View.GONE
        subscriberNotice.text = ""
    }

    private fun statusLabel(pos: Int): String = when (pos) {
        1 -> "Clear"; 2 -> "Active"; 3 -> "Delinquent"; 4 -> "Expired"
        5 -> "Inactive"; 6 -> "Probation"; else -> "All statuses"
    }

    private fun statusColor(status: String): Int = when (status.lowercase(Locale.US)) {
        "clear", "active" -> 0xFF2DD4A7.toInt()      // teal
        "delinquent" -> 0xFFF2C14E.toInt()           // amber
        "inactive" -> 0xFF6B7687.toInt()             // slate
        "expired", "revoked", "no_license_found" -> 0xFFFF5F6D.toInt()  // red
        "probation" -> 0xFFF2C14E.toInt()
        else -> 0xFF6B7687.toInt()
    }

    private fun matches(p: Parlor, query: String): Boolean {
        val terms = query.split(Regex("\\s+")).filter { it.isNotEmpty() }
        val haystack = listOf(
            p.businessName, p.licenseNumber, p.city, p.county, p.street, p.notes ?: ""
        ).joinToString(" ").lowercase(Locale.US)
        return terms.all { haystack.contains(it) }
    }

    @SuppressLint("SetTextI18n")
    private fun openDetail(p: Parlor) {
        val sheet = android.app.Dialog(this)
        sheet.setContentView(R.layout.parlor_detail)
        sheet.findViewById<TextView>(R.id.detailTitle).text = p.businessName
        sheet.findViewById<TextView>(R.id.detailStatus).text = p.status
        sheet.findViewById<TextView>(R.id.detailBody).text = buildString {
            if (p.licenseNumber != "—") {
                appendLine("License number: ${p.licenseNumber}")
                appendLine("Profession: ${p.profession}")
                appendLine("Expires: ${p.expirationDate}")
                appendLine("Originally issued: ${p.originalIssueDate}")
            }
            appendLine()
            appendLine("${p.street}")
            appendLine("${p.city}, ${p.state} ${p.zip}")
            appendLine("County: ${p.county}")
            appendLine()
            if (p.licenseNumber != "—") {
                appendLine("Discipline on file: ${if (p.disciplineOnFile) "YES" else "No"}")
                appendLine("Public complaint: ${if (p.publicComplaint) "YES" else "No"}")
                appendLine("Data as of: ${p.dataAsOf}")
            }
            appendLine("Last checked: ${p.lastChecked}")
            p.notes?.let { if (it.isNotEmpty()) { appendLine(); appendLine("Notes: $it") } }
        }
        sheet.show()
    }
}
