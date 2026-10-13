package com.example.ui.sessions

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.widget.Toast
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.FluidCapsuleApplication
import com.example.LiveSessionData
import com.example.ui.components.*
import com.example.ui.theme.LocalGlassTokens
import java.text.SimpleDateFormat
import java.util.*

@Composable
fun SessionsScreen(
    modifier: Modifier = Modifier,
    onOpenSessionInEditor: () -> Unit = {},
    onNavigateToHome: () -> Unit = {}
) {
    val app = FluidCapsuleApplication.instance
    val context = LocalContext.current
    val tokens = LocalGlassTokens.current

    val sessions by app.sessions.collectAsState()
    val activeSessionId by app.activeSessionId.collectAsState()
    val currentTranscript by app.liveStreamingTranscript.collectAsState()
    val prefs by app.preferencesManager.preferences.collectAsState()

    var showNewSessionDialog by remember { mutableStateOf(false) }
    var newSessionTitleInput by remember { mutableStateOf("") }
    var showDeleteAllConfirmDialog by remember { mutableStateOf(false) }

    val dateFormat = remember { SimpleDateFormat("MMM d, HH:mm", Locale.getDefault()) }

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(tokens.bgDark)
    ) {
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 20.dp),
            contentPadding = PaddingValues(top = 24.dp, bottom = 100.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Header
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = "Sessions",
                            fontSize = 26.sp,
                            fontWeight = FontWeight.Bold,
                            color = tokens.textPrimary
                        )
                        Text(
                            text = "Manage your voice dictations and notes",
                            fontSize = 13.sp,
                            color = tokens.textSecondary
                        )
                    }

                    // New Session Button
                    Button(
                        onClick = {
                            newSessionTitleInput = ""
                            showNewSessionDialog = true
                        },
                        colors = ButtonDefaults.buttonColors(
                            containerColor = tokens.accentViolet,
                            contentColor = Color.White
                        ),
                        shape = RoundedCornerShape(20.dp),
                        contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                        modifier = Modifier.testTag("btn_new_session")
                    ) {
                        Text("+ New", fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
                    }
                }
            }

            // Current Active Session Overview Card
            item {
                val activeSession = sessions.find { it.id == activeSessionId }
                val displayTranscript = if (currentTranscript.isNotBlank()) currentTranscript
                else activeSession?.transcript?.ifBlank { "No text recorded yet. Tap Speak to start dictating." }
                    ?: "No text recorded yet. Tap Speak to start dictating."

                val wordCount = if (displayTranscript.isBlank() || displayTranscript.startsWith("No text")) 0
                else displayTranscript.trim().split("\\s+".toRegex()).size

                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(20.dp))
                        .background(
                            Brush.linearGradient(
                                colors = listOf(tokens.surfaceGlass, Color(0x33663AF3))
                            )
                        )
                        .border(BorderStroke(1.dp, tokens.accentViolet.copy(alpha = 0.5f)), RoundedCornerShape(20.dp))
                        .padding(18.dp)
                ) {
                    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(10.dp)
                                        .clip(CircleShape)
                                        .background(Color(0xFF00E676))
                                )
                                Text(
                                    text = "ACTIVE SESSION",
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = Color(0xFF00E676),
                                    letterSpacing = 1.sp
                                )
                            }
                            Text(
                                text = "$wordCount words",
                                fontSize = 12.sp,
                                color = tokens.textSecondary,
                                fontWeight = FontWeight.Medium
                            )
                        }

                        Text(
                            text = activeSession?.title ?: "Current Session",
                            fontSize = 18.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = tokens.textPrimary
                        )

                        Text(
                            text = displayTranscript,
                            fontSize = 13.sp,
                            color = tokens.textSecondary,
                            maxLines = 3,
                            overflow = TextOverflow.Ellipsis
                        )

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            TextButton(
                                onClick = onNavigateToHome,
                                contentPadding = PaddingValues(horizontal = 8.dp, vertical = 4.dp)
                            ) {
                                Text("Speak →", color = tokens.textSecondary, fontSize = 13.sp)
                            }

                            Button(
                                onClick = onOpenSessionInEditor,
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = tokens.accentViolet,
                                    contentColor = Color.White
                                ),
                                shape = RoundedCornerShape(12.dp),
                                contentPadding = PaddingValues(horizontal = 14.dp, vertical = 6.dp)
                            ) {
                                Text("Open in Editor", fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
                            }
                        }
                    }
                }
            }

            // Session History Section Header
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Saved Sessions (${sessions.size})",
                        fontSize = 16.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = tokens.textPrimary
                    )

                    if (sessions.isNotEmpty()) {
                        TextButton(
                            onClick = { showDeleteAllConfirmDialog = true },
                            contentPadding = PaddingValues(horizontal = 8.dp, vertical = 2.dp)
                        ) {
                            Text("Clear History", color = Color(0xFFFF5252), fontSize = 13.sp, fontWeight = FontWeight.Medium)
                        }
                    }
                }
            }

            // Session List Items
            items(sessions, key = { it.id }) { session ->
                SessionItemCard(
                    session = session,
                    isActive = session.id == activeSessionId,
                    formattedDate = dateFormat.format(Date(session.timestamp)),
                    onSelect = {
                        app.switchToSession(session.id)
                        onOpenSessionInEditor()
                        Toast.makeText(context, "Opened: ${session.title}", Toast.LENGTH_SHORT).show()
                    },
                    onCopy = {
                        val cm = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                        cm.setPrimaryClip(ClipData.newPlainText("Session Transcript", session.transcript))
                        Toast.makeText(context, "Copied to clipboard", Toast.LENGTH_SHORT).show()
                    },
                    onDelete = {
                        app.deleteSession(session.id)
                        Toast.makeText(context, "Session removed", Toast.LENGTH_SHORT).show()
                    }
                )
            }

            // Settings & Storage Capacity
            item {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(16.dp))
                        .background(tokens.surfaceGlass)
                        .border(BorderStroke(0.5.dp, tokens.borderGlass), RoundedCornerShape(16.dp))
                        .padding(16.dp)
                ) {
                    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column {
                                Text("Maximum Stored Sessions", fontSize = 14.sp, fontWeight = FontWeight.SemiBold, color = tokens.textPrimary)
                                Text("Limit the number of saved sessions", fontSize = 11.sp, color = tokens.textSecondary)
                            }
                            Box(
                                modifier = Modifier
                                    .clip(RoundedCornerShape(12.dp))
                                    .background(tokens.accentViolet.copy(alpha = 0.2f))
                                    .padding(horizontal = 10.dp, vertical = 4.dp)
                            ) {
                                Text(
                                    text = "${prefs.maxStoredSessions} max",
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = tokens.accentViolet
                                )
                            }
                        }

                        Slider(
                            value = prefs.maxStoredSessions.toFloat(),
                            onValueChange = { newVal ->
                                app.preferencesManager.updateMaxStoredSessions(newVal.toInt().coerceIn(1, 20))
                            },
                            valueRange = 1f..20f,
                            steps = 18,
                            colors = SliderDefaults.colors(
                                thumbColor = tokens.accentViolet,
                                activeTrackColor = tokens.accentViolet,
                                inactiveTrackColor = Color(0x33FFFFFF)
                            ),
                            modifier = Modifier.testTag("slider_max_sessions")
                        )
                    }
                }
            }

            // Reset Current Transcript
            item {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(16.dp))
                        .background(tokens.surfaceGlass)
                        .border(BorderStroke(0.5.dp, Color(0x33FF5252)), RoundedCornerShape(16.dp))
                        .padding(16.dp)
                ) {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text(
                            text = "Reset Current Session",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = tokens.textPrimary
                        )
                        Text(
                            text = "Stops active recording and clears the current transcript.",
                            fontSize = 12.sp,
                            color = tokens.textSecondary
                        )

                        OutlinedButton(
                            onClick = {
                                app.hardReset()
                                Toast.makeText(context, "Session reset", Toast.LENGTH_SHORT).show()
                            },
                            colors = ButtonDefaults.outlinedButtonColors(contentColor = Color(0xFFFF8A80)),
                            border = BorderStroke(1.dp, Color(0x66FF5252)),
                            shape = RoundedCornerShape(12.dp),
                            modifier = Modifier.fillMaxWidth().testTag("btn_hard_reset")
                        ) {
                            Text("Reset Session", fontSize = 13.sp, fontWeight = FontWeight.Medium)
                        }
                    }
                }
            }
        }

        // New Session Dialog
        if (showNewSessionDialog) {
            AlertDialog(
                onDismissRequest = { showNewSessionDialog = false },
                title = { Text("New Session", color = tokens.textPrimary) },
                text = {
                    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        Text(
                            "Enter a title for your new dictation session, or leave blank to auto-number.",
                            fontSize = 13.sp,
                            color = tokens.textSecondary
                        )
                        OutlinedTextField(
                            value = newSessionTitleInput,
                            onValueChange = { newSessionTitleInput = it },
                            placeholder = { Text("e.g. Meeting Notes, Quick Idea", color = tokens.textSecondary.copy(alpha = 0.5f)) },
                            singleLine = true,
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = tokens.accentViolet,
                                unfocusedBorderColor = tokens.borderGlass,
                                focusedTextColor = tokens.textPrimary,
                                unfocusedTextColor = tokens.textPrimary
                            ),
                            shape = RoundedCornerShape(12.dp),
                            modifier = Modifier.fillMaxWidth().testTag("input_new_session_title")
                        )
                    }
                },
                confirmButton = {
                    Button(
                        onClick = {
                            app.createNewSession(newSessionTitleInput.trim())
                            showNewSessionDialog = false
                            onOpenSessionInEditor()
                            Toast.makeText(context, "New session created", Toast.LENGTH_SHORT).show()
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = tokens.accentViolet)
                    ) {
                        Text("Create", color = Color.White)
                    }
                },
                dismissButton = {
                    TextButton(onClick = { showNewSessionDialog = false }) {
                        Text("Cancel", color = tokens.textSecondary)
                    }
                },
                containerColor = tokens.bgCard
            )
        }

        // Clear History Confirm Dialog
        if (showDeleteAllConfirmDialog) {
            AlertDialog(
                onDismissRequest = { showDeleteAllConfirmDialog = false },
                title = { Text("Clear All Sessions?", color = tokens.textPrimary) },
                text = {
                    Text(
                        "Are you sure you want to delete all saved sessions? This will clear your saved history.",
                        fontSize = 13.sp,
                        color = tokens.textSecondary
                    )
                },
                confirmButton = {
                    Button(
                        onClick = {
                            app.clearAllSessions()
                            showDeleteAllConfirmDialog = false
                            Toast.makeText(context, "History cleared", Toast.LENGTH_SHORT).show()
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFFF5252))
                    ) {
                        Text("Delete All", color = Color.White)
                    }
                },
                dismissButton = {
                    TextButton(onClick = { showDeleteAllConfirmDialog = false }) {
                        Text("Cancel", color = tokens.textSecondary)
                    }
                },
                containerColor = tokens.bgCard
            )
        }
    }
}

@Composable
private fun SessionItemCard(
    session: LiveSessionData,
    isActive: Boolean,
    formattedDate: String,
    onSelect: () -> Unit,
    onCopy: () -> Unit,
    onDelete: () -> Unit
) {
    val tokens = LocalGlassTokens.current
    val borderCol = if (isActive) tokens.accentViolet else tokens.borderGlass
    val bgCol = if (isActive) Color(0x22663AF3) else tokens.surfaceGlass

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(16.dp))
            .background(bgCol)
            .border(BorderStroke(if (isActive) 1.dp else 0.5.dp, borderCol), RoundedCornerShape(16.dp))
            .clickable(onClick = onSelect)
            .padding(16.dp)
    ) {
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(
                        text = session.title,
                        fontSize = 15.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = tokens.textPrimary,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                    if (isActive) {
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(6.dp))
                                .background(Color(0x3300E676))
                                .padding(horizontal = 6.dp, vertical = 2.dp)
                        ) {
                            Text("Active", fontSize = 10.sp, color = Color(0xFF00E676), fontWeight = FontWeight.Bold)
                        }
                    }
                }

                Text(
                    text = formattedDate,
                    fontSize = 11.sp,
                    color = tokens.textSecondary
                )
            }

            Text(
                text = if (session.transcript.isNotBlank()) session.transcript else "Empty transcript (tap to open and dictate)",
                fontSize = 13.sp,
                color = tokens.textSecondary,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                val words = if (session.transcript.isBlank()) 0
                else session.transcript.trim().split("\\s+".toRegex()).size

                Row(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = "$words words",
                        fontSize = 11.sp,
                        color = tokens.textSecondary
                    )
                    Text("•", fontSize = 11.sp, color = tokens.textSecondary)
                    Text(
                        text = "${session.transcript.length} chars",
                        fontSize = 11.sp,
                        color = tokens.textSecondary
                    )
                }

                Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                    IconButton(onClick = onCopy, modifier = Modifier.size(32.dp)) {
                        LucideCopy(tint = tokens.textSecondary, size = 16.dp)
                    }
                    IconButton(onClick = onDelete, modifier = Modifier.size(32.dp)) {
                        LucideClose(tint = Color(0xFFFF8A80), size = 16.dp)
                    }
                }
            }
        }
    }
}
