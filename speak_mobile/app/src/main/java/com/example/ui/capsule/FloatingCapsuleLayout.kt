package com.example.ui.capsule

import androidx.compose.animation.*
import androidx.compose.animation.core.animateDpAsState
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.components.*
import com.example.ui.theme.*
import kotlin.math.roundToInt

@Composable
fun FloatingCapsuleOverlay(
    isRecording: Boolean,
    isLiveTalkbackActive: Boolean,
    amplitudes: List<Float>,
    memoryUsageFraction: Float,
    isMinimized: Boolean = false,
    onToggleMinimize: () -> Unit = {},
    transformingStatus: String? = null,
    isSpeakingBack: Boolean = false,
    onCloseClick: () -> Unit,
    onRestartContextClick: () -> Unit,
    onMicClick: () -> Unit,
    onToggleTalkback: () -> Unit,
    modifier: Modifier = Modifier,
    enableDragging: Boolean = true,
    initialOffsetX: Float = 0f,
    initialOffsetY: Float = 0f,
    onPositionChanged: ((Float, Float) -> Unit)? = null,
    highlightedButtonIndex: Int? = null
) {
    val tokens = LocalGlassTokens.current
    var offsetX by remember { mutableFloatStateOf(initialOffsetX) }
    var offsetY by remember { mutableFloatStateOf(initialOffsetY) }
    var isBeingDragged by remember { mutableStateOf(false) }

    // Update if initial changes
    LaunchedEffect(initialOffsetX, initialOffsetY) {
        if (!isBeingDragged) {
            offsetX = initialOffsetX
            offsetY = initialOffsetY
        }
    }

    val animatedWidth by animateDpAsState(
        targetValue = when {
            isMinimized -> 56.dp
            isLiveTalkbackActive -> 300.dp
            isRecording -> 296.dp
            else -> 280.dp
        },
        animationSpec = spring(dampingRatio = 0.76f, stiffness = 380f),
        label = "capsule_width"
    )

    val animatedHeight by animateDpAsState(
        targetValue = when {
            isMinimized -> 56.dp
            transformingStatus != null -> 80.dp
            else -> 60.dp
        },
        animationSpec = spring(dampingRatio = 0.76f, stiffness = 380f),
        label = "capsule_height"
    )

    val animatedCornerRadius by animateDpAsState(
        targetValue = if (isMinimized) 28.dp else 26.dp,
        animationSpec = spring(dampingRatio = 0.76f, stiffness = 380f),
        label = "capsule_corner"
    )

    val dragScale by animateFloatAsState(
        targetValue = if (isBeingDragged) 1.04f else 1.0f,
        animationSpec = spring(dampingRatio = 0.75f, stiffness = 400f),
        label = "drag_scale"
    )

    val shadowElevation by animateDpAsState(
        targetValue = if (isBeingDragged) 24.dp else 12.dp,
        label = "shadow_elevation"
    )

    val recordingGlowColor by animateColorAsState(
        targetValue = if (isRecording) Color(0xFFFF4D4D) else Color.White,
        label = "glow_color"
    )

    Box(
        modifier = modifier
            .offset { IntOffset(offsetX.roundToInt(), offsetY.roundToInt()) }
            .scale(dragScale)
            .width(animatedWidth)
            .shadow(
                elevation = shadowElevation,
                shape = RoundedCornerShape(animatedCornerRadius),
                ambientColor = Color(0x66000000),
                spotColor = Color(0x88000000)
            )
            .clip(RoundedCornerShape(animatedCornerRadius))
            .background(
                Brush.verticalGradient(
                    listOf(
                        if (isMinimized && isRecording) Color(0xF0301010) else Color(0xF0181818),
                        if (isMinimized && isRecording) Color(0xF5200808) else Color(0xF50A0A0A)
                    )
                )
            )
            .border(
                BorderStroke(
                    if (isBeingDragged || (isMinimized && isRecording)) 1.25.dp else 0.5.dp,
                    if (isBeingDragged) Color.White else if (isMinimized && isRecording) Color(0xFFFF6B6B) else Color(0x33FFFFFF)
                ),
                RoundedCornerShape(animatedCornerRadius)
            )
            .then(
                if (enableDragging) {
                    Modifier.pointerInput(isMinimized) {
                        detectDragGestures(
                            onDragStart = {
                                isBeingDragged = true
                            },
                            onDragEnd = {
                                isBeingDragged = false
                                onPositionChanged?.invoke(offsetX, offsetY)
                            },
                            onDragCancel = {
                                isBeingDragged = false
                            },
                            onDrag = { change, dragAmount ->
                                change.consume()
                                offsetX += dragAmount.x
                                offsetY += dragAmount.y
                                onPositionChanged?.invoke(offsetX, offsetY)
                            }
                        )
                    }
                } else Modifier
            )
            .testTag("floating_glass_capsule"),
        contentAlignment = Alignment.Center
    ) {
        if (isMinimized) {
            // Minimized Small Circle / Orb UI
            Box(
                modifier = Modifier
                    .size(56.dp)
                    .clip(CircleShape)
                    .pointerInput(Unit) {
                        detectTapGestures(
                            onTap = {
                                // Tap once to start/stop speaking
                                onMicClick()
                            },
                            onDoubleTap = {
                                // Tap twice to expand
                                onToggleMinimize()
                            }
                        )
                    }
                    .testTag("capsule_minimized_orb"),
                contentAlignment = Alignment.Center
            ) {
                if (isRecording) {
                    // Mini pulsing live waveform when minimized
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(2.5.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        amplitudes.take(4).forEach { amp ->
                            val h = (8 + (amp * 20)).coerceIn(6f, 26f).dp
                            Box(
                                modifier = Modifier
                                    .width(3.dp)
                                    .height(h)
                                    .clip(CircleShape)
                                    .background(Color.White)
                            )
                        }
                    }
                } else {
                    LucideMic(tint = Color.White, size = 22.dp)
                }
            }
        } else {
            // Expanded Full Capsule UI
            Column(
                modifier = Modifier.fillMaxWidth(),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Tactile Drag Grip Handle
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(top = 6.dp, bottom = 2.dp)
                        .pointerInput(Unit) {
                            detectTapGestures(
                                onDoubleTap = {
                                    // Double tap handle to minimize
                                    onToggleMinimize()
                                }
                            )
                        },
                    contentAlignment = Alignment.Center
                ) {
                    val isHandleHighlighted = highlightedButtonIndex == 5
                    Box(
                        modifier = Modifier
                            .width(if (isHandleHighlighted) 44.dp else 32.dp)
                            .height(if (isHandleHighlighted) 4.dp else 3.dp)
                            .clip(CircleShape)
                            .background(if (isHandleHighlighted) PrecisionCyan else if (isBeingDragged) Color.White else Color(0x44FFFFFF))
                    )
                }

                // Top transformation feedback chip if active
                AnimatedVisibility(
                    visible = transformingStatus != null,
                    enter = fadeIn(),
                    exit = fadeOut()
                ) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(Color(0x22FFFFFF))
                            .padding(vertical = 4.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = transformingStatus ?: "",
                            color = PrecisionCyan,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Medium
                        )
                    }
                }

                // Main horizontal capsule controls (48dp height)
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(48.dp)
                        .padding(horizontal = 8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    // Position 0 (Far Left): Close / Dismiss Capsule
                    CapsuleIconButton(
                        onClick = onCloseClick,
                        testTag = "capsule_close_button",
                        tooltip = "Close Capsule",
                        isHighlighted = highlightedButtonIndex == 0
                    ) {
                        LucideClose(tint = if (highlightedButtonIndex == 0) Color.White else Color(0xFFA1A1AA), size = 18.dp)
                    }

                    // Position 1 (Inner Left): Reset / Restart Context
                    CapsuleIconButton(
                        onClick = onRestartContextClick,
                        testTag = "capsule_restart_button",
                        tooltip = "Reset Context",
                        isHighlighted = highlightedButtonIndex == 1
                    ) {
                        LucideRotateCcw(tint = if (highlightedButtonIndex == 1) Color.White else Color(0xFFA1A1AA), size = 18.dp)
                    }

                    // Position 2 (Center Anchor): Primary Mic Action / Smooth Morphing 5-bar Waveform
                    val micBgBrush = if (isRecording) {
                        Brush.horizontalGradient(
                            listOf(Color(0xFFEF4444), Color(0xFFDC2626))
                        )
                    } else if (highlightedButtonIndex == 2) {
                        Brush.horizontalGradient(
                            listOf(Color(0xFF0F3A56), Color(0xFF1E40AF))
                        )
                    } else {
                        Brush.horizontalGradient(
                            listOf(Color(0xFF27272A), Color(0xFF18181B))
                        )
                    }

                    val micPillWidth by animateDpAsState(
                        targetValue = when {
                            isLiveTalkbackActive && isRecording -> 52.dp
                            isLiveTalkbackActive -> 36.dp
                            isRecording -> 96.dp
                            else -> 82.dp
                        },
                        animationSpec = spring(dampingRatio = 0.76f, stiffness = 380f),
                        label = "mic_pill_width"
                    )

                    Box(
                        modifier = Modifier
                            .height(36.dp)
                            .width(micPillWidth)
                            .clip(RoundedCornerShape(18.dp))
                            .background(micBgBrush)
                            .border(
                                BorderStroke(
                                    if (highlightedButtonIndex == 2) 1.75.dp else 0.75.dp,
                                    if (highlightedButtonIndex == 2) PrecisionCyan else if (isRecording) Color(0xFFFF6B6B) else Color(0x44FFFFFF)
                                ),
                                RoundedCornerShape(18.dp)
                            )
                            .clickable(
                                interactionSource = remember { MutableInteractionSource() },
                                indication = null,
                                onClick = onMicClick
                            )
                            .testTag("capsule_mic_button"),
                        contentAlignment = Alignment.Center
                    ) {
                        AnimatedContent(
                            targetState = isRecording to isLiveTalkbackActive,
                            transitionSpec = {
                                (fadeIn(animationSpec = spring(stiffness = 500f)) + scaleIn(initialScale = 0.85f)) togetherWith
                                (fadeOut(animationSpec = spring(stiffness = 500f)) + scaleOut(targetScale = 0.85f))
                            },
                            label = "mic_morph_transition"
                        ) { (recording, liveActive) ->
                            if (recording) {
                                if (liveActive) {
                                    WaveformVisualizer(
                                        amplitudes = amplitudes.take(3),
                                        maxBarHeight = 18.dp,
                                        minBarHeight = 5.dp,
                                        barWidth = 2.5.dp,
                                        barSpacing = 2.5.dp,
                                        activeColor = Color.White
                                    )
                                } else {
                                    WaveformVisualizer(
                                        amplitudes = amplitudes,
                                        maxBarHeight = 20.dp,
                                        minBarHeight = 5.dp,
                                        barWidth = 3.dp,
                                        barSpacing = 3.dp,
                                        activeColor = Color.White
                                    )
                                }
                            } else {
                                if (liveActive) {
                                    // Shrunk Speak icon-only state when Live is active
                                    LucideMic(tint = Color.White, size = 16.dp)
                                } else {
                                    // Default Speak pill with icon and label
                                    Row(
                                        verticalAlignment = Alignment.CenterVertically,
                                        horizontalArrangement = Arrangement.spacedBy(6.dp),
                                        modifier = Modifier.padding(horizontal = 10.dp)
                                    ) {
                                        LucideMic(tint = Color.White, size = 16.dp)
                                        Text(
                                            text = "Speak",
                                            color = Color.White,
                                            fontSize = 12.sp,
                                            fontWeight = FontWeight.SemiBold
                                        )
                                    }
                                }
                            }
                        }
                    }

                    // Position 3 (Inner Right): Live Voice Talkback Expansion
                    val talkbackPillWidth by animateDpAsState(
                        targetValue = if (isLiveTalkbackActive) 86.dp else 34.dp,
                        animationSpec = spring(dampingRatio = 0.76f, stiffness = 380f),
                        label = "talkback_pill_width"
                    )

                    val talkbackGlowColor by animateColorAsState(
                        targetValue = when {
                            highlightedButtonIndex == 3 -> PrecisionCyan
                            isSpeakingBack -> Color(0xFF10B981) // Emerald when speaking back
                            isLiveTalkbackActive -> PrecisionCyan
                            else -> Color(0xFFA1A1AA)
                        },
                        label = "talkback_glow"
                    )

                    Box(
                        modifier = Modifier
                            .height(34.dp)
                            .width(talkbackPillWidth)
                            .clip(RoundedCornerShape(17.dp))
                            .background(
                                if (highlightedButtonIndex == 3) Brush.horizontalGradient(
                                    listOf(Color(0xFF0F3A56), Color(0xFF0C2B3E))
                                ) else if (isLiveTalkbackActive) Brush.horizontalGradient(
                                    listOf(Color(0xFF0C2B3E), Color(0xFF0F3A56))
                                ) else Brush.horizontalGradient(listOf(Color.Transparent, Color.Transparent))
                            )
                            .border(
                                BorderStroke(
                                    if (highlightedButtonIndex == 3) 1.75.dp else 0.75.dp,
                                    if (highlightedButtonIndex == 3) PrecisionCyan else if (isLiveTalkbackActive) talkbackGlowColor else Color(0x22FFFFFF)
                                ),
                                RoundedCornerShape(17.dp)
                            )
                            .clickable(onClick = onToggleTalkback)
                            .testTag("capsule_talkback_button"),
                        contentAlignment = Alignment.Center
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(5.dp),
                            modifier = Modifier.padding(horizontal = if (isLiveTalkbackActive) 8.dp else 0.dp)
                        ) {
                            LucideAudioWave(
                                tint = talkbackGlowColor,
                                size = 17.dp
                            )
                            if (isLiveTalkbackActive) {
                                Text(
                                    text = if (isSpeakingBack) "Speaking" else "Live",
                                    color = talkbackGlowColor,
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold
                                )
                                Box(
                                    modifier = Modifier
                                        .size(5.dp)
                                        .clip(CircleShape)
                                        .background(talkbackGlowColor)
                                )
                            }
                        }
                    }

                    // Position 4 (Far Right): Minimise Button
                    CapsuleIconButton(
                        onClick = onToggleMinimize,
                        testTag = "capsule_minimize_button",
                        tooltip = "Minimise to Circle",
                        customBackground = Color(0x1AFFFFFF),
                        isHighlighted = highlightedButtonIndex == 4
                    ) {
                        LucideMinus(tint = Color.White, size = 18.dp)
                    }
                }

                // Underside Context Memory Bar (2.5dp dynamic track)
                val isMemoryBarHighlighted = highlightedButtonIndex == 6
                ContextMemoryBar(
                    usageFraction = if (isMemoryBarHighlighted) 0.65f else memoryUsageFraction,
                    modifier = Modifier
                        .fillMaxWidth()
                        .then(
                            if (isMemoryBarHighlighted) {
                                Modifier.border(BorderStroke(1.dp, PrecisionCyan), RoundedCornerShape(2.dp))
                            } else Modifier
                        )
                )
            }
        }
    }
}

@Composable
private fun CapsuleIconButton(
    onClick: () -> Unit,
    testTag: String,
    tooltip: String,
    customBackground: Color = Color.Transparent,
    isHighlighted: Boolean = false,
    icon: @Composable () -> Unit
) {
    Box(
        modifier = Modifier
            .size(34.dp)
            .clip(CircleShape)
            .background(if (isHighlighted) Color(0x4400F0FF) else customBackground)
            .border(
                BorderStroke(
                    if (isHighlighted) 1.5.dp else 0.dp,
                    if (isHighlighted) PrecisionCyan else Color.Transparent
                ),
                CircleShape
            )
            .clickable(onClick = onClick)
            .testTag(testTag),
        contentAlignment = Alignment.Center
    ) {
        icon()
    }
}
