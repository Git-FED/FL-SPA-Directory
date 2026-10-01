package ai.ninjatech.fedspa

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.BaseAdapter
import android.widget.TextView
import java.util.Locale

/**
 * Classic-views list adapter for parlor rows (used by MainActivity's
 * ListView when running in adapter mode, and by the detail dialog).
 *
 * Status colors mirror web/css/style.css:
 *   clear/active  -> teal  #2dd4a7
 *   delinquent    -> amber #f2c14e
 *   expired/revoked/no_license_found -> red #ff5f6d
 *   everything else -> slate #6b7687
 */
class ParlorAdapter(
    private val context: android.content.Context,
    private val items: List<Parlor>,
    private val onClick: (Parlor) -> Unit
) : BaseAdapter() {

    override fun getCount(): Int = items.size
    override fun getItem(position: Int): Parlor = items[position]
    override fun getItemId(position: Int): Long = position.toLong()

    override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
        val row = convertView ?: LayoutInflater.from(context)
            .inflate(R.layout.parlor_card, parent, false)
        val p = items[position]

        row.findViewById<TextView>(R.id.cardName).text = p.businessName
        row.findViewById<TextView>(R.id.cardLicense).text =
            if (p.isUnlicensed) context.getString(R.string.unlicensed_badge)
            else context.getString(R.string.license_prefix, p.licenseNumber)
        row.findViewById<TextView>(R.id.cardCity).text = p.cityLine
        row.findViewById<TextView>(R.id.cardStreet).text = p.street
        row.findViewById<TextView>(R.id.cardExpiry).text =
            if (p.isUnlicensed) "" else p.expirationDate

        val badge = row.findViewById<TextView>(R.id.cardStatus)
        badge.text = p.status.replaceFirstChar { it.uppercase(Locale.US) }
        badge.setBackgroundColor(statusColor(p.status))

        row.setOnClickListener { onClick(p) }
        return row
    }

    companion object {
        fun statusColor(status: String): Int = when (status.lowercase(Locale.US)) {
            "clear", "active" -> 0xFF2DD4A7.toInt()
            "delinquent", "probation" -> 0xFFF2C14E.toInt()
            "inactive" -> 0xFF6B7687.toInt()
            "expired", "revoked", "no_license_found" -> 0xFFFF5F6D.toInt()
            else -> 0xFF6B7687.toInt()
        }
    }
}
