package ai.ninjatech.fedspa.auto

import android.app.SearchManager
import android.content.Intent
import android.os.Bundle
import android.service.voice.VoiceInteractionService

/**
 * Voice search hook for Android Auto / assistant queries.
 *
 * Flow: assistant fires a GLOBAL_SEARCH intent carrying QUERY extras ->
 * we parse the query against bundled licensed.json -> we launch
 * CarActivity with the query pre-filled so the user sees results
 * immediately on the car screen.
 *
 * No network, no cloud speech parsing - just string matching against
 * the packaged dataset. (A full androidx.car.app VoiceSession would be
 * the upgrade path; this keeps the module dependency-free.)
 */
class VoiceSearch : VoiceInteractionService() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val query = intent?.getStringExtra(SearchManager.QUERY)
            ?: intent?.getStringExtra(Intent.EXTRA_PROCESS_TEXT)
        if (!query.isNullOrBlank()) {
            val launch = Intent(this, CarActivity::class.java).apply {
                putExtra("voice_query", query)
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            startActivity(launch)
        }
        return START_NOT_STICKY
    }

    override fun onGetVoiceSearchResultActions(): Bundle? = null
}
