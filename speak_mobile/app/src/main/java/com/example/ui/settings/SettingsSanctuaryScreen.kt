package com.example.ui.settings

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.model.CapsulePreferences
import com.example.data.model.QuickActionType
import com.example.ui.components.GlassCard
import com.example.ui.components.LucideSparkles
import com.example.ui.theme.CapsuleThemeMode
import com.example.ui.theme.LocalGlassTokens
import com.example.ui.theme.PrecisionCyan

@Composable
fun SettingsSanctuaryScreen(
    preferences: CapsulePreferences,
    onUpdatePreferences: (CapsulePreferences) -> Unit,
    onReplayOnboarding: () -> Unit,
    isOverlayPermissionGranted: Boolean = false,
    isAccessibilityActive: Boolean = false,
    onLaunchOverlayPermission: () -> Unit = {},
    onLaunchAccessibilitySettings: () -> Unit = {},
    onRequestScreenCapture: () -> Unit = {},
    modifier: Modifier = Modifier
) {
    val tokens = LocalGlassTokens.current

    var customPrompt by remember { mutableStateOf(preferences.customSystemPrompt) }
    var lexiconRaw by remember { mutableStateOf(preferences.customLexicon.joinToString(", ")) }

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
            contentPadding = PaddingValues(top = 20.dp, bottom = 120.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Header
            item {
                Text(
                    text = "Settings",
                    style = MaterialTheme.typography.headlineLarge,
                    color = tokens.textPrimary
                )
                Text(
                    text = "Configure transcription preferences and AI controls.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = tokens.textSecondary
                )
            }

            // Cross-Platform Banner
            item {
                GlassCard(modifier = Modifier.fillMaxWidth()) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = "Speak for PC",
                                style = MaterialTheme.typography.titleMedium,
                                color = tokens.textPrimary
                            )
                            Spacer(modifier = Modifier.height(2.dp))
                            Text(
                                text = "Speak v2.0 is also available on Windows and macOS with instant global voice shortcuts.",
                                style = MaterialTheme.typography.bodySmall,
                                color = tokens.textSecondary
                            )
                        }
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(8.dp))
                                .background(Color(0x22FFFFFF))
                                .padding(horizontal = 10.dp, vertical = 6.dp)
                        ) {
                            Text(
                                text = "v2.0",
                                color = PrecisionCyan,
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                }
            }

            // Universal Screen Overlay (Always On Top)
            item {
                Text(
                    text = "Universal Screen Overlay (Always On Top)",
                    style = MaterialTheme.typography.titleMedium,
                    color = tokens.textPrimary
                )
            }

            item {
                GlassCard(modifier = Modifier.fillMaxWidth()) {
                    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                                ) {
                                    Text(
                                        text = "Display Over Other Apps",
                                        style = MaterialTheme.typography.titleSmall,
                                        color = tokens.textPrimary
                                    )
                                    Box(
                                        modifier = Modifier
                                            .clip(RoundedCornerShape(6.dp))
                                            .background(
                                                if (isOverlayPermissionGranted) Color(0x2222C55E) else Color(0x22F59E0B)
                                            )
                                            .border(
                                                BorderStroke(
                                                    0.5.dp,
                                                    if (isOverlayPermissionGranted) Color(0xFF22C55E) else Color(0xFFF59E0B)
                                                ),
                                                RoundedCornerShape(6.dp)
                                            )
                                            .padding(horizontal = 6.dp, vertical = 2.dp)
                                    ) {
                                        Text(
                                            text = if (isOverlayPermissionGranted) "Granted" else "Requires Permission",
                                            color = if (isOverlayPermissionGranted) Color(0xFF4ADE80) else Color(0xFFFBBF24),
                                            fontSize = 10.sp,
                                            fontWeight = FontWeight.SemiBold
                                        )
                                    }
                                }
                                Spacer(modifier = Modifier.height(2.dp))
                                Text(
                                    text = "Float Speak's intelligent capsule anywhere on screen over WhatsApp, Gmail, Chrome, Slack, or any app.",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = tokens.textSecondary
                                )
                            }

                            Switch(
                                checked = preferences.drawOverOtherAppsEnabled,
                                onCheckedChange = { enabled ->
                                    onUpdatePreferences(preferences.copy(drawOverOtherAppsEnabled = enabled))
                                    if (enabled && !isOverlayPermissionGranted) {
                                        onLaunchOverlayPermission()
                                    }
                                },
                                colors = SwitchDefaults.colors(
                                    checkedThumbColor = Color.White,
                                    checkedTrackColor = tokens.accentViolet
                                ),
                                modifier = Modifier.testTag("draw_over_other_apps_switch")
                            )
                        }

                        if (!isOverlayPermissionGranted) {
                            Button(
                                onClick = onLaunchOverlayPermission,
                                colors = ButtonDefaults.buttonColors(containerColor = Color(0x33F59E0B)),
                                border = BorderStroke(1.dp, Color(0xFFF59E0B)),
                                shape = RoundedCornerShape(8.dp),
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .testTag("grant_overlay_permission_button")
                            ) {
                                Text("Grant Overlay Permission in Settings", color = Color(0xFFFBBF24), fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
                            }
                        }
                    }
                }
            }

            // Auto-Open While Typing Across Apps
            item {
                Text(
                    text = "Auto-Open While Typing Across Apps",
                    style = MaterialTheme.typography.titleMedium,
                    color = tokens.textPrimary
                )
            }

            item {
                GlassCard(modifier = Modifier.fillMaxWidth()) {
                    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                                ) {
                                    Text(
                                        text = "Auto-Summon When Typing",
                                        style = MaterialTheme.typography.titleSmall,
                                        color = tokens.textPrimary
                                    )
                                    Box(
                                        modifier = Modifier
                                            .clip(RoundedCornerShape(6.dp))
                                            .background(
                                                if (isAccessibilityActive) Color(0x2222C55E) else Color(0x22F59E0B)
                                            )
                                            .border(
                                                BorderStroke(
                                                    0.5.dp,
                                                    if (isAccessibilityActive) Color(0xFF22C55E) else Color(0xFFF59E0B)
                                                ),
                                                RoundedCornerShape(6.dp)
                                            )
                                            .padding(horizontal = 6.dp, vertical = 2.dp)
                                    ) {
                                        Text(
                                            text = if (isAccessibilityActive) "Service Active" else "Setup Needed",
                                            color = if (isAccessibilityActive) Color(0xFF4ADE80) else Color(0xFFFBBF24),
                                            fontSize = 10.sp,
                                            fontWeight = FontWeight.SemiBold
                                        )
                                    }
                                }
                                Spacer(modifier = Modifier.height(2.dp))
                                Text(
                                    text = "Automatically opens or expands the floating capsule whenever you tap into an input field or text box in any app.",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = tokens.textSecondary
                                )
                            }

                            Switch(
                                checked = preferences.autoOpenOnTypingEnabled,
                                onCheckedChange = { enabled ->
                                    onUpdatePreferences(preferences.copy(autoOpenOnTypingEnabled = enabled))
                                    if (enabled && !isAccessibilityActive) {
                                        onLaunchAccessibilitySettings()
                                    }
                                },
                                colors = SwitchDefaults.colors(
                                    checkedThumbColor = Color.White,
                                    checkedTrackColor = tokens.accentViolet
                                ),
                                modifier = Modifier.testTag("auto_open_typing_switch")
                            )
                        }

                        if (!isAccessibilityActive) {
                            Button(
                                onClick = onLaunchAccessibilitySettings,
                                colors = ButtonDefaults.buttonColors(containerColor = Color(0x22FFFFFF)),
                                border = BorderStroke(0.5.dp, Color(0x44FFFFFF)),
                                shape = RoundedCornerShape(8.dp),
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .testTag("open_accessibility_settings_button")
                            ) {
                                Text("Enable Speak in Android Accessibility Settings", color = Color.White, fontSize = 12.sp)
                            }
                        }

                        HorizontalDivider(color = Color(0x1AFFFFFF), thickness = 0.5.dp)

                        // Direct Text Insertion
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = "Direct Text Insertion",
                                    style = MaterialTheme.typography.titleSmall,
                                    color = tokens.textPrimary
                                )
                                Text(
                                    text = "Automatically paste refined speech directly into the active text field.",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = tokens.textSecondary
                                )
                            }
                            Switch(
                                checked = preferences.autoInsertTextEnabled,
                                onCheckedChange = { enabled ->
                                    onUpdatePreferences(preferences.copy(autoInsertTextEnabled = enabled))
                                },
                                colors = SwitchDefaults.colors(
                                    checkedThumbColor = Color.White,
                                    checkedTrackColor = tokens.accentViolet
                                ),
                                modifier = Modifier.testTag("auto_insert_text_switch")
                            )
                        }
                    }
                }
            }

            // Live Screen Share & Visual Assistant Settings
            item {
                Text(
                    text = "Live Screen Share & Visual Assistant",
                    style = MaterialTheme.typography.titleMedium,
                    color = tokens.textPrimary
                )
            }

            item {
                GlassCard(modifier = Modifier.fillMaxWidth()) {
                    Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                                ) {
                                    Text(
                                        text = "Live Screen Context",
                                        style = MaterialTheme.typography.titleSmall,
                                        color = tokens.textPrimary
                                    )
                                    Box(
                                        modifier = Modifier
                                            .clip(RoundedCornerShape(6.dp))
                                            .background(
                                                if (preferences.screenShareVisionActive) Color(0x2200FFFF) else Color(0x14FFFFFF)
                                            )
                                            .border(
                                                BorderStroke(
                                                    0.5.dp,
                                                    if (preferences.screenShareVisionActive) PrecisionCyan else Color(0x33FFFFFF)
                                                ),
                                                RoundedCornerShape(6.dp)
                                            )
                                            .padding(horizontal = 6.dp, vertical = 2.dp)
                                    ) {
                                        Text(
                                            text = if (preferences.screenShareVisionActive) "Vision Active" else "Off",
                                            color = if (preferences.screenShareVisionActive) PrecisionCyan else Color(0xFFA1A1AA),
                                            fontSize = 10.sp,
                                            fontWeight = FontWeight.SemiBold
                                        )
                                    }
                                }
                                Spacer(modifier = Modifier.height(2.dp))
                                Text(
                                    text = "Allows Gemini 3.1 Flash Live to observe active screen context in real-time to provide vision-aware dictation and intelligent contextual auto-fill.",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = tokens.textSecondary
                                )
                            }

                            Switch(
                                checked = preferences.screenShareVisionActive,
                                onCheckedChange = { active ->
                                    onUpdatePreferences(preferences.copy(screenShareVisionActive = active))
                                    if (active) {
                                        onRequestScreenCapture()
                                    }
                                },
                                colors = SwitchDefaults.colors(
                                    checkedThumbColor = Color.White,
                                    checkedTrackColor = tokens.accentViolet
                                ),
                                modifier = Modifier.testTag("screen_share_vision_switch")
                            )
                        }

                        Button(
                            onClick = onRequestScreenCapture,
                            colors = ButtonDefaults.buttonColors(containerColor = Color(0x1A00FFFF)),
                            border = BorderStroke(0.5.dp, Color(0x6600FFFF)),
                            shape = RoundedCornerShape(8.dp),
                            modifier = Modifier
                                .fillMaxWidth()
                                .testTag("test_screen_capture_button")
                        ) {
                            Text("Request / Verify Screen Capture Intent", color = PrecisionCyan, fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
                        }

                        HorizontalDivider(color = Color(0x1AFFFFFF), thickness = 0.5.dp)

                        // Frame Rate Selector
                        Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                            Text(
                                text = "Vision Stream Refresh Rate",
                                style = MaterialTheme.typography.titleSmall,
                                color = tokens.textPrimary
                            )
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                listOf(1 to "1 FPS (Saver)", 2 to "2 FPS (Balanced)", 5 to "5 FPS (Precision)").forEach { (fps, label) ->
                                    val isSelected = preferences.screenShareFps == fps
                                    Box(
                                        modifier = Modifier
                                            .weight(1f)
                                            .clip(RoundedCornerShape(8.dp))
                                            .background(if (isSelected) Color(0x3300FFFF) else Color(0x14FFFFFF))
                                            .border(
                                                BorderStroke(
                                                    if (isSelected) 1.dp else 0.5.dp,
                                                    if (isSelected) PrecisionCyan else Color(0x33FFFFFF)
                                                ),
                                                RoundedCornerShape(8.dp)
                                            )
                                            .clickable {
                                                onUpdatePreferences(preferences.copy(screenShareFps = fps))
                                            }
                                            .padding(vertical = 8.dp),
                                        contentAlignment = Alignment.Center
                                    ) {
                                        Text(
                                            text = label,
                                            fontSize = 11.sp,
                                            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
                                            color = if (isSelected) Color.White else tokens.textSecondary
                                        )
                                    }
                                }
                            }
                        }

                        // Capture Resolution Selector
                        Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                            Text(
                                text = "Capture Resolution",
                                style = MaterialTheme.typography.titleSmall,
                                color = tokens.textPrimary
                            )
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                listOf("480p" to "480p (Fast)", "720p" to "720p (HD)", "1080p" to "1080p (Crisp)").forEach { (qual, label) ->
                                    val isSelected = preferences.screenShareQuality == qual
                                    Box(
                                        modifier = Modifier
                                            .weight(1f)
                                            .clip(RoundedCornerShape(8.dp))
                                            .background(if (isSelected) Color(0x3300FFFF) else Color(0x14FFFFFF))
                                            .border(
                                                BorderStroke(
                                                    if (isSelected) 1.dp else 0.5.dp,
                                                    if (isSelected) PrecisionCyan else Color(0x33FFFFFF)
                                                ),
                                                RoundedCornerShape(8.dp)
                                            )
                                            .clickable {
                                                onUpdatePreferences(preferences.copy(screenShareQuality = qual))
                                            }
                                            .padding(vertical = 8.dp),
                                        contentAlignment = Alignment.Center
                                    ) {
                                        Text(
                                            text = label,
                                            fontSize = 11.sp,
                                            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
                                            color = if (isSelected) Color.White else tokens.textSecondary
                                        )
                                    }
                                }
                            }
                        }

                        // Privacy Shield Masking
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = "Privacy Shield",
                                    style = MaterialTheme.typography.titleSmall,
                                    color = tokens.textPrimary
                                )
                                Text(
                                    text = "Automatically pauses screen vision when password fields or secure apps are detected.",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = tokens.textSecondary
                                )
                            }
                            Switch(
                                checked = preferences.screenSharePrivacyMask,
                                onCheckedChange = { mask ->
                                    onUpdatePreferences(preferences.copy(screenSharePrivacyMask = mask))
                                },
                                colors = SwitchDefaults.colors(
                                    checkedThumbColor = Color.White,
                                    checkedTrackColor = tokens.accentViolet
                                ),
                                modifier = Modifier.testTag("screen_share_privacy_switch")
                            )
                        }
                    }
                }
            }

            // AI Model Architecture & Engine Specs
            item {
                Text(
                    text = "AI Model Engine Architecture",
                    style = MaterialTheme.typography.titleMedium,
                    color = tokens.textPrimary
                )
            }

            item {
                GlassCard(modifier = Modifier.fillMaxWidth()) {
                    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        ModelSpecRow(
                            feature = "Live Voice Transcription",
                            model = com.example.data.api.GeminiModels.TRANSCRIBE_LIVE,
                            detail = "16kHz 16-bit Mono PCM Streaming (gemini-3.5-transcribe-live)",
                            tokens = tokens
                        )
                        HorizontalDivider(color = Color(0x1AFFFFFF), thickness = 0.5.dp)
                        ModelSpecRow(
                            feature = "Live Voice Talkback (Audio In/Out)",
                            model = com.example.data.api.GeminiModels.VOICE_TALKBACK,
                            detail = "Native Low-Latency Audio PCM Talkback (gemini-3.1-flash-live)",
                            tokens = tokens
                        )
                        HorizontalDivider(color = Color(0x1AFFFFFF), thickness = 0.5.dp)
                        ModelSpecRow(
                            feature = "Smart Transform Primary",
                            model = com.example.data.api.GeminiModels.TRANSFORM_PRIMARY,
                            detail = "Surgical In-Place Voice Refinement (gemini-3.5-flash-lite)",
                            tokens = tokens
                        )
                        HorizontalDivider(color = Color(0x1AFFFFFF), thickness = 0.5.dp)
                        ModelSpecRow(
                            feature = "Smart Transform Fallback",
                            model = com.example.data.api.GeminiModels.TRANSFORM_FALLBACK,
                            detail = "High-Speed Automated Fallback Engine (gemini-3.1-flash-lite)",
                            tokens = tokens
                        )
                    }
                }
            }

            // Gemini API Key Management
            item {
                Text(
                    text = "Gemini API Key",
                    style = MaterialTheme.typography.titleMedium,
                    color = tokens.textPrimary
                )
            }

            item {
                var apiKeyInput by remember { mutableStateOf(preferences.customApiKey) }
                val hasBuildConfigKey = com.example.BuildConfig.GEMINI_API_KEY.isNotBlank()

                GlassCard(modifier = Modifier.fillMaxWidth()) {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = "API Key Configuration",
                                style = MaterialTheme.typography.titleSmall,
                                color = tokens.textPrimary
                            )
                            Box(
                                modifier = Modifier
                                    .clip(RoundedCornerShape(6.dp))
                                    .background(if (apiKeyInput.isNotBlank() || hasBuildConfigKey) Color(0x2210B981) else Color(0x22EF4444))
                                    .padding(horizontal = 8.dp, vertical = 2.dp)
                            ) {
                                Text(
                                    text = if (apiKeyInput.isNotBlank()) "Custom Key Active" else if (hasBuildConfigKey) "Environment Key Active" else "No Key Set",
                                    color = if (apiKeyInput.isNotBlank() || hasBuildConfigKey) Color(0xFF10B981) else Color(0xFFEF4444),
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Medium
                                )
                            }
                        }

                        Text(
                            text = "Add your personal Google Gemini API key to use your own quota, or leave blank to use the secure default.",
                            style = MaterialTheme.typography.bodySmall,
                            color = tokens.textSecondary
                        )

                        OutlinedTextField(
                            value = apiKeyInput,
                            onValueChange = {
                                apiKeyInput = it.trim()
                                onUpdatePreferences(preferences.copy(customApiKey = it.trim()))
                            },
                            modifier = Modifier
                                .fillMaxWidth()
                                .testTag("custom_api_key_input"),
                            placeholder = { Text("AIzaSy... (optional)", color = tokens.textSecondary) },
                            singleLine = true,
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedTextColor = tokens.textPrimary,
                                unfocusedTextColor = tokens.textPrimary,
                                focusedBorderColor = Color.White,
                                unfocusedBorderColor = Color(0x33FFFFFF)
                            ),
                            shape = RoundedCornerShape(12.dp)
                        )
                    }
                }
            }

            // Visual Theme Selection
            item {
                Text(
                    text = "Appearance",
                    style = MaterialTheme.typography.titleMedium,
                    color = tokens.textPrimary
                )
            }

            item {
                GlassCard(modifier = Modifier.fillMaxWidth()) {
                    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        CapsuleThemeMode.entries.forEach { mode ->
                            val isSelected = preferences.themeMode == mode.name
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clip(RoundedCornerShape(12.dp))
                                    .background(if (isSelected) Color(0x22FFFFFF) else Color.Transparent)
                                    .clickable {
                                        onUpdatePreferences(preferences.copy(themeMode = mode.name))
                                    }
                                    .padding(horizontal = 14.dp, vertical = 12.dp)
                                    .testTag("theme_option_${mode.name}"),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Column {
                                    Text(
                                        text = mode.title,
                                        style = MaterialTheme.typography.titleSmall,
                                        color = if (isSelected) Color.White else tokens.textPrimary
                                    )
                                    Text(
                                        text = mode.description,
                                        style = MaterialTheme.typography.bodySmall,
                                        color = tokens.textSecondary
                                    )
                                }
                                if (isSelected) {
                                    Box(
                                        modifier = Modifier
                                            .size(10.dp)
                                            .clip(CircleShape)
                                            .background(Color.White)
                                    )
                                }
                            }
                        }
                    }
                }
            }

            // Capsule Far-Right Action
            item {
                Text(
                    text = "Default Capsule Action",
                    style = MaterialTheme.typography.titleMedium,
                    color = tokens.textPrimary
                )
            }

            item {
                GlassCard(modifier = Modifier.fillMaxWidth()) {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        QuickActionType.entries.forEach { action ->
                            val isSelected = preferences.farRightAction == action
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clip(RoundedCornerShape(10.dp))
                                    .background(if (isSelected) Color(0x22FFFFFF) else Color.Transparent)
                                    .clickable {
                                        onUpdatePreferences(preferences.copy(farRightAction = action))
                                    }
                                    .padding(horizontal = 12.dp, vertical = 10.dp)
                                    .testTag("setting_action_${action.id}"),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Column(modifier = Modifier.weight(1f)) {
                                    Text(
                                        text = action.label,
                                        style = MaterialTheme.typography.titleSmall,
                                        color = tokens.textPrimary
                                    )
                                    Text(
                                        text = action.description,
                                        style = MaterialTheme.typography.bodySmall,
                                        color = tokens.textSecondary
                                    )
                                }
                                if (isSelected) {
                                    Box(
                                        modifier = Modifier
                                            .size(8.dp)
                                            .clip(CircleShape)
                                            .background(Color.White)
                                    )
                                }
                            }
                        }
                    }
                }
            }

            // Custom Lexicon
            item {
                Text(
                    text = "Custom Vocabulary",
                    style = MaterialTheme.typography.titleMedium,
                    color = tokens.textPrimary
                )
            }

            item {
                GlassCard(modifier = Modifier.fillMaxWidth()) {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text(
                            text = "Names, acronyms, and technical terms to prioritize:",
                            style = MaterialTheme.typography.bodySmall,
                            color = tokens.textSecondary
                        )
                        OutlinedTextField(
                            value = lexiconRaw,
                            onValueChange = {
                                lexiconRaw = it
                                val list = it.split(",").map { item -> item.trim() }.filter { item -> item.isNotBlank() }
                                onUpdatePreferences(preferences.copy(customLexicon = list))
                            },
                            modifier = Modifier.fillMaxWidth(),
                            placeholder = { Text("Gemini, Kotlin, Speak, API...", color = tokens.textSecondary) },
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedTextColor = tokens.textPrimary,
                                unfocusedTextColor = tokens.textPrimary,
                                focusedBorderColor = Color.White,
                                unfocusedBorderColor = Color(0x33FFFFFF)
                            ),
                            shape = RoundedCornerShape(12.dp)
                        )
                    }
                }
            }

            // Global System Prompt
            item {
                Text(
                    text = "AI System Prompt",
                    style = MaterialTheme.typography.titleMedium,
                    color = tokens.textPrimary
                )
            }

            item {
                GlassCard(modifier = Modifier.fillMaxWidth()) {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        OutlinedTextField(
                            value = customPrompt,
                            onValueChange = {
                                customPrompt = it
                                onUpdatePreferences(preferences.copy(customSystemPrompt = it))
                            },
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(110.dp),
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedTextColor = tokens.textPrimary,
                                unfocusedTextColor = tokens.textPrimary,
                                focusedBorderColor = Color.White,
                                unfocusedBorderColor = Color(0x33FFFFFF)
                            ),
                            shape = RoundedCornerShape(12.dp)
                        )
                    }
                }
            }

            // Custom Refine Actions Builder
            item {
                Text(
                    text = "Custom Refine Actions",
                    style = MaterialTheme.typography.titleMedium,
                    color = tokens.textPrimary
                )
            }

            item {
                var showAddActionDialog by remember { mutableStateOf(false) }
                var newActionName by remember { mutableStateOf("") }
                var newActionPrompt by remember { mutableStateOf("") }

                GlassCard(modifier = Modifier.fillMaxWidth()) {
                    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column {
                                Text("Personalized Rewrite Prompts", style = MaterialTheme.typography.titleSmall, color = tokens.textPrimary)
                                Text("Custom quick-chips available in Speak & Editor", style = MaterialTheme.typography.bodySmall, color = tokens.textSecondary)
                            }
                            Button(
                                onClick = { showAddActionDialog = true },
                                colors = ButtonDefaults.buttonColors(containerColor = tokens.accentViolet),
                                shape = RoundedCornerShape(16.dp),
                                contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp)
                            ) {
                                Text("+ Add", fontSize = 12.sp)
                            }
                        }

                        if (preferences.customActions.isEmpty()) {
                            Text(
                                text = "No custom actions created yet. Add one like 'Bullet Points' or 'Slack TL;DR'.",
                                fontSize = 12.sp,
                                color = tokens.textSecondary
                            )
                        } else {
                                preferences.customActions.forEach { action ->
                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .clip(RoundedCornerShape(10.dp))
                                        .background(Color(0x1AFFFFFF))
                                        .padding(horizontal = 12.dp, vertical = 8.dp),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Column(modifier = Modifier.weight(1f)) {
                                        Text(action.name, fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = tokens.textPrimary)
                                        Text(action.prompt, fontSize = 11.sp, color = tokens.textSecondary, maxLines = 1)
                                    }
                                    IconButton(
                                        onClick = {
                                            val updatedList = preferences.customActions.filter { it.id != action.id }
                                            onUpdatePreferences(preferences.copy(customActions = updatedList))
                                        },
                                        modifier = Modifier.size(28.dp)
                                    ) {
                                        Text("✕", color = Color(0xFFFF8A80), fontSize = 12.sp)
                                    }
                                }
                            }
                        }

                        if (showAddActionDialog) {
                            AlertDialog(
                                onDismissRequest = { showAddActionDialog = false },
                                title = { Text("New Custom Action", color = tokens.textPrimary) },
                                text = {
                                    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                                        OutlinedTextField(
                                            value = newActionName,
                                            onValueChange = { newActionName = it },
                                            label = { Text("Action Name (e.g. Bullet Points)") },
                                            singleLine = true,
                                            modifier = Modifier.fillMaxWidth()
                                        )
                                        OutlinedTextField(
                                            value = newActionPrompt,
                                            onValueChange = { newActionPrompt = it },
                                            label = { Text("Instruction Prompt") },
                                            placeholder = { Text("Transform text into crisp markdown bullet points...") },
                                            modifier = Modifier.fillMaxWidth().height(100.dp)
                                        )
                                    }
                                },
                                confirmButton = {
                                    Button(
                                        onClick = {
                                            if (newActionName.isNotBlank() && newActionPrompt.isNotBlank()) {
                                                val newAction = com.example.data.model.CustomRefineAction(
                                                    id = "custom_${System.currentTimeMillis()}",
                                                    name = newActionName.trim(),
                                                    voiceTrigger = newActionName.trim().lowercase().replace("\\s+".toRegex(), "_"),
                                                    prompt = newActionPrompt.trim(),
                                                    enabled = true
                                                )
                                                onUpdatePreferences(preferences.copy(customActions = preferences.customActions + newAction))
                                                newActionName = ""
                                                newActionPrompt = ""
                                                showAddActionDialog = false
                                            }
                                        },
                                        colors = ButtonDefaults.buttonColors(containerColor = tokens.accentViolet)
                                    ) {
                                        Text("Save")
                                    }
                                },
                                dismissButton = {
                                    TextButton(onClick = { showAddActionDialog = false }) {
                                        Text("Cancel")
                                    }
                                },
                                containerColor = tokens.bgCard
                            )
                        }
                    }
                }
            }

            // Temperature & Creativity Control
            item {
                Text(
                    text = "Refinement Creativity (Temperature)",
                    style = MaterialTheme.typography.titleMedium,
                    color = tokens.textPrimary
                )
            }

            item {
                GlassCard(modifier = Modifier.fillMaxWidth()) {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text("Model Temperature", style = MaterialTheme.typography.titleSmall, color = tokens.textPrimary)
                            Text(String.format("%.2f", preferences.temperature), fontSize = 13.sp, fontWeight = FontWeight.Bold, color = tokens.accentViolet)
                        }
                        Slider(
                            value = preferences.temperature,
                            onValueChange = { newVal ->
                                onUpdatePreferences(preferences.copy(temperature = newVal))
                            },
                            valueRange = 0.0f..1.0f,
                            colors = SliderDefaults.colors(
                                thumbColor = tokens.accentViolet,
                                activeTrackColor = tokens.accentViolet,
                                inactiveTrackColor = Color(0x33FFFFFF)
                            )
                        )
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text("0.0 (Strict / Deterministic)", fontSize = 10.sp, color = tokens.textSecondary)
                            Text("1.0 (Creative)", fontSize = 10.sp, color = tokens.textSecondary)
                        }
                    }
                }
            }

            // Custom Signature Mark & Verification Mode
            item {
                Text(
                    text = "Signature & Verification",
                    style = MaterialTheme.typography.titleMedium,
                    color = tokens.textPrimary
                )
            }

            item {
                GlassCard(modifier = Modifier.fillMaxWidth()) {
                    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        // Signature Mark
                        Text("Custom Signature Mark (Optional)", style = MaterialTheme.typography.titleSmall, color = tokens.textPrimary)
                        OutlinedTextField(
                            value = preferences.customSignatureMark,
                            onValueChange = { onUpdatePreferences(preferences.copy(customSignatureMark = it)) },
                            placeholder = { Text("e.g. -- Dictated with Speak", color = tokens.textSecondary) },
                            singleLine = true,
                            modifier = Modifier.fillMaxWidth(),
                            shape = RoundedCornerShape(10.dp)
                        )

                        HorizontalDivider(color = Color(0x1AFFFFFF), thickness = 0.5.dp)

                        // Verification Mode
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text("Diff Verification Mode", style = MaterialTheme.typography.titleSmall, color = tokens.textPrimary)
                                Text("Visually highlight refined modifications before applying permanently", style = MaterialTheme.typography.bodySmall, color = tokens.textSecondary)
                            }
                            Switch(
                                checked = preferences.verificationActive,
                                onCheckedChange = { onUpdatePreferences(preferences.copy(verificationActive = it)) },
                                colors = SwitchDefaults.colors(
                                    checkedThumbColor = Color.White,
                                    checkedTrackColor = tokens.accentViolet
                                )
                            )
                        }
                    }
                }
            }

            // Replay Tour Action
            item {
                GlassCard(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable(onClick = onReplayOnboarding)
                        .testTag("replay_onboarding_card")
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(
                                text = "Welcome Tour",
                                style = MaterialTheme.typography.titleMedium,
                                color = tokens.textPrimary
                            )
                            Text(
                                text = "View voice commands and permissions setup.",
                                style = MaterialTheme.typography.bodySmall,
                                color = tokens.textSecondary
                            )
                        }
                        Text(text = "View", color = Color.White, fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
                    }
                }
            }

            // Attribution & Copyright
            item {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 20.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "Speak v2.0 • Also on PC",
                        style = MaterialTheme.typography.labelSmall,
                        color = tokens.textSecondary
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "Made by Amir Bagawan",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Medium,
                        color = tokens.textPrimary,
                        modifier = Modifier.testTag("developer_attribution_text")
                    )
                }
            }
        }
    }
}

@Composable
private fun ModelSpecRow(
    feature: String,
    model: String,
    detail: String,
    tokens: com.example.ui.theme.GlassTokens
) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(3.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = feature,
                style = MaterialTheme.typography.titleSmall,
                color = tokens.textPrimary
            )
            Box(
                modifier = Modifier
                    .clip(RoundedCornerShape(6.dp))
                    .background(Color(0x1A00FFFF))
                    .border(BorderStroke(0.5.dp, Color(0x4400FFFF)), RoundedCornerShape(6.dp))
                    .padding(horizontal = 8.dp, vertical = 2.dp)
            ) {
                Text(
                    text = model,
                    color = PrecisionCyan,
                    fontSize = 11.sp,
                    fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace,
                    fontWeight = FontWeight.SemiBold
                )
            }
        }
        Text(
            text = detail,
            style = MaterialTheme.typography.bodySmall,
            color = tokens.textSecondary
        )
    }
}
