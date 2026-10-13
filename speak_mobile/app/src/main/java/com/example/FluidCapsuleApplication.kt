package com.example

import android.app.Application
import android.util.Log
import com.example.data.api.AudioRecordStreamer
import com.example.data.api.GeminiLiveWebSocketClient
import com.example.data.api.GeminiTransformService
import com.example.data.audio.SpeechInputManager
import com.example.data.local.AppDatabase
import com.example.data.local.PreferencesManager
import com.example.data.local.SessionRecord
import com.example.data.local.TranscriptionRecord
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class SpokenReplacementRecord(
    val originalSpokenText: String,
    val refinedText: String,
    val startIndex: Int = 0,
    val endIndex: Int = 0,
    val timestamp: Long = System.currentTimeMillis()
)

data class LiveSessionData(
    val id: String = java.util.UUID.randomUUID().toString(),
    val title: String,
    val transcript: String = "",
    val modelUsed: String = com.example.data.api.GeminiModels.GEMINI_3_1_FLASH_LIVE,
    val timestamp: Long = System.currentTimeMillis(),
    val wordCount: Int = 0
)

class FluidCapsuleApplication : Application() {
    val applicationScope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    lateinit var database: AppDatabase
        private set

    lateinit var preferencesManager: PreferencesManager
        private set

    lateinit var transformService: GeminiTransformService
        private set

    lateinit var liveWebSocketClient: GeminiLiveWebSocketClient
        private set

    lateinit var audioStreamer: AudioRecordStreamer
        private set

    lateinit var speechInputManager: SpeechInputManager
        private set

    // Multi-Session Engine
    private val _sessions = MutableStateFlow<List<LiveSessionData>>(emptyList())
    val sessions: StateFlow<List<LiveSessionData>> = _sessions.asStateFlow()

    private val _activeSessionId = MutableStateFlow("")
    val activeSessionId: StateFlow<String> = _activeSessionId.asStateFlow()

    // Real-time speech stream state for active screens & floating capsule
    private val _liveStreamingTranscript = MutableStateFlow("")
    val liveStreamingTranscript: StateFlow<String> = _liveStreamingTranscript.asStateFlow()

    // Exact spoken words tracked in the current vocal session
    private val _trackedSpokenWords = MutableStateFlow("")
    val trackedSpokenWords: StateFlow<String> = _trackedSpokenWords.asStateFlow()

    // Last in-place replacement (original words deleted and replaced with refined)
    private val _lastReplacement = MutableStateFlow<SpokenReplacementRecord?>(null)
    val lastReplacement: StateFlow<SpokenReplacementRecord?> = _lastReplacement.asStateFlow()

    private val _latestVoiceTalkback = MutableStateFlow("")
    val latestVoiceTalkback: StateFlow<String> = _latestVoiceTalkback.asStateFlow()

    private val _activeTransformState = MutableStateFlow<String?>(null)
    val activeTransformState: StateFlow<String?> = _activeTransformState.asStateFlow()

    private var currentSessionBaseText = ""

    override fun onCreate() {
        super.onCreate()
        instance = this

        database = AppDatabase.getInstance(this)
        preferencesManager = PreferencesManager(this)

        transformService = GeminiTransformService(
            customApiKeyProvider = { preferencesManager.preferences.value.customApiKey },
            lexiconProvider = { preferencesManager.preferences.value.customLexicon }
        )

        liveWebSocketClient = GeminiLiveWebSocketClient(
            customApiKeyProvider = { preferencesManager.preferences.value.customApiKey },
            systemPromptProvider = { preferencesManager.preferences.value.customSystemPrompt },
            lexiconProvider = { preferencesManager.preferences.value.customLexicon },
            onTranscriptReceived = { chunk, isTurnComplete ->
                if (chunk.isNotEmpty()) {
                    val updated = _liveStreamingTranscript.value + chunk
                    _liveStreamingTranscript.value = updated
                    _trackedSpokenWords.value += chunk
                    updateActiveSessionTranscript(updated)
                }
            },
            onTransformationDetected = { cmd, contextText ->
                applicationScope.launch {
                    _activeTransformState.value = "Executing: $cmd"
                    val result = transformService.executeSmartCommand(contextText, cmd)
                    result.onSuccess { transformed ->
                        updateActiveSessionTranscript(transformed)
                        _activeTransformState.value = null
                    }
                }
            },
            onVoiceResponseReceived = { voiceResponseChunk ->
                _latestVoiceTalkback.value = voiceResponseChunk
            }
        )

        speechInputManager = SpeechInputManager(
            context = this,
            onPartialResult = { partial ->
                val full = if (currentSessionBaseText.isNotBlank()) "$currentSessionBaseText $partial" else partial
                _liveStreamingTranscript.value = full
                _trackedSpokenWords.value = partial
                updateActiveSessionTranscript(full)
            },
            onFinalResult = { final ->
                val full = if (currentSessionBaseText.isNotBlank()) "$currentSessionBaseText $final" else final
                currentSessionBaseText = full
                _liveStreamingTranscript.value = full
                _trackedSpokenWords.value = final
                updateActiveSessionTranscript(full)
            },
            onError = { errorMsg ->
                Log.d("FluidCapsuleApp", "Speech recognizer status: $errorMsg")
            }
        )

        audioStreamer = AudioRecordStreamer { pcmBytes ->
            liveWebSocketClient.sendAudioChunk(pcmBytes)
        }

        // Load sessions from Room database
        applicationScope.launch(Dispatchers.IO) {
            database.capsuleDao().getAllSessions().collect { sessionRecords ->
                if (sessionRecords.isEmpty()) {
                    val initialId = "default_session_1"
                    val initial = SessionRecord(
                        id = initialId,
                        title = "Session 1",
                        transcript = "",
                        modelUsed = com.example.data.api.GeminiModels.GEMINI_3_1_FLASH_LIVE,
                        updatedAt = System.currentTimeMillis(),
                        wordCount = 0
                    )
                    database.capsuleDao().insertOrUpdateSession(initial)
                } else {
                    val mapped = sessionRecords.map {
                        LiveSessionData(
                            id = it.id,
                            title = it.title,
                            transcript = it.transcript,
                            modelUsed = it.modelUsed,
                            timestamp = it.updatedAt,
                            wordCount = it.wordCount
                        )
                    }
                    _sessions.value = mapped
                    if (_activeSessionId.value.isEmpty() || mapped.none { it.id == _activeSessionId.value }) {
                        val first = mapped.first()
                        _activeSessionId.value = first.id
                        _liveStreamingTranscript.value = first.transcript
                        _trackedSpokenWords.value = first.transcript
                        currentSessionBaseText = first.transcript
                    }
                }
            }
        }
    }

    fun startRecording(isTalkback: Boolean = false) {
        currentSessionBaseText = _liveStreamingTranscript.value.trim()
        _latestVoiceTalkback.value = ""
        _trackedSpokenWords.value = ""
        audioStreamer.startRecording()
        speechInputManager.startListening()
        liveWebSocketClient.startLiveSession(isTalkback = isTalkback)
    }

    fun stopRecording() {
        audioStreamer.stopRecording()
        speechInputManager.stopListening()
        liveWebSocketClient.stopLiveSession()

        val currentText = _liveStreamingTranscript.value.trim()
        val words = if (currentText.isBlank()) 0 else currentText.split("\\s+".toRegex()).size
        if (currentText.isNotBlank()) {
            applicationScope.launch(Dispatchers.IO) {
                database.capsuleDao().insertTranscription(
                    TranscriptionRecord(
                        originalText = currentText,
                        modelUsed = com.example.data.api.GeminiModels.GEMINI_3_1_FLASH_LIVE,
                        wordCount = words,
                        characterCount = currentText.length
                    )
                )
            }
        }
    }

    fun updateActiveSessionTranscript(newText: String) {
        _liveStreamingTranscript.value = newText
        val currentId = _activeSessionId.value
        val words = if (newText.isBlank()) 0 else newText.trim().split("\\s+".toRegex()).size

        val currentList = _sessions.value
        val updatedList = currentList.map {
            if (it.id == currentId) {
                it.copy(transcript = newText, wordCount = words, timestamp = System.currentTimeMillis())
            } else it
        }
        _sessions.value = updatedList

        applicationScope.launch(Dispatchers.IO) {
            val item = updatedList.find { it.id == currentId }
            if (item != null) {
                database.capsuleDao().insertOrUpdateSession(
                    SessionRecord(
                        id = item.id,
                        title = item.title,
                        transcript = item.transcript,
                        modelUsed = item.modelUsed,
                        updatedAt = item.timestamp,
                        wordCount = item.wordCount
                    )
                )
            }
        }
    }

    fun startNewSpeechSession() {
        _trackedSpokenWords.value = ""
        _liveStreamingTranscript.value = ""
        _latestVoiceTalkback.value = ""
        currentSessionBaseText = ""
    }

    fun recordReplacement(original: String, refined: String, start: Int, end: Int) {
        _lastReplacement.value = SpokenReplacementRecord(
            originalSpokenText = original,
            refinedText = refined,
            startIndex = start,
            endIndex = end
        )
    }

    fun clearReplacementUndo() {
        _lastReplacement.value = null
    }

    fun clearLiveTranscript() {
        _liveStreamingTranscript.value = ""
        _trackedSpokenWords.value = ""
        _latestVoiceTalkback.value = ""
        currentSessionBaseText = ""
        updateActiveSessionTranscript("")
        liveWebSocketClient.restartContext()
    }

    fun appendLiveTranscript(text: String) {
        val updated = _liveStreamingTranscript.value + text
        updateActiveSessionTranscript(updated)
        _trackedSpokenWords.value += text
    }

    fun createNewSession(customTitle: String = ""): String {
        val newId = java.util.UUID.randomUUID().toString()
        val title = if (customTitle.isNotBlank()) customTitle else "Session #${_sessions.value.size + 1}"
        val newSession = LiveSessionData(
            id = newId,
            title = title,
            transcript = "",
            modelUsed = com.example.data.api.GeminiModels.GEMINI_3_1_FLASH_LIVE,
            timestamp = System.currentTimeMillis(),
            wordCount = 0
        )

        val maxSessions = preferencesManager.preferences.value.maxStoredSessions
        val updated = mutableListOf(newSession)
        updated.addAll(_sessions.value)
        val clamped = updated.take(maxSessions)
        _sessions.value = clamped
        _activeSessionId.value = newId

        _liveStreamingTranscript.value = ""
        _trackedSpokenWords.value = ""
        _latestVoiceTalkback.value = ""
        currentSessionBaseText = ""
        liveWebSocketClient.restartContext()

        applicationScope.launch(Dispatchers.IO) {
            database.capsuleDao().insertOrUpdateSession(
                SessionRecord(
                    id = newSession.id,
                    title = newSession.title,
                    transcript = "",
                    modelUsed = newSession.modelUsed,
                    updatedAt = newSession.timestamp,
                    wordCount = 0
                )
            )
        }
        return newId
    }

    fun switchToSession(sessionId: String) {
        val target = _sessions.value.find { it.id == sessionId } ?: return
        _activeSessionId.value = sessionId
        _liveStreamingTranscript.value = target.transcript
        _trackedSpokenWords.value = target.transcript
        currentSessionBaseText = target.transcript
    }

    fun deleteSession(sessionId: String) {
        val updated = _sessions.value.filter { it.id != sessionId }
        _sessions.value = updated

        applicationScope.launch(Dispatchers.IO) {
            database.capsuleDao().deleteSessionById(sessionId)
        }

        if (_activeSessionId.value == sessionId) {
            val next = updated.firstOrNull()
            if (next != null) {
                switchToSession(next.id)
            } else {
                createNewSession("Session 1")
            }
        }
    }

    fun clearAllSessions() {
        stopRecording()
        _liveStreamingTranscript.value = ""
        _trackedSpokenWords.value = ""
        _latestVoiceTalkback.value = ""
        currentSessionBaseText = ""
        _sessions.value = emptyList()

        applicationScope.launch(Dispatchers.IO) {
            database.capsuleDao().clearAllSessions()
            createNewSession("Session 1")
        }
    }

    // Alias for backwards compatibility
    fun purgeAllSessions() {
        clearAllSessions()
    }

    fun hardReset() {
        stopRecording()
        _liveStreamingTranscript.value = ""
        _trackedSpokenWords.value = ""
        _latestVoiceTalkback.value = ""
        _lastReplacement.value = null
        currentSessionBaseText = ""
        updateActiveSessionTranscript("")
        liveWebSocketClient.restartContext()
    }

    companion object {
        lateinit var instance: FluidCapsuleApplication
            private set
    }
}
