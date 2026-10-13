package com.example.ui.components

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.example.ui.theme.CrimsonAlert
import com.example.ui.theme.ElectricMint
import com.example.ui.theme.WarmAmber

@Composable
fun ContextMemoryBar(
    usageFraction: Float,
    modifier: Modifier = Modifier,
    height: Dp = 3.dp
) {
    val animatedFraction by animateFloatAsState(
        targetValue = usageFraction.coerceIn(0.02f, 1.0f),
        animationSpec = spring(dampingRatio = 0.72f, stiffness = 380f),
        label = "memory_bar_fraction"
    )

    val targetColor = when {
        animatedFraction <= 0.60f -> ElectricMint
        animatedFraction <= 0.85f -> WarmAmber
        else -> CrimsonAlert
    }

    val animatedColor by animateColorAsState(
        targetValue = targetColor,
        animationSpec = spring(dampingRatio = 0.72f, stiffness = 380f),
        label = "memory_bar_color"
    )

    Box(
        modifier = modifier
            .fillMaxWidth()
            .height(height)
            .clip(RoundedCornerShape(bottomStart = 24.dp, bottomEnd = 24.dp))
            .background(Color(0x1FFFFFFF))
    ) {
        Box(
            modifier = Modifier
                .fillMaxHeight()
                .fillMaxWidth(animatedFraction)
                .background(animatedColor)
        )
    }
}
