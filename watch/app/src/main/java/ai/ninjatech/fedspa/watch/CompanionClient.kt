package ai.ninjatech.fedspa.watch

import android.app.Service
import android.content.Intent
import android.os.IBinder

/**
 * Phone <-> watch handoff service.
 *
 * The phone app (ai.ninjatech.fedspa) can bounce its current search
 * query to the watch with a simple startService intent. No data sync
 * protocol, no message bus - the watch carries its own bundled copy
 * of licensed.json, so all that travels is the query string.
 *
 * This service exists as the seam where a real Wear MessageClient
 * integration would go if the maintainer adopts
 * androidx.wear (Google's own library); today it's a plain intent
 * receiver, keeping the module dependency-free.
 */
class CompanionClient : Service() {

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val query = intent?.getStringExtra("voice_query")
        if (!query.isNullOrBlank()) {
            val launch = Intent(this, WatchActivity::class.java).apply {
                putExtra("voice_query", query)
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            startActivity(launch)
        }
        return START_NOT_STICKY
    }
}
