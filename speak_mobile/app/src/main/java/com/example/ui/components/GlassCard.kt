package com.example.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxScope
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.example.ui.theme.LocalGlassTokens

@Composable
fun GlassCard(
    modifier: Modifier = Modifier,
    shape: Shape = RoundedCornerShape(16.dp),
    borderWidth: Dp = 0.5.dp,
    customBackground: Color? = null,
    customBorderColor: Color? = null,
    contentPadding: Dp = 16.dp,
    content: @Composable BoxScope.() -> Unit
) {
    val tokens = LocalGlassTokens.current
    val bgColor = customBackground ?: tokens.surfaceGlass
    val borderColor = customBorderColor ?: tokens.borderGlass

    Box(
        modifier = modifier
            .shadow(
                elevation = 8.dp,
                shape = shape,
                ambientColor = Color(0x1F000000),
                spotColor = Color(0x3D000000)
            )
            .clip(shape)
            .background(bgColor)
            .border(
                border = BorderStroke(borderWidth, borderColor),
                shape = shape
            )
            .padding(contentPadding),
        content = content
    )
}

@Composable
fun GlassCapsuleContainer(
    modifier: Modifier = Modifier,
    shape: Shape = RoundedCornerShape(24.dp),
    borderWidth: Dp = 0.5.dp,
    content: @Composable BoxScope.() -> Unit
) {
    val tokens = LocalGlassTokens.current

    Box(
        modifier = modifier
            .shadow(
                elevation = 12.dp,
                shape = shape,
                ambientColor = Color(0x2E000000),
                spotColor = Color(0x52000000)
            )
            .clip(shape)
            .background(
                Brush.verticalGradient(
                    colors = listOf(
                        tokens.surfaceGlass,
                        tokens.surface.copy(alpha = 0.85f)
                    )
                )
            )
            .border(
                border = BorderStroke(borderWidth, tokens.borderGlass),
                shape = shape
            ),
        content = content
    )
}
