package com.example.service

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.AccessibilityServiceInfo
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Bundle
import android.util.Log
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import com.example.FluidCapsuleApplication
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class SpeakTypingAccessibilityService : AccessibilityService() {

    private var activeEditableNode: AccessibilityNodeInfo? = null

    override fun onServiceConnected() {
        super.onServiceConnected()
        val info = AccessibilityServiceInfo().apply {
            eventTypes = AccessibilityEvent.TYPE_VIEW_FOCUSED or
                    AccessibilityEvent.TYPE_VIEW_CLICKED or
                    AccessibilityEvent.TYPE_VIEW_TEXT_CHANGED
            feedbackType = AccessibilityServiceInfo.FEEDBACK_GENERIC
            notificationTimeout = 100
            flags = AccessibilityServiceInfo.FLAG_RETRIEVE_INTERACTIVE_WINDOWS
        }
        serviceInfo = info
        instance = this
        _isAccessibilityActive.value = true
        Log.d(TAG, "SpeakTypingAccessibilityService connected.")
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event == null) return
        val type = event.eventType

        if (type == AccessibilityEvent.TYPE_VIEW_FOCUSED || type == AccessibilityEvent.TYPE_VIEW_CLICKED) {
            val source = event.source ?: return
            val className = source.className?.toString().orEmpty()
            val isEditable = source.isEditable ||
                    className.contains("EditText", ignoreCase = true) ||
                    className.contains("TextView", ignoreCase = true) && source.isFocusable

            if (isEditable) {
                activeEditableNode = source
                val pkg = event.packageName?.toString().orEmpty()
                _currentActiveApp.value = pkg

                val isPassword = source.isPassword
                _isPasswordFieldActive.value = isPassword

                try {
                    val app = FluidCapsuleApplication.instance
                    val prefs = app.preferencesManager.preferences.value

                    if (prefs.autoOpenOnTypingEnabled) {
                        Log.d(TAG, "Typing field detected in app $pkg. Triggering Speak overlay.")
                        FloatingCapsuleOverlayService.showOrExpand(this)
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Error handling typing event: ${e.message}")
                }
            }
        }
    }

    override fun onInterrupt() {
        Log.d(TAG, "SpeakTypingAccessibilityService interrupted.")
    }

    override fun onDestroy() {
        super.onDestroy()
        _isAccessibilityActive.value = false
        if (instance == this) {
            instance = null
        }
        activeEditableNode = null
    }

    companion object {
        private const val TAG = "SpeakAccessibility"

        var instance: SpeakTypingAccessibilityService? = null
            private set

        private val _isAccessibilityActive = MutableStateFlow(false)
        val isAccessibilityActive: StateFlow<Boolean> = _isAccessibilityActive.asStateFlow()

        private val _currentActiveApp = MutableStateFlow("")
        val currentActiveApp: StateFlow<String> = _currentActiveApp.asStateFlow()

        private val _isPasswordFieldActive = MutableStateFlow(false)
        val isPasswordFieldActive: StateFlow<Boolean> = _isPasswordFieldActive.asStateFlow()

        fun insertTextIntoFocusedField(context: Context, text: String): Boolean {
            val service = instance ?: return false
            val node = service.activeEditableNode ?: return false

            return try {
                val args = Bundle().apply {
                    putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, text)
                }
                val directSet = node.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args)
                if (!directSet) {
                    // Fallback to clipboard paste
                    val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                    clipboard.setPrimaryClip(ClipData.newPlainText("Speak Refined Voice", text))
                    node.performAction(AccessibilityNodeInfo.ACTION_PASTE)
                } else {
                    true
                }
            } catch (e: Exception) {
                Log.e(TAG, "Failed to insert text: ${e.message}")
                false
            }
        }
    }
}
