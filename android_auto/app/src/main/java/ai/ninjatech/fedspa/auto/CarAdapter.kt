package ai.ninjatech.fedspa.auto

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.BaseAdapter
import android.widget.TextView
import java.util.Locale

/**
 * Row adapter for the car list when a system ListView is used instead of
 * the LinearLayout container (tablet/dashboards in landscape). Same rows,
 * same big-target rules as CarActivity's inline rendering.
 */
class CarAdapter(
    private val context: Context,
    private val items: List<CarActivity.Row>,
    private val onClick: (CarActivity.Row) -> Unit
) : BaseAdapter() {

    override fun getCount(): Int = items.size
    override fun getItem(position: Int): CarActivity.Row = items[position]
    override fun getItemId(position: Int): Long = position.toLong()

    override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
        val row = convertView ?: LayoutInflater.from(context)
            .inflate(R.layout.car_row, parent, false)
        val item = items[position]

        row.findViewById<TextView>(R.id.rowName).text = item.name
        row.findViewById<TextView>(R.id.rowMeta).text = "${item.license} · ${item.city}"
        row.findViewById<TextView>(R.id.rowStatus).text =
            item.status.replaceFirstChar { it.uppercase(Locale.US) }

        row.setOnClickListener { onClick(item) }
        return row
    }

    companion object {
        /** Status color matching every other surface. */
        fun statusColor(status: String): Int = when (status.lowercase(Locale.US)) {
            "clear", "active" -> 0xFF2DD4A7.toInt()
            "delinquent", "probation" -> 0xFFF2C14E.toInt()
            "expired", "revoked" -> 0xFFFF5F6D.toInt()
            else -> 0xFF6B7687.toInt()
        }
    }
}
