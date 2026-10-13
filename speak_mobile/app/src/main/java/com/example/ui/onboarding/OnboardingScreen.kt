package com.example.ui.onboarding

import android.content.Context
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.api.GeminiModels
import com.example.data.model.CapsulePreferences
import com.example.data.model.QuickActionType
import com.example.ui.capsule.FloatingCapsuleOverlay
import com.example.ui.components.*
import com.example.ui.theme.*

@Composable
fun OnboardingScreen(
    preferences: CapsulePreferences,
    onUpdatePreferences: (CapsulePreferences) -> Unit,
    onCompleteOnboarding: () -> Unit,
    modifier: Modifier = Modifier
) {
    val tokens = LocalGlassTokens.current
    val context = LocalContext.current
    var currentStep by remember { mutableIntStateOf(0) }

    // User name & lexicon state
    var userNameInput by remember { mutableStateOf(preferences.userName) }
    var lexiconInput by remember { mutableStateOf(preferences.customLexicon.joinToString(", ")) }

    // Permission state trackers
    var hasAudioPermission by remember {
        mutableStateOf(
            androidx.core.content.ContextCompat.checkSelfPermission(
                context,
                android.Manifest.permission.RECORD_AUDIO
            ) == android.content.pm.PackageManager.PERMISSION_GRANTED
        )
    }

    val audioPermissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        hasAudioPermission = granted
    }

    // Playground text state for testing
    var playgroundText by remember {
        mutableStateOf("Um, the meeting starts at 2pm actually 3pm tomorrow, you know?")
    }

    val totalSteps = 6

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(tokens.background)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .statusBarsPadding()
                .navigationBarsPadding()
                .padding(horizontal = 20.dp, vertical = 14.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Header Progress Bar Indicator
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 10.dp),
                horizontalArrangement = Arrangement.spacedBy(6.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                for (i in 0 until totalSteps) {
                    val progressFraction by animateFloatAsState(
                        targetValue = if (i <= currentStep) 1f else 0f,
                        animationSpec = spring(dampingRatio = 0.72f, stiffness = 380f),
                        label = "onboarding_progress_$i"
                    )
                    Box(
                        modifier = Modifier
                            .weight(1f)
                            .height(4.dp)
                            .clip(RoundedCornerShape(2.dp))
                            .background(Color(0x22FFFFFF))
                    ) {
                        Box(
                            modifier = Modifier
                                .fillMaxHeight()
                                .fillMaxWidth(progressFraction)
                                .background(if (i == currentStep) PrecisionCyan else Color.White)
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Step Content
            AnimatedContent(
                targetState = currentStep,
                transitionSpec = { fadeIn() togetherWith fadeOut() },
                modifier = Modifier.weight(1f),
                label = "onboarding_step_content"
            ) { step ->
                when (step) {
                    0 -> BarHighlightingTourStep(tokens)
                    1 -> RefineAndToolsTourStep(tokens)
                    2 -> GeminiEngineArchitectureStep(tokens)
                    3 -> PermissionsStep(
                        tokens = tokens,
                        hasAudio = hasAudioPermission,
                        onRequestAudio = {
                            audioPermissionLauncher.launch(android.Manifest.permission.RECORD_AUDIO)
                        }
                    )
                    4 -> LexiconStep(
                        tokens = tokens,
                        userName = userNameInput,
                        onNameChange = { userNameInput = it },
                        lexiconText = lexiconInput,
                        onLexiconChange = { lexiconInput = it }
                    )
                    5 -> InteractivePlaygroundStep(
                        tokens = tokens,
                        playgroundText = playgroundText,
                        onTextChange = { playgroundText = it }
                    )
                }
            }

            // Bottom Navigation Actions
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 10.dp, bottom = 6.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                if (currentStep > 0) {
                    TextButton(
                        onClick = { currentStep-- },
                        modifier = Modifier.testTag("onboarding_back_button")
                    ) {
                        Text(
                            text = "Back",
                            color = tokens.textSecondary,
                            fontSize = 15.sp
                        )
                    }
                } else {
                    Spacer(modifier = Modifier.width(60.dp))
                }

                Button(
                    onClick = {
                        if (currentStep == 4) {
                            val lexList = lexiconInput.split(",").map { it.trim() }.filter { it.isNotBlank() }
                            onUpdatePreferences(
                                preferences.copy(
                                    userName = userNameInput,
                                    customLexicon = lexList
                                )
                            )
                        }
                        if (currentStep < totalSteps - 1) {
                            currentStep++
                        } else {
                            onCompleteOnboarding()
                        }
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color.White,
                        contentColor = Color.Black
                    ),
                    shape = RoundedCornerShape(20.dp),
                    modifier = Modifier
                        .height(48.dp)
                        .testTag("onboarding_next_button")
                ) {
                    Text(
                        text = if (currentStep == totalSteps - 1) "Get Started" else "Continue",
                        color = Color.Black,
                        fontSize = 15.sp,
                        fontWeight = FontWeight.SemiBold
                    )
                }
            }
        }
    }
}

/**
 * Step 0: Floating Bar Highlighting & Controls Tutorial
 * Explains the bar highlighting feature and the exact function of every button.
 */
@Composable
private fun BarHighlightingTourStep(tokens: GlassTokens) {
    var selectedActionIndex by remember { mutableIntStateOf(2) }

    val controlsList = listOf(
        Triple(
            "Close Capsule",
            "Position 0 (Far Left)",
            "Instantly hides the floating capsule when you want an unobstructed screen. The capsule automatically reappears whenever you tap a text field or launch Speak."
        ),
        Triple(
            "Reset Buffer",
            "Position 1 (Inner Left)",
            "Clears your live dictation buffer and restarts conversational context. Use this whenever you want to begin a fresh thought or change subjects."
        ),
        Triple(
            "Speak / Mic Action Pill",
            "Position 2 (Center Anchor)",
            "The heart of Speak. Highlights in crimson when recording 16kHz PCM audio, rendering a live 5-bar audio waveform that dances to your voice."
        ),
        Triple(
            "Live Talkback Pill",
            "Position 3 (Inner Right)",
            "Activates conversational voice powered by Gemini 3.1 Flash Live. Highlights in Precision Cyan and Emerald as Speak listens, reasons, and talks back to you in real-time."
        ),
        Triple(
            "Minimize to Orb",
            "Position 4 (Far Right)",
            "Collapses the full bar into an unobtrusive 56dp floating glass orb. Tap once to toggle dictation, or double-tap to expand back to the full bar."
        ),
        Triple(
            "Tactile Drag Grip",
            "Position 5 (Top Handle)",
            "Center handle allows you to reposition the capsule anywhere on screen. Highlights when touched or dragged. Double-tap the handle to quickly minimize."
        ),
        Triple(
            "Context Memory Bar",
            "Position 6 (Underside Track)",
            "A real-time telemetry strip along the bottom that highlights data throughput and token consumption, keeping latency under 180ms."
        )
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "Bar Highlighting & Controls",
            style = MaterialTheme.typography.headlineMedium,
            color = tokens.textPrimary,
            textAlign = TextAlign.Center
        )
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = "The floating bar highlights dynamically to show active states. Tap any control below to highlight it on the bar:",
            style = MaterialTheme.typography.bodyMedium,
            color = tokens.textSecondary,
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Live Mock Capsule with Dynamic Highlighting
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp),
            contentAlignment = Alignment.Center
        ) {
            FloatingCapsuleOverlay(
                isRecording = selectedActionIndex == 2,
                isLiveTalkbackActive = selectedActionIndex == 3,
                amplitudes = listOf(0.4f, 0.85f, 1.0f, 0.7f, 0.35f),
                memoryUsageFraction = 0.42f,
                isMinimized = false,
                onToggleMinimize = { selectedActionIndex = 4 },
                onCloseClick = { selectedActionIndex = 0 },
                onRestartContextClick = { selectedActionIndex = 1 },
                onMicClick = { selectedActionIndex = 2 },
                onToggleTalkback = { selectedActionIndex = 3 },
                enableDragging = false,
                highlightedButtonIndex = selectedActionIndex
            )
        }

        // Leader line or spotlight indicator
        Canvas(
            modifier = Modifier
                .fillMaxWidth()
                .height(28.dp)
        ) {
            val w = size.width
            val targetX = when (selectedActionIndex) {
                0 -> w * 0.18f
                1 -> w * 0.34f
                2 -> w * 0.50f
                3 -> w * 0.66f
                4 -> w * 0.82f
                5 -> w * 0.50f
                else -> w * 0.50f
            }

            drawLine(
                color = PrecisionCyan,
                start = Offset(targetX, 0f),
                end = Offset(targetX, size.height),
                strokeWidth = 1.5.dp.toPx(),
                pathEffect = PathEffect.dashPathEffect(floatArrayOf(8f, 8f), 0f)
            )
            drawCircle(
                color = PrecisionCyan,
                radius = 3.dp.toPx(),
                center = Offset(targetX, size.height)
            )
        }

        // Selected Control Details Glass Card
        val selectedItem = controlsList[selectedActionIndex]
        GlassCard(
            modifier = Modifier.fillMaxWidth(),
            contentPadding = 16.dp
        ) {
            Column {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = selectedItem.first,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = tokens.textPrimary
                    )
                    Text(
                        text = selectedItem.second,
                        fontSize = 11.sp,
                        color = PrecisionCyan,
                        fontWeight = FontWeight.Medium
                    )
                }
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = selectedItem.third,
                    style = MaterialTheme.typography.bodyMedium,
                    color = tokens.textSecondary,
                    lineHeight = 20.sp
                )
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Horizontal Selector Chips for Easy Tapping
        Text(
            text = "Tap any button to inspect its function:",
            style = MaterialTheme.typography.labelMedium,
            color = tokens.textSecondary,
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(modifier = Modifier.height(8.dp))

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            val chips = listOf(
                "Close" to 0,
                "Reset" to 1,
                "Speak / Mic" to 2,
                "Live Talkback" to 3,
                "Minimize" to 4,
                "Drag Handle" to 5,
                "Context Bar" to 6
            )
            chips.forEach { (label, index) ->
                val isSelected = selectedActionIndex == index
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(16.dp))
                        .background(if (isSelected) Color(0x3300F0FF) else Color(0x14FFFFFF))
                        .border(
                            BorderStroke(
                                1.dp,
                                if (isSelected) PrecisionCyan else Color(0x22FFFFFF)
                            ),
                            RoundedCornerShape(16.dp)
                        )
                        .clickable { selectedActionIndex = index }
                        .padding(horizontal = 14.dp, vertical = 8.dp)
                ) {
                    Text(
                        text = label,
                        color = if (isSelected) Color.White else tokens.textSecondary,
                        fontSize = 12.sp,
                        fontWeight = if (isSelected) FontWeight.SemiBold else FontWeight.Normal
                    )
                }
            }
        }
    }
}

/**
 * Step 1: AI Refinement Tools & "Refine" Interactive Demo
 * Showcases in-place "Refine", "Polish", "Formalize", etc. with a live try-it demo.
 */
@Composable
private fun RefineAndToolsTourStep(tokens: GlassTokens) {
    val sampleRawText = "Um, hey everyone, we need to schedule the release review for tomorrow at 2pm actually 3:30pm, like, to go over the final checklist, you know?"
    var currentDemoText by remember { mutableStateOf(sampleRawText) }
    var activeToolApplied by remember { mutableStateOf<String?>(null) }
    var isTransforming by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "AI Refinement Tools",
            style = MaterialTheme.typography.headlineMedium,
            color = tokens.textPrimary,
            textAlign = TextAlign.Center
        )
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = "Turn conversational verbal stumbles into clean, publication-ready text with one tap.",
            style = MaterialTheme.typography.bodyMedium,
            color = tokens.textSecondary,
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Interactive "Try Refine" Playground Card
        GlassCard(
            modifier = Modifier.fillMaxWidth(),
            contentPadding = 16.dp
        ) {
            Column {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        LucideSparkles(tint = PrecisionCyan, size = 18.dp)
                        Text(
                            text = "Interactive 'Refine' Demo",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = tokens.textPrimary
                        )
                    }

                    if (activeToolApplied != null) {
                        Text(
                            text = "Modified ($activeToolApplied)",
                            fontSize = 11.sp,
                            color = PrecisionCyan,
                            fontWeight = FontWeight.Medium
                        )
                    }
                }

                Spacer(modifier = Modifier.height(10.dp))

                // Spoken Text Display Box
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(12.dp))
                        .background(Color(0x1AFFFFFF))
                        .border(
                            BorderStroke(
                                0.75.dp,
                                if (activeToolApplied != null) PrecisionCyan else Color(0x33FFFFFF)
                            ),
                            RoundedCornerShape(12.dp)
                        )
                        .padding(12.dp)
                ) {
                    Text(
                        text = currentDemoText,
                        color = tokens.textPrimary,
                        fontSize = 14.sp,
                        lineHeight = 20.sp,
                        fontFamily = if (activeToolApplied != null) FontFamily.Default else FontFamily.Default
                    )
                }

                Spacer(modifier = Modifier.height(12.dp))

                // Transformation Action Row
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // Star Button: Refine (fixes stumbles & removes fillers)
                    Button(
                        onClick = {
                            activeToolApplied = "Refine"
                            currentDemoText = "We need to schedule the release review for tomorrow at 3:30 PM to go over the final checklist."
                        },
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFF0F3A56),
                            contentColor = PrecisionCyan
                        ),
                        border = BorderStroke(1.dp, PrecisionCyan),
                        shape = RoundedCornerShape(14.dp),
                        contentPadding = PaddingValues(horizontal = 14.dp, vertical = 6.dp),
                        modifier = Modifier.weight(1.3f)
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            LucideSparkles(tint = PrecisionCyan, size = 16.dp)
                            Text(
                                text = "Refine",
                                fontWeight = FontWeight.Bold,
                                fontSize = 13.sp
                            )
                        }
                    }

                    // Polish Button
                    OutlinedButton(
                        onClick = {
                            activeToolApplied = "Polish"
                            currentDemoText = "Everyone, we need to schedule tomorrow's release review for 3:30 PM to complete the final checklist."
                        },
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = Color.White),
                        border = BorderStroke(0.75.dp, Color(0x44FFFFFF)),
                        shape = RoundedCornerShape(14.dp),
                        contentPadding = PaddingValues(horizontal = 10.dp, vertical = 6.dp),
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("Polish", fontSize = 12.sp)
                    }

                    // Reset Demo Button
                    TextButton(
                        onClick = {
                            activeToolApplied = null
                            currentDemoText = sampleRawText
                        },
                        contentPadding = PaddingValues(horizontal = 8.dp)
                    ) {
                        Text("Reset", color = tokens.textSecondary, fontSize = 12.sp)
                    }
                }

                // What happened explanation
                AnimatedVisibility(visible = activeToolApplied == "Refine") {
                    Column(modifier = Modifier.padding(top = 10.dp)) {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(8.dp))
                                .background(Color(0x1400F0FF))
                                .padding(horizontal = 10.dp, vertical = 6.dp)
                        ) {
                            Text(
                                text = "✓ Removed verbal fillers (\"um\", \"like\", \"you know\")\n✓ Resolved self-correction (\"2pm actually 3:30pm\" → \"3:30 PM\")\n✓ Restored standard punctuation & capitalization",
                                color = PrecisionCyan,
                                fontSize = 11.sp,
                                lineHeight = 16.sp
                            )
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Tool Dictionary Guide
        Text(
            text = "Refinement Tool Suite:",
            style = MaterialTheme.typography.labelLarge,
            color = tokens.textPrimary,
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(modifier = Modifier.height(8.dp))

        RefineToolItem(
            name = "Refine (Primary)",
            tag = "Voice Stumble Fixer",
            description = "Detects self-corrections (\"Monday wait Tuesday\" -> \"Tuesday\"), removes stutter/fillers (\"um\", \"uh\", \"like\"), and formats time without changing your natural tone.",
            tokens = tokens
        )
        Spacer(modifier = Modifier.height(8.dp))

        RefineToolItem(
            name = "Polish",
            tag = "Publication Copyedit",
            description = "Improves cadence and clarity. Smooths rough sentence transitions for clean, publishable prose.",
            tokens = tokens
        )
        Spacer(modifier = Modifier.height(8.dp))

        RefineToolItem(
            name = "Formalize",
            tag = "Executive Presence",
            description = "Rewrites casual spoken thoughts into polished business correspondence suitable for clients and leadership.",
            tokens = tokens
        )
        Spacer(modifier = Modifier.height(8.dp))

        RefineToolItem(
            name = "Summarize",
            tag = "Key Takeaways",
            description = "Condenses lengthy spoken transcripts into high-signal, scannable bullet points.",
            tokens = tokens
        )
        Spacer(modifier = Modifier.height(8.dp))

        RefineToolItem(
            name = "Elaborate",
            tag = "Deep Explanation",
            description = "Expands brief notes into comprehensive, well-reasoned paragraphs.",
            tokens = tokens
        )
    }
}

@Composable
private fun RefineToolItem(
    name: String,
    tag: String,
    description: String,
    tokens: GlassTokens
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(Color(0x14FFFFFF))
            .border(BorderStroke(0.5.dp, Color(0x22FFFFFF)), RoundedCornerShape(12.dp))
            .padding(horizontal = 14.dp, vertical = 10.dp),
        verticalAlignment = Alignment.Top
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = name,
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.SemiBold,
                    color = tokens.textPrimary
                )
                Text(
                    text = tag,
                    fontSize = 11.sp,
                    color = PrecisionCyan,
                    fontWeight = FontWeight.Medium
                )
            }
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = description,
                style = MaterialTheme.typography.bodySmall,
                color = tokens.textSecondary,
                lineHeight = 17.sp
            )
        }
    }
}

/**
 * Step 2: Gemini 3.1 Flash Live Engine Architecture
 */
@Composable
private fun GeminiEngineArchitectureStep(tokens: GlassTokens) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Box(
            modifier = Modifier
                .size(68.dp)
                .clip(CircleShape)
                .background(Color(0x22FFFFFF))
                .border(BorderStroke(1.dp, PrecisionCyan), CircleShape),
            contentAlignment = Alignment.Center
        ) {
            LucideAudioWave(tint = PrecisionCyan, size = 32.dp)
        }

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "Gemini 3.1 Flash Live Engine",
            style = MaterialTheme.typography.headlineMedium,
            color = tokens.textPrimary,
            textAlign = TextAlign.Center
        )
        Spacer(modifier = Modifier.height(6.dp))
        Text(
            text = "Real-time, bidirectional voice streaming powered by Gemini multimodal WebSocket channels.",
            style = MaterialTheme.typography.bodyMedium,
            color = tokens.textSecondary,
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(24.dp))

        GlassCard(
            modifier = Modifier.fillMaxWidth(),
            contentPadding = 18.dp
        ) {
            Column {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = "Active AI Models",
                            style = MaterialTheme.typography.titleMedium,
                            color = tokens.textPrimary
                        )
                        Text(
                            text = "Bidirectional streaming & in-place rewrite",
                            style = MaterialTheme.typography.bodySmall,
                            color = tokens.textSecondary
                        )
                    }
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(12.dp))
                            .background(Color(0x2200F0FF))
                            .border(BorderStroke(0.5.dp, PrecisionCyan), RoundedCornerShape(12.dp))
                            .padding(horizontal = 10.dp, vertical = 4.dp)
                    ) {
                        Text(
                            text = "CONNECTED",
                            color = PrecisionCyan,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.SemiBold
                        )
                    }
                }

                Spacer(modifier = Modifier.height(14.dp))

                ModelEngineBadge(
                    modelName = GeminiModels.GEMINI_3_1_FLASH_LIVE,
                    role = "Primary Live Voice Engine",
                    detail = "Bidirectional 16kHz PCM audio streaming & instant vocal talkback"
                )
                Spacer(modifier = Modifier.height(8.dp))

                ModelEngineBadge(
                    modelName = GeminiModels.TRANSFORM_PRIMARY,
                    role = "Primary In-Place Rewriter",
                    detail = "Drives 'Refine', 'Polish', 'Formalize' & custom transformations"
                )
                Spacer(modifier = Modifier.height(8.dp))

                ModelEngineBadge(
                    modelName = GeminiModels.TRANSFORM_FALLBACK,
                    role = "Automated Fallback Engine",
                    detail = "Guarantees zero-interruption rewriting in low-connectivity conditions"
                )
            }
        }
    }
}

@Composable
private fun ModelEngineBadge(modelName: String, role: String, detail: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(10.dp))
            .background(Color(0x14FFFFFF))
            .border(BorderStroke(0.5.dp, Color(0x22FFFFFF)), RoundedCornerShape(10.dp))
            .padding(horizontal = 12.dp, vertical = 10.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = modelName,
                    color = Color.White,
                    fontSize = 12.sp,
                    fontFamily = FontFamily.Monospace,
                    fontWeight = FontWeight.SemiBold
                )
                Text(
                    text = role,
                    color = PrecisionCyan,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Medium
                )
            }
            Spacer(modifier = Modifier.height(3.dp))
            Text(
                text = detail,
                color = Color(0xFFA1A1AA),
                fontSize = 11.sp
            )
        }
    }
}

/**
 * Step 3: Microphone Permission
 */
@Composable
private fun PermissionsStep(
    tokens: GlassTokens,
    hasAudio: Boolean,
    onRequestAudio: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "Voice Setup & Privacy",
            style = MaterialTheme.typography.headlineMedium,
            color = tokens.textPrimary,
            textAlign = TextAlign.Center
        )
        Spacer(modifier = Modifier.height(6.dp))
        Text(
            text = "Speak processes 16kHz audio directly through secure streaming without third-party tracking.",
            style = MaterialTheme.typography.bodyMedium,
            color = tokens.textSecondary,
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(24.dp))

        PermissionCard(
            title = "Microphone Audio Access",
            description = "Required to record voice dictation and capture multi-frequency waveform telemetry.",
            isGranted = hasAudio,
            onClick = onRequestAudio,
            testTag = "perm_audio_toggle"
        )
        Spacer(modifier = Modifier.height(12.dp))

        PermissionCard(
            title = "Gemini Live Audio Channel",
            description = "Streaming 16kHz PCM audio to Gemini 3.1 Flash Live with low latency (<180ms).",
            isGranted = true,
            onClick = {},
            testTag = "perm_engine_status"
        )
        Spacer(modifier = Modifier.height(12.dp))

        PermissionCard(
            title = "On-Device Local Backup",
            description = "Integrated Android SpeechRecognizer for continuous offline speech recognition.",
            isGranted = true,
            onClick = {},
            testTag = "perm_local_status"
        )
    }
}

@Composable
private fun PermissionCard(
    title: String,
    description: String,
    isGranted: Boolean,
    onClick: () -> Unit,
    testTag: String
) {
    val tokens = LocalGlassTokens.current
    GlassCard(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .testTag(testTag),
        contentPadding = 16.dp
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium,
                    color = tokens.textPrimary
                )
                Spacer(modifier = Modifier.height(2.dp))
                Text(
                    text = description,
                    style = MaterialTheme.typography.bodySmall,
                    color = tokens.textSecondary
                )
            }
            Spacer(modifier = Modifier.width(12.dp))
            Box(
                modifier = Modifier
                    .clip(RoundedCornerShape(16.dp))
                    .background(if (isGranted) Color(0x2200F0FF) else Color(0x14FFFFFF))
                    .border(
                        BorderStroke(0.5.dp, if (isGranted) PrecisionCyan else Color(0x33FFFFFF)),
                        RoundedCornerShape(16.dp)
                    )
                    .padding(horizontal = 12.dp, vertical = 6.dp)
            ) {
                Text(
                    text = if (isGranted) "Granted" else "Enable",
                    color = if (isGranted) PrecisionCyan else Color.White,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.SemiBold
                )
            }
        }
    }
}

/**
 * Step 4: Personal Vocabulary (Lexicon)
 */
@Composable
private fun LexiconStep(
    tokens: GlassTokens,
    userName: String,
    onNameChange: (String) -> Unit,
    lexiconText: String,
    onLexiconChange: (String) -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
    ) {
        Text(
            text = "Personal Vocabulary",
            style = MaterialTheme.typography.headlineMedium,
            color = tokens.textPrimary
        )
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = "Add names, company terms, and technical acronyms so Speak spells them correctly every time.",
            style = MaterialTheme.typography.bodyMedium,
            color = tokens.textSecondary
        )

        Spacer(modifier = Modifier.height(20.dp))

        GlassCard(modifier = Modifier.fillMaxWidth()) {
            Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                Text(
                    text = "Your Name",
                    style = MaterialTheme.typography.titleMedium,
                    color = tokens.textPrimary
                )
                OutlinedTextField(
                    value = userName,
                    onValueChange = onNameChange,
                    modifier = Modifier
                        .fillMaxWidth()
                        .testTag("lexicon_user_name_input"),
                    placeholder = { Text("Enter your name...", color = tokens.textSecondary) },
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = tokens.textPrimary,
                        unfocusedTextColor = tokens.textPrimary,
                        focusedBorderColor = Color.White,
                        unfocusedBorderColor = Color(0x33FFFFFF)
                    ),
                    shape = RoundedCornerShape(12.dp)
                )

                Text(
                    text = "Custom Words (Comma-separated)",
                    style = MaterialTheme.typography.titleMedium,
                    color = tokens.textPrimary
                )
                OutlinedTextField(
                    value = lexiconText,
                    onValueChange = onLexiconChange,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(110.dp)
                        .testTag("lexicon_terms_input"),
                    placeholder = { Text("Speak, Kotlin, Compose, Gemini, API...", color = tokens.textSecondary) },
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
}

/**
 * Step 5: Interactive Live Playground
 */
@Composable
private fun InteractivePlaygroundStep(
    tokens: GlassTokens,
    playgroundText: String,
    onTextChange: (String) -> Unit
) {
    var isSimulatedRecording by remember { mutableStateOf(false) }
    var isPlaygroundCapsuleMinimized by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "Live Interactive Sandbox",
            style = MaterialTheme.typography.headlineMedium,
            color = tokens.textPrimary,
            textAlign = TextAlign.Center
        )
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = "Drag the capsule, test the Speak button, or try refining the text below:",
            style = MaterialTheme.typography.bodyMedium,
            color = tokens.textSecondary,
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(14.dp))

        // Dedicated Touch & Drag Arena
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
                .clip(RoundedCornerShape(16.dp))
                .background(Color(0x15FFFFFF))
                .border(BorderStroke(0.5.dp, tokens.borderGlass), RoundedCornerShape(16.dp))
                .padding(12.dp)
        ) {
            Column(modifier = Modifier.fillMaxSize()) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Interactive Note Buffer",
                        style = MaterialTheme.typography.labelMedium,
                        color = tokens.textSecondary
                    )

                    // Quick Refine button inside playground
                    TextButton(
                        onClick = {
                            var text = playgroundText
                            text = text.replace(Regex("(\\b\\w+\\b)\\s+(?:actually|i mean|no wait)\\s+(\\b\\w+\\b)", RegexOption.IGNORE_CASE)) { m -> m.groupValues[2] }
                            text = text.replace(Regex("\\b(um|uh|like|you know)\\b", RegexOption.IGNORE_CASE), "")
                            text = text.replace(Regex("\\s+"), " ").trim()
                            text = text.replaceFirstChar { if (it.isLowerCase()) it.titlecase() else it.toString() }
                            if (!text.endsWith(".")) text += "."
                            onTextChange(text)
                        },
                        contentPadding = PaddingValues(horizontal = 8.dp, vertical = 2.dp)
                    ) {
                        LucideSparkles(tint = PrecisionCyan, size = 14.dp)
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("Refine Text", color = PrecisionCyan, fontSize = 12.sp)
                    }
                }

                Spacer(modifier = Modifier.height(6.dp))

                OutlinedTextField(
                    value = playgroundText,
                    onValueChange = onTextChange,
                    modifier = Modifier
                        .fillMaxWidth()
                        .weight(1f)
                        .testTag("playground_text_field"),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = tokens.textPrimary,
                        unfocusedTextColor = tokens.textPrimary,
                        focusedBorderColor = Color.White,
                        unfocusedBorderColor = Color(0x33FFFFFF)
                    ),
                    shape = RoundedCornerShape(12.dp)
                )
            }

            // Draggable Floating Capsule Overlay
            FloatingCapsuleOverlay(
                isRecording = isSimulatedRecording,
                isLiveTalkbackActive = false,
                amplitudes = if (isSimulatedRecording) listOf(0.4f, 0.8f, 1.0f, 0.7f, 0.4f) else listOf(0.1f, 0.1f, 0.1f, 0.1f, 0.1f),
                memoryUsageFraction = 0.30f,
                isMinimized = isPlaygroundCapsuleMinimized,
                onToggleMinimize = {
                    isPlaygroundCapsuleMinimized = !isPlaygroundCapsuleMinimized
                },
                onCloseClick = {},
                onRestartContextClick = { onTextChange("") },
                onMicClick = { isSimulatedRecording = !isSimulatedRecording },
                onToggleTalkback = {},
                enableDragging = true,
                modifier = Modifier.align(Alignment.Center)
            )
        }
    }
}
