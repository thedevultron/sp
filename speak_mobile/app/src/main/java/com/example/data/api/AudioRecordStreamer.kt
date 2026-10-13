package com.example.data.api

import android.annotation.SuppressLint
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlin.math.abs
import kotlin.math.sqrt

class AudioRecordStreamer(
    private val onAudioChunk: (ByteArray) -> Unit
) {
    companion object {
        const val SAMPLE_RATE = 16000
        const val CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO
        const val AUDIO_FORMAT = AudioFormat.ENCODING_PCM_16BIT
    }

    private var audioRecord: AudioRecord? = null
    private var recordingJob: Job? = null
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    private val _isRecording = MutableStateFlow(false)
    val isRecording: StateFlow<Boolean> = _isRecording.asStateFlow()

    // 5 normalized amplitude values (0f..1f) for multi-frequency 5-bar visualizer
    private val _amplitudes = MutableStateFlow(listOf(0.1f, 0.1f, 0.1f, 0.1f, 0.1f))
    val amplitudes: StateFlow<List<Float>> = _amplitudes.asStateFlow()

    @SuppressLint("MissingPermission")
    fun startRecording(): Boolean {
        if (_isRecording.value) return true

        val minBufferSize = AudioRecord.getMinBufferSize(
            SAMPLE_RATE,
            CHANNEL_CONFIG,
            AUDIO_FORMAT
        )

        val bufferSize = (minBufferSize * 2).coerceAtLeast(1024)

        try {
            audioRecord = AudioRecord(
                MediaRecorder.AudioSource.MIC,
                SAMPLE_RATE,
                CHANNEL_CONFIG,
                AUDIO_FORMAT,
                bufferSize
            )

            if (audioRecord?.state != AudioRecord.STATE_INITIALIZED) {
                audioRecord?.release()
                audioRecord = null
                return false
            }

            audioRecord?.startRecording()
            _isRecording.value = true

            recordingJob = scope.launch {
                val buffer = ShortArray(512)
                val byteBuffer = ByteArray(1024)

                while (isActive && _isRecording.value) {
                    val readCount = audioRecord?.read(buffer, 0, buffer.size) ?: -1
                    if (readCount > 0) {
                        // Convert ShortArray to ByteArray (Little-Endian PCM 16-bit)
                        for (i in 0 until readCount) {
                            val shortVal = buffer[i].toInt()
                            byteBuffer[i * 2] = (shortVal and 0xFF).toByte()
                            byteBuffer[i * 2 + 1] = ((shortVal shr 8) and 0xFF).toByte()
                        }
                        val validBytes = byteBuffer.copyOf(readCount * 2)
                        onAudioChunk(validBytes)

                        // Compute multi-frequency bar heights
                        computeWaveformBars(buffer, readCount)
                    } else {
                        delay(20)
                    }
                }
            }
            return true
        } catch (e: Exception) {
            _isRecording.value = false
            return false
        }
    }

    private fun computeWaveformBars(buffer: ShortArray, readCount: Int) {
        if (readCount <= 0) return
        var sumSquares = 0.0
        val segmentSize = (readCount / 5).coerceAtLeast(1)
        val bars = FloatArray(5)

        for (b in 0 until 5) {
            var segmentSum = 0.0
            val start = b * segmentSize
            val end = ((b + 1) * segmentSize).coerceAtMost(readCount)
            for (i in start until end) {
                val sample = buffer[i]
                segmentSum += abs(sample.toDouble())
                sumSquares += sample * sample
            }
            val avg = if (end > start) segmentSum / (end - start) else 0.0
            val normalized = (avg / 12000.0).toFloat().coerceIn(0.12f, 1.0f)
            bars[b] = normalized
        }

        // Add natural harmonic variation
        val baseRms = sqrt(sumSquares / readCount)
        val overallEnergy = (baseRms / 14000.0).toFloat().coerceIn(0.1f, 1.0f)

        _amplitudes.value = listOf(
            (bars[0] * 0.7f + overallEnergy * 0.3f).coerceIn(0.12f, 1.0f),
            (bars[1] * 0.9f + overallEnergy * 0.4f).coerceIn(0.15f, 1.0f),
            (bars[2] * 1.1f + overallEnergy * 0.5f).coerceIn(0.20f, 1.0f),
            (bars[3] * 0.85f + overallEnergy * 0.4f).coerceIn(0.15f, 1.0f),
            (bars[4] * 0.65f + overallEnergy * 0.3f).coerceIn(0.12f, 1.0f)
        )
    }

    fun stopRecording() {
        _isRecording.value = false
        recordingJob?.cancel()
        recordingJob = null
        try {
            audioRecord?.stop()
            audioRecord?.release()
        } catch (e: Exception) {
            // Ignore clean teardown exceptions
        }
        audioRecord = null
        _amplitudes.value = listOf(0.1f, 0.1f, 0.1f, 0.1f, 0.1f)
    }
}
