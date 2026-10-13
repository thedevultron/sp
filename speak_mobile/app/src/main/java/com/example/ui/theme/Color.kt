package com.example.ui.theme

import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color

// Pure Monochrome Black Fluid Glass Theme
val ObsidianBackground = Color(0xFF000000)
val ObsidianSurface = Color(0xFF0D0D0D)
val ObsidianGlassSurface = Color(0xD9121212) // rgba(18, 18, 18, 0.85)
val ObsidianGlassBorder = Color(0x2EFFFFFF)  // rgba(255, 255, 255, 0.18)
val ObsidianTextPrimary = Color(0xFFFFFFFF)
val ObsidianTextSecondary = Color(0xFF8E8E93)
val ObsidianCard = Color(0xFF141414)

// Clean Light Monochrome Theme
val LightBackground = Color(0xFFF7F7F8)
val LightSurface = Color(0xFFFFFFFF)
val LightGlassSurface = Color(0xEEFFFFFF)
val LightGlassBorder = Color(0x1F000000)
val LightTextPrimary = Color(0xFF000000)
val LightTextSecondary = Color(0xFF6B7280)
val LightCard = Color(0xFFF0F0F2)

// Dynamic Status Accents (Monochrome, Void Violet & Precision Cyan)
val VoidViolet = Color(0xFF663AF3)
val VoidVioletGlow = Color(0x66663AF3)
val VoidVioletLight = Color(0xFF8B6BF7)
val MidnightDark = Color(0xFF05060F)
val MidnightSurface = Color(0xFF0B1023)
val MidnightCard = Color(0xFF101735)
val MidnightGlass = Color(0xD90B1023)
val MidnightBorder = Color(0x33C7D3EA)
val FrostTextPrimary = Color(0xFFD1E4FA)
val FrostTextSecondary = Color(0xFF8E9BB5)
val IceBlueCompanion = Color(0xFF38BDF8)

val ElectricMint = Color(0xFF10B981)
val PrecisionCyan = Color(0xFF38BDF8)
val SpeakBlue = Color(0xFF007AFF)
val WarmAmber = Color(0xFFF59E0B)
val CrimsonAlert = Color(0xFFEF4444)
val SlateMuted = Color(0xFF71717A)
val GeminiBlue = Color(0xFF38BDF8)
val GeminiPurple = Color(0xFF8B6BF7)

// Gradients
val SpeakGlassBrush = Brush.verticalGradient(
    colors = listOf(
        Color(0xEE1E1E1E),
        Color(0xDD0D0D0D)
    )
)

val SpeakMonochromeGlow = Brush.horizontalGradient(
    colors = listOf(Color(0xFFFFFFFF), Color(0xFF71717A))
)
