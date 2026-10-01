package ai.ninjatech.fedspa

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.Context
import android.content.Intent
import android.widget.RemoteViews

/**
 * Home-screen widget: shows the licensed count + "data as of" date, with a
 * tap that opens the app. RemoteViews means classic views only - no
 * Compose, no RecyclerView here, deliberately simple.
 */
class WidgetProvider : AppWidgetProvider() {

    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray
    ) {
        val doc = NetworkHelper.loadLicensed(context)
        val count = doc?.optJSONArray("parlors")?.length() ?: 0
        val asOf = doc?.optString("as_of") ?: ""

        val tapIntent = PendingIntent.getActivity(
            context,
            0,
            Intent(context, MainActivity::class.java),
            PendingIntent.FLAG_IMMUTABLE
        )

        for (id in appWidgetIds) {
            val views = RemoteViews(context.packageName, R.layout.widget)
            views.setTextViewText(R.id.widgetCount, count.toString())
            views.setTextViewText(R.id.widgetAsOf, asOf)
            views.setOnClickPendingIntent(R.id.widgetRoot, tapIntent)
            appWidgetManager.updateAppWidget(id, views)
        }
    }
}
