package com.example.data.api

object GeminiModels {
    // Primary Live Model: Gemini 3.1 Flash Live (Primary live model per user request)
    const val GEMINI_3_1_FLASH_LIVE = "gemini-3.1-flash-live"
    const val LIVE_PRIMARY = "gemini-3.1-flash-live"
    const val LIVE_FALLBACK_1 = "gemini-3-flash-live"
    const val LIVE_FALLBACK_2 = "gemini-2.5-flash-live"

    // Voice Transcription Engine: 16kHz PCM streaming
    const val TRANSCRIBE_LIVE = "gemini-3.1-flash-live"

    // Live Voice Talkback & Multimodal Companion
    const val VOICE_TALKBACK = "gemini-3.1-flash-live"

    // Smart Mode In-Place Transformations: Primary Production Model
    const val TRANSFORM_PRIMARY = "gemini-3.5-flash-lite"

    // Smart Mode In-Place Transformations: Backup Automated Fallback Model
    const val TRANSFORM_FALLBACK = "gemini-3.1-flash-lite"
}

