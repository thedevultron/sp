package com.example.ui.home

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.widget.Toast
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
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.BuildConfig
import com.example.data.local.TranscriptionRecord
import com.example.data.model.CapsulePreferences
import com.example.ui.components.*
import com.example.ui.theme.*
import java.text.SimpleDateFormat
import java.util.*

@Composable
fun HomeDashboardScreen(
    preferences: CapsulePreferences,
    recentTranscriptions: List<TranscriptionRecord>,
    totalWords: Int,
    isLiveConnected: Boolean,
    isRecording: Boolean,
    tokenMemoryUsage: Float,
    showInAppCapsule: Boolean,
    onToggleInAppCapsule: () -> Unit,
    onResetCapsulePosition: () -> Unit,
    onStartRecordingToggle: () -> Unit,
    onClearHistory: () -> Unit,
    onUpdateApiKey: (String) -> Unit = {},
    modifier: Modifier = Modifier
) {
    val tokens = LocalGlassTokens.current
    val context = LocalContext.current
    val dateFormat = remember { SimpleDateFormat("MMM d, h:mm a", Locale.getDefault()) }

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(tokens.background)
    ) {
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .statusBarsPadding()
                .padding(horizontal = 20.dp),
            contentPadding = PaddingValues(top = 16.dp, bottom = 120.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Header: Speak v2.0
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = "Speak",
                            style = MaterialTheme.typography.headlineLarge,
                            color = tokens.textPrimary
                        )
                        Text(
                            text = "Instant voice dictation & refinement",
                            style = MaterialTheme.typography.bodyMedium,
                            color = tokens.textSecondary
                        )
                    }

                    // Live Engine Status Pill
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(16.dp))
                            .background(if (isLiveConnected) Color(0x22FFFFFF) else Color(0x14FFFFFF))
                            .border(
                                BorderStroke(
                                    0.5.dp,
                                    if (isLiveConnected) Color.White else Color(0x33FFFFFF)
                                ),
                                RoundedCornerShape(16.dp)
                            )
                            .padding(horizontal = 12.dp, vertical = 6.dp)
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(8.dp)
                                    .clip(CircleShape)
                                    .background(if (isLiveConnected) PrecisionCyan else Color(0xFF71717A))
                            )
                            Text(
                                text = if (isLiveConnected) "Gemini Live" else "Ready",
                                color = if (isLiveConnected) Color.White else Color(0xFFA1A1AA),
                                fontSize = 11.sp,
                                fontWeight = FontWeight.SemiBold
                            )
                        }
                    }
                }
            }

            // Movable Floating Capsule Controller Card
            item {
                GlassCard(
                    modifier = Modifier.fillMaxWidth(),
                    contentPadding = 18.dp
                ) {
                    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(10.dp)
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(34.dp)
                                        .clip(CircleShape)
                                        .background(Color(0x22FFFFFF)),
                                    contentAlignment = Alignment.Center
                                ) {
                                    LucideSparkles(tint = Color.White, size = 18.dp)
                                }
                                Column {
                                    Text(
                                        text = "Floating Voice Bar",
                                        style = MaterialTheme.typography.titleMedium,
                                        color = tokens.textPrimary
                                    )
                                    Text(
                                        text = "Quick on-screen voice shortcut",
                                        style = MaterialTheme.typography.bodySmall,
                                        color = tokens.textSecondary
                                    )
                                }
                            }

                            // Switch Toggle
                            Switch(
                                checked = showInAppCapsule,
                                onCheckedChange = { onToggleInAppCapsule() },
                                colors = SwitchDefaults.colors(
                                    checkedThumbColor = Color.White,
                                    checkedTrackColor = Color(0xFF3F3F46),
                                    uncheckedThumbColor = Color(0xFFA1A1AA),
                                    uncheckedTrackColor = Color(0x22FFFFFF)
                                ),
                                modifier = Modifier.testTag("toggle_in_app_capsule_switch")
                            )
                        }

                        // Guidance and Reset Row
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(10.dp))
                                .background(Color(0x14FFFFFF))
                                .padding(horizontal = 12.dp, vertical = 8.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = "Drag handle to reposition anywhere",
                                style = MaterialTheme.typography.bodySmall,
                                color = tokens.textSecondary
                            )

                            Text(
                                text = "Reset Position",
                                color = Color.White,
                                fontSize = 12.sp,
                                fontWeight = FontWeight.SemiBold,
                                modifier = Modifier
                                    .clickable(onClick = onResetCapsulePosition)
                                    .testTag("reset_capsule_position_button")
                            )
                        }

                        // System-wide status row
                        if (preferences.drawOverOtherAppsEnabled || preferences.autoOpenOnTypingEnabled) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(8.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                if (preferences.drawOverOtherAppsEnabled) {
                                    Box(
                                        modifier = Modifier
                                            .clip(RoundedCornerShape(6.dp))
                                            .background(Color(0x2222C55E))
                                            .border(BorderStroke(0.5.dp, Color(0xFF22C55E)), RoundedCornerShape(6.dp))
                                            .padding(horizontal = 8.dp, vertical = 3.dp)
                                    ) {
                                        Text(
                                            text = "Always On Top Active",
                                            color = Color(0xFF4ADE80),
                                            fontSize = 11.sp,
                                            fontWeight = FontWeight.Medium
                                        )
                                    }
                                }
                                if (preferences.autoOpenOnTypingEnabled) {
                                    Box(
                                        modifier = Modifier
                                            .clip(RoundedCornerShape(6.dp))
                                            .background(Color(0x2200FFFF))
                                            .border(BorderStroke(0.5.dp, Color(0x6600FFFF)), RoundedCornerShape(6.dp))
                                            .padding(horizontal = 8.dp, vertical = 3.dp)
                                    ) {
                                        Text(
                                            text = "Auto-Opens When Typing",
                                            color = PrecisionCyan,
                                            fontSize = 11.sp,
                                            fontWeight = FontWeight.Medium
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // Stats Matrix Card
            item {
                GlassCard(
                    modifier = Modifier.fillMaxWidth(),
                    contentPadding = 20.dp
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        StatTile(
                            title = "Total Words",
                            value = totalWords.toString(),
                            subtitle = "Dictated"
                        )
                        StatTile(
                            title = "AI Engine",
                            value = "Gemini 3.1",
                            subtitle = "Flash Live"
                        )
                        StatTile(
                            title = "Status",
                            value = if (isRecording) "Recording" else "Ready",
                            subtitle = if (isRecording) "Listening..." else "Tap to Speak"
                        )
                    }
                }
            }

            // Dashboard Gemini API Key Card
            item {
                var dashboardApiKeyInput by remember(preferences.customApiKey) {
                    mutableStateOf(preferences.customApiKey)
                }
                var isKeyVisible by remember { mutableStateOf(false) }
                val hasBuildConfigKey = BuildConfig.GEMINI_API_KEY.isNotBlank()
                val isCustomActive = preferences.customApiKey.isNotBlank()

                GlassCard(
                    modifier = Modifier.fillMaxWidth(),
                    contentPadding = 18.dp
                ) {
                    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(10.dp)
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(34.dp)
                                        .clip(CircleShape)
                                        .background(Color(0x22FFFFFF)),
                                    contentAlignment = Alignment.Center
                                ) {
                                    LucideSparkles(tint = if (isCustomActive || hasBuildConfigKey) PrecisionCyan else Color(0xFFFBBF24), size = 18.dp)
                                }
                                Column {
                                    Text(
                                        text = "Gemini API Key",
                                        style = MaterialTheme.typography.titleMedium,
                                        color = tokens.textPrimary
                                    )
                                    Text(
                                        text = "Direct access to Gemini 3.1 Flash Live",
                                        style = MaterialTheme.typography.bodySmall,
                                        color = tokens.textSecondary
                                    )
                                }
                            }

                            // Status Badge
                            Box(
                                modifier = Modifier
                                    .clip(RoundedCornerShape(6.dp))
                                    .background(
                                        when {
                                            isCustomActive -> Color(0x2222C55E)
                                            hasBuildConfigKey -> Color(0x2200FFFF)
                                            else -> Color(0x22F59E0B)
                                        }
                                    )
                                    .border(
                                        BorderStroke(
                                            0.5.dp,
                                            when {
                                                isCustomActive -> Color(0xFF22C55E)
                                                hasBuildConfigKey -> PrecisionCyan
                                                else -> Color(0xFFF59E0B)
                                            }
                                        ),
                                        RoundedCornerShape(6.dp)
                                    )
                                    .padding(horizontal = 8.dp, vertical = 3.dp)
                            ) {
                                Text(
                                    text = when {
                                        isCustomActive -> "Custom Key Active"
                                        hasBuildConfigKey -> "Cloud Key Ready"
                                        else -> "Key Required"
                                    },
                                    color = when {
                                        isCustomActive -> Color(0xFF4ADE80)
                                        hasBuildConfigKey -> PrecisionCyan
                                        else -> Color(0xFFFBBF24)
                                    },
                                    fontSize = 10.sp,
                                    fontWeight = FontWeight.SemiBold
                                )
                            }
                        }

                        Text(
                            text = "Enter your Google Gemini API key to activate real-time voice refinement and live streaming. Key is stored securely on device.",
                            style = MaterialTheme.typography.bodySmall,
                            color = tokens.textSecondary
                        )

                        OutlinedTextField(
                            value = dashboardApiKeyInput,
                            onValueChange = { dashboardApiKeyInput = it },
                            modifier = Modifier
                                .fillMaxWidth()
                                .testTag("dashboard_api_key_input"),
                            placeholder = {
                                Text(
                                    text = if (hasBuildConfigKey) "Using environment key (or enter custom key)" else "AIzaSy...",
                                    color = tokens.textSecondary,
                                    fontSize = 13.sp
                                )
                            },
                            singleLine = true,
                            visualTransformation = if (isKeyVisible) VisualTransformation.None else PasswordVisualTransformation(),
                            trailingIcon = {
                                IconButton(
                                    onClick = { isKeyVisible = !isKeyVisible },
                                    modifier = Modifier.testTag("dashboard_api_key_toggle_visibility")
                                ) {
                                    LucideEye(
                                        tint = if (isKeyVisible) Color.White else tokens.textSecondary,
                                        size = 18.dp
                                    )
                                }
                            },
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = PrecisionCyan,
                                unfocusedBorderColor = Color(0x33FFFFFF),
                                focusedTextColor = Color.White,
                                unfocusedTextColor = Color.White,
                                cursorColor = PrecisionCyan
                            ),
                            shape = RoundedCornerShape(10.dp)
                        )

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(10.dp)
                        ) {
                            Button(
                                onClick = {
                                    val trimmed = dashboardApiKeyInput.trim()
                                    onUpdateApiKey(trimmed)
                                    Toast.makeText(
                                        context,
                                        if (trimmed.isNotBlank()) "Gemini API Key saved!" else "Custom API Key cleared",
                                        Toast.LENGTH_SHORT
                                    ).show()
                                },
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = Color.White,
                                    contentColor = Color.Black
                                ),
                                shape = RoundedCornerShape(8.dp),
                                modifier = Modifier
                                    .weight(1f)
                                    .testTag("dashboard_api_key_save_button")
                            ) {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(6.dp)
                                ) {
                                    LucideCheck(tint = Color.Black, size = 16.dp)
                                    Text(
                                        text = "Save API Key",
                                        fontWeight = FontWeight.Bold,
                                        fontSize = 13.sp
                                    )
                                }
                            }

                            if (dashboardApiKeyInput.isNotBlank() || isCustomActive) {
                                OutlinedButton(
                                    onClick = {
                                        dashboardApiKeyInput = ""
                                        onUpdateApiKey("")
                                        Toast.makeText(context, "API Key cleared", Toast.LENGTH_SHORT).show()
                                    },
                                    border = BorderStroke(0.5.dp, Color(0x44FFFFFF)),
                                    shape = RoundedCornerShape(8.dp),
                                    modifier = Modifier.testTag("dashboard_api_key_clear_button")
                                ) {
                                    Text(
                                        text = "Clear",
                                        color = tokens.textSecondary,
                                        fontSize = 13.sp
                                    )
                                }
                            }
                        }
                    }
                }
            }

            // Real-Time Mic Action Card
            item {
                GlassCard(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable(onClick = onStartRecordingToggle)
                        .testTag("home_quick_mic_card"),
                    contentPadding = 18.dp
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(14.dp)
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(44.dp)
                                    .clip(CircleShape)
                                    .background(
                                        if (isRecording) Brush.linearGradient(listOf(Color(0xFFEF4444), Color(0xFFDC2626)))
                                        else Brush.linearGradient(listOf(Color(0xFF27272A), Color(0xFF18181B)))
                                    )
                                    .border(
                                        BorderStroke(1.dp, if (isRecording) Color(0xFFFF6B6B) else Color(0x44FFFFFF)),
                                        CircleShape
                                    ),
                                contentAlignment = Alignment.Center
                            ) {
                                LucideMic(tint = Color.White, size = 22.dp)
                            }

                            Column {
                                Text(
                                    text = if (isRecording) "Listening & Streaming..." else "Tap to Speak",
                                    style = MaterialTheme.typography.titleMedium,
                                    color = tokens.textPrimary
                                )
                                Text(
                                    text = if (isRecording) "Say 'Refine this' to polish text" else "Real-time dictation & refinement",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = tokens.textSecondary
                                )
                            }
                        }

                        LucideSparkles(tint = Color.White, size = 20.dp)
                    }
                }
            }

            // Recent Transcriptions Header
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Recent Transcriptions",
                        style = MaterialTheme.typography.titleLarge,
                        color = tokens.textPrimary
                    )

                    if (recentTranscriptions.isNotEmpty()) {
                        TextButton(
                            onClick = onClearHistory,
                            modifier = Modifier.testTag("clear_history_button")
                        ) {
                            Text(
                                text = "Clear History",
                                color = tokens.textSecondary,
                                fontSize = 13.sp
                            )
                        }
                    }
                }
            }

            if (recentTranscriptions.isEmpty()) {
                item {
                    GlassCard(
                        modifier = Modifier.fillMaxWidth(),
                        contentPadding = 24.dp
                    ) {
                        Column(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Text(
                                text = "No Transcriptions Yet",
                                style = MaterialTheme.typography.titleMedium,
                                color = tokens.textPrimary
                            )
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = "Tap the microphone or speak in any text field to start.",
                                style = MaterialTheme.typography.bodySmall,
                                color = tokens.textSecondary
                            )
                        }
                    }
                }
            } else {
                items(recentTranscriptions) { record ->
                    TranscriptionHistoryItem(
                        record = record,
                        formattedDate = dateFormat.format(Date(record.timestamp)),
                        tokens = tokens,
                        onCopy = { text ->
                            val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                            clipboard.setPrimaryClip(ClipData.newPlainText("Transcription", text))
                            Toast.makeText(context, "Copied to clipboard", Toast.LENGTH_SHORT).show()
                        }
                    )
                }
            }
        }
    }
}

@Composable
private fun StatTile(
    title: String,
    value: String,
    subtitle: String
) {
    val tokens = LocalGlassTokens.current
    Column {
        Text(
            text = title,
            style = MaterialTheme.typography.bodySmall,
            color = tokens.textSecondary
        )
        Spacer(modifier = Modifier.height(2.dp))
        Text(
            text = value,
            style = MaterialTheme.typography.headlineMedium,
            color = tokens.textPrimary
        )
        Text(
            text = subtitle,
            style = MaterialTheme.typography.labelSmall,
            color = tokens.textSecondary
        )
    }
}

@Composable
private fun TranscriptionHistoryItem(
    record: TranscriptionRecord,
    formattedDate: String,
    tokens: GlassTokens,
    onCopy: (String) -> Unit
) {
    val displayText = record.transformedText ?: record.originalText

    GlassCard(
        modifier = Modifier
            .fillMaxWidth()
            .testTag("history_item_${record.id}"),
        contentPadding = 16.dp
    ) {
        Column {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = formattedDate,
                    style = MaterialTheme.typography.labelSmall,
                    color = tokens.textSecondary
                )
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(8.dp))
                            .background(Color(0x22FFFFFF))
                            .padding(horizontal = 8.dp, vertical = 2.dp)
                    ) {
                        Text(
                            text = "${record.wordCount} words",
                            color = tokens.textSecondary,
                            fontSize = 10.sp
                        )
                    }

                    Text(
                        text = "Copy",
                        color = Color.White,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Medium,
                        modifier = Modifier.clickable { onCopy(displayText) }
                    )
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = displayText,
                style = MaterialTheme.typography.bodyMedium,
                color = tokens.textPrimary
            )

            if (record.transformedText != null && record.transformedText != record.originalText) {
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = "Original: ${record.originalText}",
                    style = MaterialTheme.typography.bodySmall,
                    color = tokens.textSecondary,
                    maxLines = 2
                )
            }
        }
    }
}
