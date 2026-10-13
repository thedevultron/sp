package com.example

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.media.projection.MediaProjectionManager
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.*
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.example.data.local.SmartNote
import com.example.data.local.TranscriptionRecord
import com.example.service.FloatingCapsuleOverlayService
import com.example.service.SpeakTypingAccessibilityService
import com.example.ui.capsule.FloatingCapsuleOverlay
import com.example.ui.components.ElevatedBottomBar
import com.example.ui.components.MainDestination
import com.example.ui.editor.SmartEditorScreen
import com.example.ui.home.HomeDashboardScreen
import com.example.ui.onboarding.OnboardingScreen
import com.example.ui.sessions.SessionsScreen
import com.example.ui.settings.SettingsSanctuaryScreen
import com.example.ui.theme.CapsuleThemeMode
import com.example.ui.theme.FluidCapsuleTheme
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        val app = FluidCapsuleApplication.instance

        setContent {
            val context = LocalContext.current
            val scope = rememberCoroutineScope()
            val preferences by app.preferencesManager.preferences.collectAsStateWithLifecycle()
            val recentTranscriptionsFlow = remember { app.database.capsuleDao().getRecentTranscriptions(20) }
            val recentTranscriptions by recentTranscriptionsFlow.collectAsStateWithLifecycle(emptyList())

            val totalWordsFlow = remember { app.database.capsuleDao().getTotalWordsTranscribed() }
            val totalWordsTranscribed by totalWordsFlow.collectAsStateWithLifecycle(0)

            val isRecording by app.audioStreamer.isRecording.collectAsStateWithLifecycle()
            val amplitudes by app.audioStreamer.amplitudes.collectAsStateWithLifecycle()
            val isLiveConnected by app.liveWebSocketClient.isConnected.collectAsStateWithLifecycle()
            val tokenMemoryUsage by app.liveWebSocketClient.tokenUsageFraction.collectAsStateWithLifecycle()
            val liveTranscript by app.liveStreamingTranscript.collectAsStateWithLifecycle()
            val trackedSpokenWords by app.trackedSpokenWords.collectAsStateWithLifecycle()
            val lastReplacement by app.lastReplacement.collectAsStateWithLifecycle()
            val transformingStatus by app.activeTransformState.collectAsStateWithLifecycle()

            var showOnboarding by remember { mutableStateOf(!preferences.onboardingCompleted) }
            var currentDestination by remember { mutableStateOf(MainDestination.HOME) }
            var showInAppCapsule by remember { mutableStateOf(true) }
            var isCapsuleMinimized by remember { mutableStateOf(false) }
            var isLiveTalkbackActive by remember { mutableStateOf(false) }
            val isSpeakingBack by app.liveWebSocketClient.isSpeakingBack.collectAsStateWithLifecycle()

            // In-app movable capsule coordinates
            var capsuleX by remember { mutableFloatStateOf(0f) }
            var capsuleY by remember { mutableFloatStateOf(60f) }

            var editorContent by remember {
                mutableStateOf("# Speak Notes\n\nVoice intelligence active. Speak in real time or tap 'Refine & Polish' to transform text in place.")
            }
            var editorBaselineBeforeSpeech by remember { mutableStateOf("") }
            var isEditorTransforming by remember { mutableStateOf(false) }

            // Overlay & Accessibility status tracking
            var isOverlayPermissionGranted by remember {
                mutableStateOf(Settings.canDrawOverlays(this@MainActivity))
            }
            val isAccessibilityActive by SpeakTypingAccessibilityService.isAccessibilityActive.collectAsStateWithLifecycle()

            // MediaProjection Manager for Live Screen Context
            val mediaProjectionManager = remember {
                getSystemService(Context.MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
            }
            val screenCaptureLauncher = rememberLauncherForActivityResult(
                contract = ActivityResultContracts.StartActivityForResult()
            ) { result ->
                if (result.resultCode == android.app.Activity.RESULT_OK) {
                    Toast.makeText(this@MainActivity, "Live Screen Context connected!", Toast.LENGTH_SHORT).show()
                    app.preferencesManager.updateScreenShareVision(true)
                } else {
                    Toast.makeText(this@MainActivity, "Screen capture was cancelled", Toast.LENGTH_SHORT).show()
                    app.preferencesManager.updateScreenShareVision(false)
                }
            }

            // Sync overlay permission on activity resume
            DisposableEffect(lifecycle) {
                val observer = androidx.lifecycle.LifecycleEventObserver { _, event ->
                    if (event == androidx.lifecycle.Lifecycle.Event.ON_RESUME) {
                        isOverlayPermissionGranted = Settings.canDrawOverlays(this@MainActivity)
                        if (preferences.drawOverOtherAppsEnabled && isOverlayPermissionGranted) {
                            FloatingCapsuleOverlayService.start(this@MainActivity)
                        }
                    }
                }
                lifecycle.addObserver(observer)
                onDispose {
                    lifecycle.removeObserver(observer)
                }
            }

            // Reactively start or stop the overlay service based on preferences
            LaunchedEffect(preferences.drawOverOtherAppsEnabled, isOverlayPermissionGranted) {
                if (preferences.drawOverOtherAppsEnabled && isOverlayPermissionGranted) {
                    FloatingCapsuleOverlayService.start(this@MainActivity)
                } else if (!preferences.drawOverOtherAppsEnabled) {
                    FloatingCapsuleOverlayService.stop(this@MainActivity)
                }
            }

            // Runtime Microphone Permission Launcher
            val micPermissionLauncher = rememberLauncherForActivityResult(
                contract = ActivityResultContracts.RequestPermission()
            ) { isGranted ->
                if (isGranted) {
                    editorBaselineBeforeSpeech = editorContent
                    app.startNewSpeechSession()
                    app.liveWebSocketClient.startLiveSession(isTalkback = isLiveTalkbackActive)
                    val started = app.audioStreamer.startRecording()
                    if (!started) {
                        Toast.makeText(context, "Microphone initialized in simulation mode", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    Toast.makeText(context, "Microphone permission is required for live voice", Toast.LENGTH_SHORT).show()
                }
            }

            fun toggleLiveTalkback() {
                if (currentDestination == MainDestination.EDITOR || showOnboarding) {
                    Toast.makeText(context, "Talkback is disabled during Editor/Setup for controlled transcription", Toast.LENGTH_SHORT).show()
                    return
                }
                isLiveTalkbackActive = !isLiveTalkbackActive
                app.liveWebSocketClient.setTalkbackEnabled(isLiveTalkbackActive)
                if (isRecording) {
                    app.liveWebSocketClient.stopLiveSession()
                    app.liveWebSocketClient.startLiveSession(isTalkback = isLiveTalkbackActive)
                }
                val msg = if (isLiveTalkbackActive) {
                    "Live Talkback active: Gemini 3.1 Flash Live voice"
                } else {
                    "Real-time Transcription active (gemini-3.5-transcribe-live)"
                }
                Toast.makeText(context, msg, Toast.LENGTH_SHORT).show()
            }

            fun toggleRecordingWithPermission() {
                try {
                    if (isRecording) {
                        app.stopRecording()
                    } else {
                        val hasPerm = ContextCompat.checkSelfPermission(
                            context,
                            Manifest.permission.RECORD_AUDIO
                        ) == PackageManager.PERMISSION_GRANTED
                        if (hasPerm) {
                            editorBaselineBeforeSpeech = editorContent
                            val effectiveTalkback = isLiveTalkbackActive && currentDestination != MainDestination.EDITOR && !showOnboarding
                            app.startRecording(isTalkback = effectiveTalkback)
                        } else {
                            micPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
                        }
                    }
                } catch (e: Exception) {
                    Toast.makeText(context, "Recording error: ${e.localizedMessage}", Toast.LENGTH_SHORT).show()
                }
            }

            // Disable automated speech synthesis or talkback during editor or setup/onboarding phases
            LaunchedEffect(currentDestination, showOnboarding) {
                if (showOnboarding || currentDestination == MainDestination.EDITOR) {
                    if (isLiveTalkbackActive) {
                        isLiveTalkbackActive = false
                        app.liveWebSocketClient.setTalkbackEnabled(false)
                        if (isRecording) {
                            app.liveWebSocketClient.stopLiveSession()
                            app.liveWebSocketClient.startLiveSession(isTalkback = false)
                        }
                    }
                }
            }

            // Stream spoken words directly into the active editor
            LaunchedEffect(trackedSpokenWords) {
                if (isRecording && trackedSpokenWords.isNotBlank() && currentDestination == MainDestination.EDITOR) {
                    val base = editorBaselineBeforeSpeech.trim()
                    editorContent = if (base.isEmpty()) {
                        trackedSpokenWords
                    } else {
                        "$base $trackedSpokenWords"
                    }
                }
            }

            val themeEnum = remember(preferences.themeMode) {
                try {
                    CapsuleThemeMode.valueOf(preferences.themeMode)
                } catch (e: Exception) {
                    CapsuleThemeMode.DARK_OBSIDIAN
                }
            }

            FluidCapsuleTheme(
                themeMode = themeEnum,
                blurRadius = preferences.blurRadiusDp.dp,
                borderOpacity = preferences.borderOpacity
            ) {
                if (showOnboarding) {
                    OnboardingScreen(
                        preferences = preferences,
                        onUpdatePreferences = { updated ->
                            app.preferencesManager.updateUserName(updated.userName)
                            app.preferencesManager.updateLexicon(updated.customLexicon)
                        },
                        onCompleteOnboarding = {
                            app.preferencesManager.setOnboardingCompleted(true)
                            showOnboarding = false
                        }
                    )
                } else {
                    Box(modifier = Modifier.fillMaxSize()) {
                        Scaffold(
                            modifier = Modifier.fillMaxSize(),
                            contentWindowInsets = WindowInsets(0, 0, 0, 0),
                            bottomBar = {
                                ElevatedBottomBar(
                                    currentDestination = currentDestination,
                                    onDestinationSelected = { currentDestination = it }
                                )
                            }
                        ) { innerPadding ->
                            AnimatedContent(
                                targetState = currentDestination,
                                transitionSpec = { fadeIn() togetherWith fadeOut() },
                                modifier = Modifier
                                    .fillMaxSize()
                                    .padding(innerPadding),
                                label = "main_navigation_content"
                            ) { destination ->
                                when (destination) {
                                    MainDestination.HOME -> {
                                        HomeDashboardScreen(
                                            preferences = preferences,
                                            recentTranscriptions = recentTranscriptions,
                                            totalWords = totalWordsTranscribed ?: 0,
                                            isLiveConnected = isLiveConnected,
                                            isRecording = isRecording,
                                            tokenMemoryUsage = tokenMemoryUsage,
                                            showInAppCapsule = showInAppCapsule,
                                            onToggleInAppCapsule = { showInAppCapsule = !showInAppCapsule },
                                            onResetCapsulePosition = {
                                                capsuleX = 0f
                                                capsuleY = 60f
                                            },
                                            onStartRecordingToggle = {
                                                toggleRecordingWithPermission()
                                            },
                                            onClearHistory = {
                                                scope.launch {
                                                    app.database.capsuleDao().clearAllTranscriptions()
                                                }
                                            },
                                            onUpdateApiKey = { key ->
                                                app.preferencesManager.updateCustomApiKey(key)
                                            }
                                        )
                                    }
                                    MainDestination.EDITOR -> {
                                        SmartEditorScreen(
                                            currentText = editorContent,
                                            onTextChange = {
                                                editorContent = it
                                                app.updateActiveSessionTranscript(it)
                                            },
                                            liveStreamingTranscript = liveTranscript,
                                            trackedSpokenWords = trackedSpokenWords,
                                            lastReplacement = lastReplacement,
                                            isTransforming = isEditorTransforming,
                                            onFocusTextBox = {
                                                showInAppCapsule = true
                                            },
                                            onUndoReplacement = {
                                                val record = lastReplacement
                                                if (record != null) {
                                                    if (editorContent.contains(record.refinedText)) {
                                                        editorContent = editorContent.replace(record.refinedText, record.originalSpokenText)
                                                    } else {
                                                        editorContent = record.originalSpokenText
                                                    }
                                                    app.clearReplacementUndo()
                                                    Toast.makeText(context, "Reverted to original spoken text", Toast.LENGTH_SHORT).show()
                                                }
                                            },
                                            onApplyTransformation = { actionType, targetSegment ->
                                                scope.launch {
                                                    val textToTransform = targetSegment.ifBlank { editorContent }
                                                    if (textToTransform.isBlank()) return@launch

                                                    isEditorTransforming = true
                                                    val result = app.transformService.executeTransformation(textToTransform, actionType)
                                                    result.onSuccess { transformed ->
                                                        // Precisely delete original target segment and replace in-place
                                                        editorContent = if (editorContent.contains(textToTransform)) {
                                                            editorContent.replace(textToTransform, transformed)
                                                        } else {
                                                            transformed
                                                        }

                                                        // Track replacement for undo & stats
                                                        app.recordReplacement(
                                                            original = textToTransform,
                                                            refined = transformed,
                                                            start = 0,
                                                            end = transformed.length
                                                        )

                                                        app.database.capsuleDao().insertTranscription(
                                                            TranscriptionRecord(
                                                                originalText = textToTransform,
                                                                transformedText = transformed,
                                                                actionType = actionType.id,
                                                                modelUsed = com.example.data.api.GeminiModels.TRANSFORM_PRIMARY,
                                                                wordCount = transformed.split("\\s+".toRegex()).size,
                                                                characterCount = transformed.length
                                                            )
                                                        )
                                                    }
                                                    isEditorTransforming = false
                                                }
                                            },
                                            onSaveNote = { title, content ->
                                                scope.launch {
                                                    app.database.capsuleDao().insertOrUpdateNote(
                                                        SmartNote(
                                                             title = title.ifBlank { "Untitled Note" },
                                                            content = content,
                                                            wordCount = content.split("\\s+".toRegex()).size,
                                                            characterCount = content.length
                                                        )
                                                    )
                                                }
                                            }
                                        )
                                    }
                                    MainDestination.SESSIONS -> {
                                        SessionsScreen(
                                            onOpenSessionInEditor = {
                                                editorContent = app.liveStreamingTranscript.value
                                                currentDestination = MainDestination.EDITOR
                                            },
                                            onNavigateToHome = {
                                                currentDestination = MainDestination.HOME
                                            }
                                        )
                                    }
                                    MainDestination.SETTINGS -> {
                                        SettingsSanctuaryScreen(
                                            preferences = preferences,
                                            onUpdatePreferences = { updated ->
                                                app.preferencesManager.updatePreferences(updated)
                                            },
                                            onReplayOnboarding = {
                                                showOnboarding = true
                                            },
                                            isOverlayPermissionGranted = isOverlayPermissionGranted,
                                            isAccessibilityActive = isAccessibilityActive,
                                            onLaunchOverlayPermission = {
                                                try {
                                                    val intent = Intent(
                                                        Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                                                        Uri.parse("package:$packageName")
                                                    )
                                                    startActivity(intent)
                                                } catch (e: Exception) {
                                                    val fallback = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION)
                                                    startActivity(fallback)
                                                }
                                            },
                                            onLaunchAccessibilitySettings = {
                                                try {
                                                    val intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
                                                    startActivity(intent)
                                                } catch (e: Exception) {
                                                    Toast.makeText(this@MainActivity, "Could not open accessibility settings", Toast.LENGTH_SHORT).show()
                                                }
                                            },
                                            onRequestScreenCapture = {
                                                try {
                                                    screenCaptureLauncher.launch(mediaProjectionManager.createScreenCaptureIntent())
                                                } catch (e: Exception) {
                                                    Toast.makeText(this@MainActivity, "Screen capture not supported", Toast.LENGTH_SHORT).show()
                                                }
                                            }
                                        )
                                    }
                                }
                            }
                        }

                        // Floating In-App Movable Capsule (Rendered at top layer so user can drag it anywhere)
                        if (showInAppCapsule) {
                            Box(
                                modifier = Modifier
                                    .fillMaxSize()
                                    .statusBarsPadding()
                                    .padding(top = 16.dp),
                                contentAlignment = Alignment.TopCenter
                            ) {
                                FloatingCapsuleOverlay(
                                    isRecording = isRecording,
                                    isLiveTalkbackActive = isLiveTalkbackActive,
                                    amplitudes = amplitudes,
                                    memoryUsageFraction = tokenMemoryUsage,
                                    isMinimized = isCapsuleMinimized,
                                    onToggleMinimize = {
                                        isCapsuleMinimized = !isCapsuleMinimized
                                    },
                                    transformingStatus = transformingStatus,
                                    isSpeakingBack = isSpeakingBack,
                                    initialOffsetX = capsuleX,
                                    initialOffsetY = capsuleY,
                                    onPositionChanged = { x, y ->
                                        capsuleX = x
                                        capsuleY = y
                                    },
                                    onCloseClick = {
                                        showInAppCapsule = false
                                    },
                                    onRestartContextClick = {
                                        app.clearLiveTranscript()
                                    },
                                    onMicClick = {
                                        toggleRecordingWithPermission()
                                    },
                                    onToggleTalkback = {
                                        toggleLiveTalkback()
                                    },
                                    enableDragging = true
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}
