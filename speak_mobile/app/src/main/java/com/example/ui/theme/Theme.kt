package com.example.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.Immutable
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

enum class CapsuleThemeMode(val title: String, val description: String) {
    DARK_OBSIDIAN("Dark Obsidian", "Pure black fluid glass with crisp white contrast"),
    LIGHT_MINIMAL("Monochrome Light", "Clean bright glass with deep black typography")
}

@Immutable
data class GlassTokens(
    val surface: Color,
    val surfaceGlass: Color,
    val borderGlass: Color,
    val background: Color,
    val textPrimary: Color,
    val textSecondary: Color,
    val cardBackground: Color,
    val accent: Color,
    val accentViolet: Color = VoidViolet,
    val bgDark: Color = MidnightDark,
    val bgCard: Color = MidnightCard,
    val blurRadius: Dp = 20.dp,
    val borderOpacity: Float = 0.15f
)

val LocalGlassTokens = staticCompositionLocalOf {
    GlassTokens(
        surface = MidnightSurface,
        surfaceGlass = MidnightGlass,
        borderGlass = MidnightBorder,
        background = MidnightDark,
        textPrimary = FrostTextPrimary,
        textSecondary = FrostTextSecondary,
        cardBackground = MidnightCard,
        accent = VoidViolet
    )
}

private val DarkObsidianColorScheme = darkColorScheme(
    primary = VoidViolet,
    onPrimary = Color.White,
    secondary = PrecisionCyan,
    onSecondary = Color.Black,
    tertiary = ElectricMint,
    background = MidnightDark,
    onBackground = FrostTextPrimary,
    surface = MidnightSurface,
    onSurface = FrostTextPrimary,
    surfaceVariant = MidnightCard,
    onSurfaceVariant = FrostTextSecondary
)

private val LightMinimalColorScheme = lightColorScheme(
    primary = Color.Black,
    onPrimary = Color.White,
    secondary = SpeakBlue,
    onSecondary = Color.White,
    tertiary = ElectricMint,
    background = LightBackground,
    onBackground = LightTextPrimary,
    surface = LightSurface,
    onSurface = LightTextPrimary,
    surfaceVariant = LightCard,
    onSurfaceVariant = LightTextSecondary
)

@Composable
fun FluidCapsuleTheme(
    themeMode: CapsuleThemeMode = CapsuleThemeMode.DARK_OBSIDIAN,
    blurRadius: Dp = 20.dp,
    borderOpacity: Float = 0.15f,
    content: @Composable () -> Unit
) {
    val (colorScheme, glassTokens) = when (themeMode) {
        CapsuleThemeMode.DARK_OBSIDIAN -> Pair(
            DarkObsidianColorScheme,
            GlassTokens(
                surface = ObsidianSurface,
                surfaceGlass = ObsidianGlassSurface,
                borderGlass = ObsidianGlassBorder,
                background = ObsidianBackground,
                textPrimary = ObsidianTextPrimary,
                textSecondary = ObsidianTextSecondary,
                cardBackground = ObsidianCard,
                accent = Color.White,
                blurRadius = blurRadius,
                borderOpacity = borderOpacity
            )
        )
        CapsuleThemeMode.LIGHT_MINIMAL -> Pair(
            LightMinimalColorScheme,
            GlassTokens(
                surface = LightSurface,
                surfaceGlass = LightGlassSurface,
                borderGlass = LightGlassBorder,
                background = LightBackground,
                textPrimary = LightTextPrimary,
                textSecondary = LightTextSecondary,
                cardBackground = LightCard,
                accent = Color.Black,
                blurRadius = blurRadius,
                borderOpacity = borderOpacity
            )
        )
    }

    CompositionLocalProvider(LocalGlassTokens provides glassTokens) {
        MaterialTheme(
            colorScheme = colorScheme,
            typography = Typography,
            content = content
        )
    }
}
