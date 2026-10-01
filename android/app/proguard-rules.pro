# FED-SPA Android R8 rules.
#
# The app is tiny and uses reflection NOWHERE except org.json (platform)
# and javax.crypto (platform). Data classes are plain Kotlin - R8 keeps
# them fine. The only thing worth pinning is the widget provider entry
# point referenced from the manifest, which AAPT rules handle anyway.
#
# Listed here to document intent: nothing to keep.

# org.json ships inside the Android platform; no action needed.

# Parlor data class is used only via properties; R8 may rename but
# never strip it because MainActivity references it directly.
-keep class ai.ninjatech.fedspa.Parlor { *; }
-keep class ai.ninjatech.fedspa.WidgetProvider { *; }

# Keep GCM cipher construction strings if R8 ever inlines them oddly.
-keepclassmembers class ai.ninjatech.fedspa.CryptoHelper { *; }
