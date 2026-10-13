package com.example.data.local

import androidx.room.*
import kotlinx.coroutines.flow.Flow

@Dao
interface CapsuleDao {
    @Query("SELECT * FROM transcription_records ORDER BY timestamp DESC")
    fun getAllTranscriptions(): Flow<List<TranscriptionRecord>>

    @Query("SELECT * FROM transcription_records ORDER BY timestamp DESC LIMIT :limit")
    fun getRecentTranscriptions(limit: Int): Flow<List<TranscriptionRecord>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertTranscription(record: TranscriptionRecord): Long

    @Delete
    suspend fun deleteTranscription(record: TranscriptionRecord)

    @Query("DELETE FROM transcription_records")
    suspend fun clearAllTranscriptions()

    @Query("SELECT SUM(wordCount) FROM transcription_records")
    fun getTotalWordsTranscribed(): Flow<Int?>

    // Smart Notes
    @Query("SELECT * FROM smart_notes ORDER BY updatedAt DESC")
    fun getAllNotes(): Flow<List<SmartNote>>

    @Query("SELECT * FROM smart_notes WHERE id = :id")
    suspend fun getNoteById(id: Long): SmartNote?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertOrUpdateNote(note: SmartNote): Long

    @Delete
    suspend fun deleteNote(note: SmartNote)

    // Voice Sessions
    @Query("SELECT * FROM session_records ORDER BY updatedAt DESC")
    fun getAllSessions(): Flow<List<SessionRecord>>

    @Query("SELECT * FROM session_records WHERE id = :id")
    suspend fun getSessionById(id: String): SessionRecord?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertOrUpdateSession(session: SessionRecord)

    @Query("DELETE FROM session_records WHERE id = :id")
    suspend fun deleteSessionById(id: String)

    @Query("DELETE FROM session_records")
    suspend fun clearAllSessions()
}
