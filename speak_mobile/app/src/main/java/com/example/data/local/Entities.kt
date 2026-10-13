package com.example.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "transcription_records")
data class TranscriptionRecord(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val timestamp: Long = System.currentTimeMillis(),
    val originalText: String,
    val transformedText: String? = null,
    val actionType: String = "dictation",
    val modelUsed: String = "gemini-3.5-transcribe-live",
    val wordCount: Int = 0,
    val characterCount: Int = 0,
    val latencyMs: Long = 0
)

@Entity(tableName = "smart_notes")
data class SmartNote(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val title: String,
    val content: String,
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis(),
    val wordCount: Int = 0,
    val characterCount: Int = 0,
    val tags: String = "Draft"
)

@Entity(tableName = "session_records")
data class SessionRecord(
    @PrimaryKey
    val id: String = java.util.UUID.randomUUID().toString(),
    val title: String,
    val transcript: String = "",
    val modelUsed: String = "gemini-3.1-flash-live",
    val updatedAt: Long = System.currentTimeMillis(),
    val wordCount: Int = 0
)
