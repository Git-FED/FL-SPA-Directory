package ai.ninjatech.fedspa

/**
 * One establishment row, used for BOTH tiers.
 *
 * Licensed rows come from assets/licensed.json (public, shipped in every
 * build). Unlicensed rows come from the decrypted subscriber envelope -
 * same shape, minus the license fields (licenseNumber is "—").
 *
 * Field names map 1:1 to data/meta/schema.json definitions:
 *   licensed_parlor / unlicensed_parlor.
 */
data class Parlor(
    val licenseNumber: String,
    val businessName: String,
    val profession: String,
    val status: String,
    val expirationDate: String,
    val originalIssueDate: String,
    val street: String,
    val city: String,
    val state: String,
    val zip: String,
    val county: String,
    val disciplineOnFile: Boolean,
    val publicComplaint: Boolean,
    val dataAsOf: String,
    val lastChecked: String,
    val notes: String?
) {
    /** "Boynton Beach, FL" style label for list rows. */
    val cityLine: String get() = "$city, $state"

    /** True when this row is from the subscriber watchlist tier. */
    val isUnlicensed: Boolean get() = licenseNumber == "—"

    /** Full mailing address on one line. */
    val addressLine: String get() = "$street, $city, $state $zip"

    /**
     * Days until expirationDate (ISO yyyy-mm-dd), or null when the row
     * has no expiration (unlicensed tier) or the date is unparseable.
     * Negative = already expired.
     */
    fun daysUntilExpiry(): Int? {
        if (expirationDate.isEmpty()) return null
        return try {
            val exp = java.time.LocalDate.parse(expirationDate)
            java.time.LocalDate.now().until(exp, java.time.temporal.ChronoUnit.DAYS).toInt()
        } catch (e: Exception) {
            null
        }
    }

    /** The web UI shows an "expiring soon" chip at <= 180 days; match it. */
    val expiringSoon: Boolean get() = (daysUntilExpiry() ?: 999) in 0..180
}
