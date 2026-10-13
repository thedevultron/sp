package com.example.service

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.graphics.PixelFormat
import android.net.Uri
import android.os.Build
import android.os.IBinder
import android.provider.Settings
import android.util.Log
import android.view.Gravity
import android.view.View
import android.view.WindowManager
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.ComposeView
import androidx.compose.ui.platform.ViewCompositionStrategy
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.app.NotificationCompat
import androidx.lifecycle.*
import androidx.lifecycle.setViewTreeLifecycleOwner
import androidx.lifecycle.setViewTreeViewModelStoreOwner
import androidx.savedstate.SavedStateRegistry
import androidx.savedstate.SavedStateRegistryController
import androidx.savedstate.SavedStateRegistryOwner
import androidx.savedstate.setViewTreeSavedStateRegistryOwner
import com.example.FluidCapsuleApplication
import com.example.MainActivity
import com.example.R
import com.example.ui.capsule.FloatingCapsuleOverlay
import com.example.ui.theme.FluidCapsuleTheme
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class FloatingCapsuleOverlayService : Service(), LifecycleOwner, ViewModelStoreOwner, SavedStateRegistryOwner {

    private val lifecycleRegistry = LifecycleRegistry(this)
    private val appViewModelStore = ViewModelStore()
    private val savedStateRegistryController = SavedStateRegistryController.create(this)

    override val lifecycle: Lifecycle get() = lifecycleRegistry
    override val viewModelStore: ViewModelStore get() = appViewModelStore
    override val savedStateRegistry: SavedStateRegistry get() = savedStateRegistryController.savedStateRegistry

    private var windowManager: WindowManager? = null
    private var overlayComposeView: ComposeView? = null
    private var windowLayoutParams: WindowManager.LayoutParams? = null

    // Real-time overlay state
    private val _isOverlayVisible = MutableStateFlow(true)
    private val _isMinimized = MutableStateFlow(false)

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        savedStateRegistryController.performRestore(null)
        lifecycleRegistry.handleLifecycleEvent(Lifecycle.Event.ON_CREATE)
        lifecycleRegistry.handleLifecycleEvent(Lifecycle.Event.ON_START)
        lifecycleRegistry.handleLifecycleEvent(Lifecycle.Event.ON_RESUME)

        createNotificationChannel()
        startForegroundNotification()

        windowManager = getSystemService(Context.WINDOW_SERVICE) as WindowManager
        setupOverlayView()

        instance = this
        _isOverlayRunning.value = true
        Log.d(TAG, "FloatingCapsuleOverlayService created and running.")
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Speak Floating Overlay",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Universal voice dictation and text refinement floating capsule"
                setShowBadge(false)
            }
            val nm = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            nm.createNotificationChannel(channel)
        }
    }

    private fun startForegroundNotification() {
        val openIntent = Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }
        val pendingIntent = PendingIntent.getActivity(
            this,
            0,
            openIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Speak Floating Capsule")
            .setContentText("Universal voice intelligence active across all apps")
            .setSmallIcon(R.mipmap.ic_launcher)
            .setOngoing(true)
            .setContentIntent(pendingIntent)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()

        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                    startForeground(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE)
                } else {
                    startForeground(NOTIFICATION_ID, notification)
                }
            } else {
                startForeground(NOTIFICATION_ID, notification)
            }
        } catch (e: Exception) {
            Log.e(TAG, "Could not start as microphone foreground service: ${e.message}. Starting regular foreground.")
            try {
                startForeground(NOTIFICATION_ID, notification)
            } catch (ex: Exception) {
                Log.e(TAG, "Failed startForeground completely: ${ex.message}")
            }
        }
    }

    private fun setupOverlayView() {
        if (!Settings.canDrawOverlays(this)) {
            Log.w(TAG, "Cannot draw overlays: permission not granted.")
            return
        }

        val overlayType = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
        } else {
            @Suppress("DEPRECATION")
            WindowManager.LayoutParams.TYPE_PHONE
        }

        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            overlayType,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
                    WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.START
            x = 80
            y = 260
        }
        windowLayoutParams = params

        val composeView = ComposeView(this).apply {
            setViewCompositionStrategy(ViewCompositionStrategy.DisposeOnDetachedFromWindowOrReleasedFromPool)
            this.setViewTreeLifecycleOwner(this@FloatingCapsuleOverlayService)
            this.setViewTreeViewModelStoreOwner(this@FloatingCapsuleOverlayService)
            this.setViewTreeSavedStateRegistryOwner(this@FloatingCapsuleOverlayService)

            setContent {
                FluidCapsuleTheme {
                    OverlayContent()
                }
            }
        }
        overlayComposeView = composeView

        try {
            windowManager?.addView(composeView, params)
            Log.d(TAG, "Overlay view added to WindowManager.")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to add overlay view to WindowManager: ${e.message}")
        }
    }

    @Composable
    private fun OverlayContent() {
        val app = FluidCapsuleApplication.instance
        val isRecording by app.audioStreamer.isRecording.collectAsState()
        val isLiveConnected by app.liveWebSocketClient.isConnected.collectAsState()
        val amplitudes by app.audioStreamer.amplitudes.collectAsState()
        val streamingTranscript by app.liveStreamingTranscript.collectAsState()
        val transformingStatus by app.activeTransformState.collectAsState()
        val latestVoiceTalkback by app.latestVoiceTalkback.collectAsState()
        val isVisible by _isOverlayVisible.collectAsState()
        val isMinimized by _isMinimized.collectAsState()
        val currentApp by SpeakTypingAccessibilityService.currentActiveApp.collectAsState()

        if (!isVisible) return

        Box(
            modifier = Modifier
                .wrapContentSize()
                .pointerInput(Unit) {
                    detectDragGestures { change, dragAmount ->
                        change.consume()
                        val params = windowLayoutParams ?: return@detectDragGestures
                        params.x += dragAmount.x.toInt()
                        params.y += dragAmount.y.toInt()
                        try {
                            windowManager?.updateViewLayout(overlayComposeView, params)
                        } catch (e: Exception) {
                            Log.e(TAG, "Error updating window layout: ${e.message}")
                        }
                    }
                }
        ) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                FloatingCapsuleOverlay(
                    isRecording = isRecording,
                    isLiveTalkbackActive = isLiveConnected,
                    amplitudes = amplitudes,
                    memoryUsageFraction = (streamingTranscript.length / 1000f).coerceIn(0f, 1f),
                    isMinimized = isMinimized,
                    onToggleMinimize = {
                        _isMinimized.value = !_isMinimized.value
                    },
                    transformingStatus = transformingStatus,
                    isSpeakingBack = latestVoiceTalkback.isNotBlank(),
                    onCloseClick = {
                        _isOverlayVisible.value = false
                    },
                    onRestartContextClick = {
                        app.clearLiveTranscript()
                    },
                    onMicClick = {
                        if (isRecording) {
                            app.stopRecording()
                            // If user is currently typing in an external app and auto-insert is enabled
                            val prefs = app.preferencesManager.preferences.value
                            if (prefs.autoInsertTextEnabled && streamingTranscript.isNotBlank()) {
                                SpeakTypingAccessibilityService.insertTextIntoFocusedField(
                                    this@FloatingCapsuleOverlayService,
                                    streamingTranscript
                                )
                            }
                        } else {
                            app.startRecording(isTalkback = false)
                        }
                    },
                    onToggleTalkback = {
                        if (isRecording) {
                            app.stopRecording()
                        } else {
                            app.startRecording(isTalkback = true)
                        }
                    },
                    enableDragging = false // We handle dragging at the WindowManager level
                )

                // Subtitle badge if typing in an external app
                if (!isMinimized && currentApp.isNotBlank() && currentApp != packageName) {
                    val appSimpleName = currentApp.substringAfterLast(".")
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(8.dp))
                            .background(Color(0xCC111318))
                            .padding(horizontal = 8.dp, vertical = 2.dp)
                    ) {
                        Text(
                            text = "Over $appSimpleName • Tap to dictate",
                            fontSize = 10.sp,
                            color = Color(0xAAFFFFFF)
                        )
                    }
                }
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        lifecycleRegistry.handleLifecycleEvent(Lifecycle.Event.ON_PAUSE)
        lifecycleRegistry.handleLifecycleEvent(Lifecycle.Event.ON_STOP)
        lifecycleRegistry.handleLifecycleEvent(Lifecycle.Event.ON_DESTROY)
        appViewModelStore.clear()

        overlayComposeView?.let {
            try {
                windowManager?.removeView(it)
            } catch (e: Exception) {
                Log.e(TAG, "Error removing overlay view: ${e.message}")
            }
        }
        overlayComposeView = null
        windowManager = null
        _isOverlayRunning.value = false
        if (instance == this) {
            instance = null
        }
        Log.d(TAG, "FloatingCapsuleOverlayService destroyed.")
    }

    companion object {
        private const val TAG = "FloatingCapsuleService"
        private const val CHANNEL_ID = "speak_overlay_channel"
        private const val NOTIFICATION_ID = 2049

        var instance: FloatingCapsuleOverlayService? = null
            private set

        private val _isOverlayRunning = MutableStateFlow(false)
        val isOverlayRunning: StateFlow<Boolean> = _isOverlayRunning.asStateFlow()

        fun start(context: Context) {
            if (!Settings.canDrawOverlays(context)) {
                Log.w(TAG, "Cannot start overlay service: ACTION_MANAGE_OVERLAY_PERMISSION needed.")
                return
            }
            val intent = Intent(context, FloatingCapsuleOverlayService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(intent)
            } else {
                context.startService(intent)
            }
        }

        fun stop(context: Context) {
            val intent = Intent(context, FloatingCapsuleOverlayService::class.java)
            context.stopService(intent)
            _isOverlayRunning.value = false
        }

        fun toggle(context: Context) {
            if (isOverlayRunning.value) {
                stop(context)
            } else {
                start(context)
            }
        }

        fun showOrExpand(context: Context) {
            val service = instance
            if (service != null) {
                service._isOverlayVisible.value = true
                service._isMinimized.value = false
            } else {
                if (Settings.canDrawOverlays(context)) {
                    start(context)
                }
            }
        }
    }
}
