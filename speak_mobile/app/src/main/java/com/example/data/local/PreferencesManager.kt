package com.example.data.local

import android.content.Context
import android.content.SharedPreferences
import com.example.data.model.CapsulePreferences
import com.example.data.model.CustomRefineAction
import com.example.data.model.QuickActionType
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import org.json.JSONArray
import org.json.JSONObject

class PreferencesManager(context: Context) {
    private val prefs: SharedPreferences = context.getSharedPreferences("speak_voice_prefs", Context.MODE_PRIVATE)

    private val _preferences = MutableStateFlow(loadPreferences())
    val preferences: StateFlow<CapsulePreferences> = _preferences.asStateFlow()

    private fun loadPreferences(): CapsulePreferences {
        val theme = prefs.getString("theme_mode", "DARK_OBSIDIAN") ?: "DARK_OBSIDIAN"
        val blur = prefs.getFloat("blur_radius", 24f)
        val border = prefs.getFloat("border_opacity", 0.18f)
        val actionId = prefs.getString("far_right_action", QuickActionType.REFINE.id) ?: QuickActionType.REFINE.id
        val action = QuickActionType.entries.find { it.id == actionId } ?: QuickActionType.REFINE
        val name = prefs.getString("user_name", "Alex") ?: "Alex"
        val lexiconRaw = prefs.getString("custom_lexicon", "Speak, Gemini 3.1 Flash Live, Kotlin, Void Violet, PCM 16kHz") ?: ""
        val lexiconList = if (lexiconRaw.isBlank()) emptyList() else lexiconRaw.split(",").map { it.trim() }
        val prompt = prefs.getString(
            "system_prompt",
            "You are Speak Voice Intelligence, a high-fidelity voice companion and dictation assistant. Transcribe and refine text with pristine accuracy."
        ) ?: ""
        val proAccess = prefs.getBoolean("pro_access_active", true)
        val customKey = prefs.getString("custom_api_key", "") ?: ""
        val backupKeysRaw = prefs.getString("backup_api_keys", "") ?: ""
        val backupKeys = if (backupKeysRaw.isBlank()) emptyList() else backupKeysRaw.split(";;;").filter { it.isNotBlank() }
        val onboarding = prefs.getBoolean("onboarding_completed", true)
        val alwaysOn = prefs.getBoolean("always_on_smart_mode", true)
        val haptic = prefs.getBoolean("haptic_feedback", true)
        val temp = prefs.getFloat("temperature", 0.3f)
        val maxSessions = prefs.getInt("max_stored_sessions", 5)
        val verification = prefs.getBoolean("verification_active", true)
        val overlayEnabled = prefs.getBoolean("draw_over_other_apps", false)
        val autoOpenTyping = prefs.getBoolean("auto_open_on_typing", false)
        val autoInsertText = prefs.getBoolean("auto_insert_text", true)
        val screenShare = prefs.getBoolean("screen_share_vision", false)
        val screenFps = prefs.getInt("screen_share_fps", 2)
        val screenQuality = prefs.getString("screen_share_quality", "720p") ?: "720p"
        val screenPrivacy = prefs.getBoolean("screen_share_privacy_mask", true)
        val sigMark = prefs.getString("custom_signature_mark", "") ?: ""

        val customActions = loadCustomActions()

        return CapsulePreferences(
            themeMode = theme,
            blurRadiusDp = blur,
            borderOpacity = border,
            farRightAction = action,
            userName = name,
            customLexicon = lexiconList,
            customSystemPrompt = prompt,
            proAccessActive = proAccess,
            customApiKey = customKey,
            backupApiKeys = backupKeys,
            onboardingCompleted = onboarding,
            alwaysOnSmartMode = alwaysOn,
            hapticFeedbackEnabled = haptic,
            temperature = temp,
            maxStoredSessions = maxSessions,
            verificationActive = verification,
            drawOverOtherAppsEnabled = overlayEnabled,
            autoOpenOnTypingEnabled = autoOpenTyping,
            autoInsertTextEnabled = autoInsertText,
            screenShareVisionActive = screenShare,
            screenShareFps = screenFps,
            screenShareQuality = screenQuality,
            screenSharePrivacyMask = screenPrivacy,
            customSignatureMark = sigMark,
            customActions = customActions
        )
    }

    private fun loadCustomActions(): List<CustomRefineAction> {
        val raw = prefs.getString("custom_refine_actions_json", null) ?: return listOf(
            CustomRefineAction(
                id = "custom_1",
                name = "Bulletize",
                voiceTrigger = "bulletize",
                prompt = "Format the text into clean, structured Markdown bullet points with bold lead-ins. Output only the bullets:",
                enabled = true
            ),
            CustomRefineAction(
                id = "custom_2",
                name = "Action Items",
                voiceTrigger = "tasks",
                prompt = "Extract clear, actionable to-do items from the text, formatted as a checkbox list with owners if mentioned. Output only the checklist:",
                enabled = false
            ),
            CustomRefineAction(
                id = "custom_3",
                name = "Executive Brief",
                voiceTrigger = "executive",
                prompt = "Convert this text into an executive summary paragraph followed by 3 strategic takeaways. Output only the brief:",
                enabled = false
            )
        )

        return try {
            val jsonArr = JSONArray(raw)
            val list = mutableListOf<CustomRefineAction>()
            for (i in 0 until jsonArr.length()) {
                val obj = jsonArr.getJSONObject(i)
                list.add(
                    CustomRefineAction(
                        id = obj.optString("id", "custom_$i"),
                        name = obj.optString("name", "Custom"),
                        voiceTrigger = obj.optString("voiceTrigger", "custom"),
                        prompt = obj.optString("prompt", ""),
                        enabled = obj.optBoolean("enabled", true)
                    )
                )
            }
            list
        } catch (e: Exception) {
            emptyList()
        }
    }

    fun updateTheme(themeMode: String) {
        prefs.edit().putString("theme_mode", themeMode).apply()
        _preferences.value = _preferences.value.copy(themeMode = themeMode)
    }

    fun updateBlurRadius(blurRadius: Float) {
        prefs.edit().putFloat("blur_radius", blurRadius).apply()
        _preferences.value = _preferences.value.copy(blurRadiusDp = blurRadius)
    }

    fun updateBorderOpacity(opacity: Float) {
        prefs.edit().putFloat("border_opacity", opacity).apply()
        _preferences.value = _preferences.value.copy(borderOpacity = opacity)
    }

    fun updateFarRightAction(action: QuickActionType) {
        prefs.edit().putString("far_right_action", action.id).apply()
        _preferences.value = _preferences.value.copy(farRightAction = action)
    }

    fun updateUserName(name: String) {
        prefs.edit().putString("user_name", name).apply()
        _preferences.value = _preferences.value.copy(userName = name)
    }

    fun updateLexicon(lexicon: List<String>) {
        val raw = lexicon.joinToString(",")
        prefs.edit().putString("custom_lexicon", raw).apply()
        _preferences.value = _preferences.value.copy(customLexicon = lexicon)
    }

    fun updateSystemPrompt(prompt: String) {
        prefs.edit().putString("system_prompt", prompt).apply()
        _preferences.value = _preferences.value.copy(customSystemPrompt = prompt)
    }

    fun updateCustomApiKey(key: String) {
        prefs.edit().putString("custom_api_key", key).apply()
        _preferences.value = _preferences.value.copy(customApiKey = key)
    }

    fun addBackupApiKey(key: String) {
        val current = _preferences.value.backupApiKeys.toMutableList()
        if (key.isNotBlank() && !current.contains(key)) {
            current.add(key)
            val raw = current.joinToString(";;;")
            prefs.edit().putString("backup_api_keys", raw).apply()
            _preferences.value = _preferences.value.copy(backupApiKeys = current)
        }
    }

    fun removeBackupApiKey(key: String) {
        val current = _preferences.value.backupApiKeys.toMutableList()
        current.remove(key)
        val raw = current.joinToString(";;;")
        prefs.edit().putString("backup_api_keys", raw).apply()
        _preferences.value = _preferences.value.copy(backupApiKeys = current)
    }

    fun setOnboardingCompleted(completed: Boolean) {
        prefs.edit().putBoolean("onboarding_completed", completed).apply()
        _preferences.value = _preferences.value.copy(onboardingCompleted = completed)
    }

    fun updateAlwaysOnSmartMode(enabled: Boolean) {
        prefs.edit().putBoolean("always_on_smart_mode", enabled).apply()
        _preferences.value = _preferences.value.copy(alwaysOnSmartMode = enabled)
    }

    fun updateHapticFeedback(enabled: Boolean) {
        prefs.edit().putBoolean("haptic_feedback", enabled).apply()
        _preferences.value = _preferences.value.copy(hapticFeedbackEnabled = enabled)
    }

    fun updateTemperature(temp: Float) {
        prefs.edit().putFloat("temperature", temp).apply()
        _preferences.value = _preferences.value.copy(temperature = temp)
    }

    fun updateMaxStoredSessions(max: Int) {
        val clamped = max.coerceIn(1, 20)
        prefs.edit().putInt("max_stored_sessions", clamped).apply()
        _preferences.value = _preferences.value.copy(maxStoredSessions = clamped)
    }

    fun updateVerificationActive(active: Boolean) {
        prefs.edit().putBoolean("verification_active", active).apply()
        _preferences.value = _preferences.value.copy(verificationActive = active)
    }

    fun updateDrawOverOtherApps(enabled: Boolean) {
        prefs.edit().putBoolean("draw_over_other_apps", enabled).apply()
        _preferences.value = _preferences.value.copy(drawOverOtherAppsEnabled = enabled)
    }

    fun updateAutoOpenOnTyping(enabled: Boolean) {
        prefs.edit().putBoolean("auto_open_on_typing", enabled).apply()
        _preferences.value = _preferences.value.copy(autoOpenOnTypingEnabled = enabled)
    }

    fun updateAutoInsertText(enabled: Boolean) {
        prefs.edit().putBoolean("auto_insert_text", enabled).apply()
        _preferences.value = _preferences.value.copy(autoInsertTextEnabled = enabled)
    }

    fun updateScreenShareVision(active: Boolean) {
        prefs.edit().putBoolean("screen_share_vision", active).apply()
        _preferences.value = _preferences.value.copy(screenShareVisionActive = active)
    }

    fun updateScreenShareFps(fps: Int) {
        prefs.edit().putInt("screen_share_fps", fps).apply()
        _preferences.value = _preferences.value.copy(screenShareFps = fps)
    }

    fun updateScreenShareQuality(quality: String) {
        prefs.edit().putString("screen_share_quality", quality).apply()
        _preferences.value = _preferences.value.copy(screenShareQuality = quality)
    }

    fun updateScreenSharePrivacyMask(enabled: Boolean) {
        prefs.edit().putBoolean("screen_share_privacy_mask", enabled).apply()
        _preferences.value = _preferences.value.copy(screenSharePrivacyMask = enabled)
    }

    fun updateCustomSignatureMark(mark: String) {
        prefs.edit().putString("custom_signature_mark", mark).apply()
        _preferences.value = _preferences.value.copy(customSignatureMark = mark)
    }

    fun updateCustomActions(actions: List<CustomRefineAction>) {
        val jsonArr = JSONArray()
        for (a in actions) {
            val obj = JSONObject()
            obj.put("id", a.id)
            obj.put("name", a.name)
            obj.put("voiceTrigger", a.voiceTrigger)
            obj.put("prompt", a.prompt)
            obj.put("enabled", a.enabled)
            jsonArr.put(obj)
        }
        prefs.edit().putString("custom_refine_actions_json", jsonArr.toString()).apply()
        _preferences.value = _preferences.value.copy(customActions = actions)
    }

    fun updatePreferences(newPrefs: CapsulePreferences) {
        updateTheme(newPrefs.themeMode)
        updateFarRightAction(newPrefs.farRightAction)
        updateLexicon(newPrefs.customLexicon)
        updateSystemPrompt(newPrefs.customSystemPrompt)
        updateCustomApiKey(newPrefs.customApiKey)
        updateTemperature(newPrefs.temperature)
        updateMaxStoredSessions(newPrefs.maxStoredSessions)
        updateVerificationActive(newPrefs.verificationActive)
        updateDrawOverOtherApps(newPrefs.drawOverOtherAppsEnabled)
        updateAutoOpenOnTyping(newPrefs.autoOpenOnTypingEnabled)
        updateAutoInsertText(newPrefs.autoInsertTextEnabled)
        updateScreenShareVision(newPrefs.screenShareVisionActive)
        updateScreenShareFps(newPrefs.screenShareFps)
        updateScreenShareQuality(newPrefs.screenShareQuality)
        updateScreenSharePrivacyMask(newPrefs.screenSharePrivacyMask)
        updateCustomSignatureMark(newPrefs.customSignatureMark)
        updateCustomActions(newPrefs.customActions)
        _preferences.value = newPrefs
    }
}
