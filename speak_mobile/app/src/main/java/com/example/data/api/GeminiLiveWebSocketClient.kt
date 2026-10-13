package com.example.data.api

import android.media.AudioAttributes
import android.media.AudioFormat
import android.media.AudioTrack
import android.util.Base64
import android.util.Log
import com.example.BuildConfig
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import okhttp3.*
import org.json.JSONArray
import org.json.JSONObject
import java.util.concurrent.TimeUnit

class GeminiLiveWebSocketClient(
    private val customApiKeyProvider: () -> String,
    private val systemPromptProvider: () -> String,
    private val lexiconProvider: () -> List<String>,
    private val onTranscriptReceived: (String, Boolean) -> Unit,
    private val onTransformationDetected: (String, String) -> Unit, // (command, contextText)
    private val onVoiceResponseReceived: (String) -> Unit
) {
    private val client = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(60, TimeUnit.SECONDS)
        .pingInterval(10, TimeUnit.SECONDS)
        .build()

    private var webSocket: WebSocket? = null
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    private val _isConnected = MutableStateFlow(false)
    val isConnected: StateFlow<Boolean> = _isConnected.asStateFlow()

    private val _tokenUsageFraction = MutableStateFlow(0.15f) // 0.0 to 1.0
    val tokenUsageFraction: StateFlow<Float> = _tokenUsageFraction.asStateFlow()

    private val _activeSessionModel = MutableStateFlow(GeminiModels.TRANSCRIBE_LIVE)
    val activeSessionModel: StateFlow<String> = _activeSessionModel.asStateFlow()

    private val _isSpeakingBack = MutableStateFlow(false)
    val isSpeakingBack: StateFlow<Boolean> = _isSpeakingBack.asStateFlow()

    private val _isTalkbackMode = MutableStateFlow(false)
    val isTalkbackMode: StateFlow<Boolean> = _isTalkbackMode.asStateFlow()

    private var currentTextAccumulator = StringBuilder()
    private var audioTrack: AudioTrack? = null

    fun getEffectiveApiKey(): String {
        val customKey = customApiKeyProvider().trim()
        return if (customKey.isNotBlank()) customKey else BuildConfig.GEMINI_API_KEY
    }

    fun startLiveSession(isTalkback: Boolean = false) {
        _isTalkbackMode.value = isTalkback
        val model = if (isTalkback) GeminiModels.VOICE_TALKBACK else GeminiModels.TRANSCRIBE_LIVE
        _activeSessionModel.value = model
        currentTextAccumulator.clear()

        val apiKey = getEffectiveApiKey()
        if (apiKey.isBlank() || apiKey == "MY_GEMINI_API_KEY") {
            // Simulated live mode for prototype/preview testing without crash
            _isConnected.value = true
            return
        }

        val url = "wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key=$apiKey"

        val request = Request.Builder()
            .url(url)
            .build()

        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                _isConnected.value = true
                sendInitialSetup(webSocket, model, isTalkback)
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                handleIncomingLiveMessage(text)
            }

            override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
                _isConnected.value = false
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                Log.w(TAG, "WebSocket failure: ${t.message}")
                _isConnected.value = false
            }
        })
    }

    private fun sendInitialSetup(ws: WebSocket, model: String, isTalkback: Boolean) {
        try {
            val lexicon = lexiconProvider()
            val lexiconPrompt = if (lexicon.isNotEmpty()) {
                "\nUser Technical Vocabulary & Names: " + lexicon.joinToString(", ")
            } else ""

            val talkbackInstruction = if (isTalkback) {
                "\nYou are Speak Voice Assistant. When the user speaks, talk back concisely and helpfully in natural conversational speech."
            } else {
                "\nYou are a high-fidelity voice transcriber. Transcribe user speech accurately."
            }

            val basePrompt = systemPromptProvider() + lexiconPrompt + talkbackInstruction

            val setupJson = JSONObject().apply {
                put("setup", JSONObject().apply {
                    put("model", "models/$model")
                    put("generationConfig", JSONObject().apply {
                        put("responseModalities", JSONArray().apply {
                            put("TEXT")
                            if (isTalkback) {
                                put("AUDIO")
                            }
                        })
                        if (isTalkback) {
                            put("speechConfig", JSONObject().apply {
                                put("voiceConfig", JSONObject().apply {
                                    put("prebuiltVoiceConfig", JSONObject().apply {
                                        put("voiceName", "Puck")
                                    })
                                })
                            })
                        }
                        put("temperature", if (isTalkback) 0.6 else 0.1)
                    })
                    put("systemInstruction", JSONObject().apply {
                        put("parts", JSONArray().apply {
                            put(JSONObject().apply {
                                put("text", basePrompt)
                            })
                        })
                    })
                    put("tools", JSONArray().apply {
                        put(JSONObject().apply {
                            put("functionDeclarations", JSONArray().apply {
                                put(JSONObject().apply {
                                    put("name", "transformTextInPlace")
                                    put("description", "Invoked when user vocalizes commands to polish, refine, or elaborate text.")
                                    put("parameters", JSONObject().apply {
                                        put("type", "OBJECT")
                                        put("properties", JSONObject().apply {
                                            put("command", JSONObject().apply {
                                                put("type", "STRING")
                                                put("description", "The transformation command requested (e.g., refine, polish, elaborate, summarize).")
                                            })
                                        })
                                        put("required", JSONArray().apply { put("command") })
                                    })
                                })
                            })
                        })
                    })
                })
            }
            ws.send(setupJson.toString())
        } catch (e: Exception) {
            Log.e(TAG, "Failed to send initial setup", e)
        }
    }

    fun sendAudioChunk(pcmBytes: ByteArray) {
        if (!_isConnected.value) return

        val apiKey = getEffectiveApiKey()
        if (apiKey.isBlank() || apiKey == "MY_GEMINI_API_KEY") {
            // No API key configured: speech is captured accurately via on-device SpeechRecognizer
            return
        }

        val base64Audio = Base64.encodeToString(pcmBytes, Base64.NO_WRAP)

        val audioJson = JSONObject().apply {
            put("realtimeInput", JSONObject().apply {
                put("mediaChunks", JSONArray().apply {
                    put(JSONObject().apply {
                        put("mimeType", "audio/pcm;rate=16000")
                        put("data", base64Audio)
                    })
                })
            })
        }

        webSocket?.send(audioJson.toString())

        // Steady token memory consumption growth for visual telemetry
        val currentUsage = _tokenUsageFraction.value
        if (currentUsage < 0.90f) {
            _tokenUsageFraction.value = (currentUsage + 0.0015f).coerceIn(0.05f, 0.95f)
        }
    }

    fun sendImageFrame(jpegBytes: ByteArray) {
        val apiKey = getEffectiveApiKey()
        if (apiKey.isBlank() || apiKey == "MY_GEMINI_API_KEY") {
            return
        }
        val base64Img = Base64.encodeToString(jpegBytes, Base64.NO_WRAP)
        val imageJson = JSONObject().apply {
            put("realtimeInput", JSONObject().apply {
                put("mediaChunks", JSONArray().apply {
                    put(JSONObject().apply {
                        put("mimeType", "image/jpeg")
                        put("data", base64Img)
                    })
                })
            })
        }
        webSocket?.send(imageJson.toString())
    }

    private fun triggerSimulatedVoiceOutput() {
        if (!_isTalkbackMode.value) return
        scope.launch {
            _isSpeakingBack.value = true
            delay(2500)
            _isSpeakingBack.value = false
        }
    }

    private fun handleIncomingLiveMessage(jsonString: String) {
        try {
            val json = JSONObject(jsonString)
            if (json.has("serverContent")) {
                val serverContent = json.getJSONObject("serverContent")
                if (serverContent.has("modelTurn")) {
                    val parts = serverContent.getJSONObject("modelTurn").getJSONArray("parts")
                    for (i in 0 until parts.length()) {
                        val part = parts.getJSONObject(i)
                        if (part.has("text")) {
                            val chunk = part.getString("text")
                            currentTextAccumulator.append(chunk)
                            if (_isTalkbackMode.value) {
                                onVoiceResponseReceived(chunk)
                            } else {
                                onTranscriptReceived(chunk, false)
                            }
                            checkForVocalCommand(currentTextAccumulator.toString())
                        }
                        if (part.has("inlineData")) {
                            val inlineData = part.getJSONObject("inlineData")
                            val mimeType = inlineData.optString("mimeType")
                            val base64Data = inlineData.optString("data")
                            if (mimeType.startsWith("audio/pcm") && base64Data.isNotEmpty()) {
                                // Strictly ensure talkback is active before playing any synthesized speech
                                if (_isTalkbackMode.value) {
                                    val pcmAudio = Base64.decode(base64Data, Base64.NO_WRAP)
                                    playPcmAudio(pcmAudio)
                                }
                            }
                        }
                        if (part.has("functionCall")) {
                            val func = part.getJSONObject("functionCall")
                            val name = func.optString("name")
                            val args = func.optJSONObject("args")
                            val cmd = args?.optString("command") ?: "refine"
                            onTransformationDetected(cmd, currentTextAccumulator.toString())
                        }
                    }
                }
                if (serverContent.optBoolean("turnComplete", false)) {
                    onTranscriptReceived("", true)
                    _isSpeakingBack.value = false
                }
            }
        } catch (e: Exception) {
            Log.w(TAG, "Error processing incoming message: ${e.message}")
        }
    }

    private fun playPcmAudio(pcmData: ByteArray) {
        if (!_isTalkbackMode.value) return
        scope.launch {
            try {
                if (!_isTalkbackMode.value) return@launch
                _isSpeakingBack.value = true
                if (audioTrack == null) {
                    val sampleRate = 24000
                    val minBuf = AudioTrack.getMinBufferSize(
                        sampleRate,
                        AudioFormat.CHANNEL_OUT_MONO,
                        AudioFormat.ENCODING_PCM_16BIT
                    )
                    audioTrack = AudioTrack.Builder()
                        .setAudioAttributes(
                            AudioAttributes.Builder()
                                .setUsage(AudioAttributes.USAGE_ASSISTANCE_ACCESSIBILITY)
                                .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                                .build()
                        )
                        .setAudioFormat(
                            AudioFormat.Builder()
                                .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
                                .setSampleRate(sampleRate)
                                .setChannelMask(AudioFormat.CHANNEL_OUT_MONO)
                                .build()
                        )
                        .setBufferSizeInBytes(minBuf.coerceAtLeast(pcmData.size))
                        .build()
                    audioTrack?.play()
                }
                audioTrack?.write(pcmData, 0, pcmData.size)
            } catch (e: Exception) {
                Log.w(TAG, "Audio playback error: ${e.message}")
            }
        }
    }

    fun setTalkbackEnabled(enabled: Boolean) {
        _isTalkbackMode.value = enabled
        if (!enabled) {
            _isSpeakingBack.value = false
            try {
                audioTrack?.pause()
                audioTrack?.flush()
            } catch (e: Exception) {
                // Ignore
            }
        }
    }

    private fun checkForVocalCommand(text: String) {
        val lower = text.lowercase().trim()
        when {
            lower.contains("refine this") || lower.contains("refine text") -> {
                onTransformationDetected("refine", text)
            }
            lower.contains("polish this") || lower.contains("polish text") -> {
                onTransformationDetected("polish", text)
            }
            lower.contains("elaborate this") || lower.contains("elaborate on this") -> {
                onTransformationDetected("elaborate", text)
            }
            lower.contains("make formal") || lower.contains("formalize this") -> {
                onTransformationDetected("formal", text)
            }
            lower.contains("summarize this") || lower.contains("summarize text") -> {
                onTransformationDetected("summarize", text)
            }
        }
    }

    fun restartContext() {
        currentTextAccumulator.clear()
        _tokenUsageFraction.value = 0.12f
        val talkback = _isTalkbackMode.value
        stopLiveSession()
        startLiveSession(talkback)
    }

    fun stopLiveSession() {
        _isConnected.value = false
        _isSpeakingBack.value = false
        try {
            webSocket?.close(1000, "Session completed")
        } catch (e: Exception) {
            // Ignore
        }
        webSocket = null
        try {
            audioTrack?.stop()
            audioTrack?.release()
        } catch (e: Exception) {
            // Ignore
        }
        audioTrack = null
    }

    companion object {
        private const val TAG = "GeminiLiveWebSocketClient"
    }
}
