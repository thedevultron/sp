package com.example.ui.components

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.example.ui.theme.PrecisionCyan

@Composable
fun WaveformVisualizer(
    amplitudes: List<Float>,
    modifier: Modifier = Modifier,
    maxBarHeight: Dp = 24.dp,
    minBarHeight: Dp = 6.dp,
    barWidth: Dp = 3.dp,
    barSpacing: Dp = 3.dp,
    activeColor: Color = Color.White
) {
    val barBrushes = listOf(
        Brush.verticalGradient(listOf(Color(0xFF80C0FF), activeColor)),
        Brush.verticalGradient(listOf(Color(0xFF4CA0FF), PrecisionCyan)),
        Brush.verticalGradient(listOf(Color.White, Color(0xFF007AFF))),
        Brush.verticalGradient(listOf(Color(0xFF4CA0FF), PrecisionCyan)),
        Brush.verticalGradient(listOf(Color(0xFF80C0FF), activeColor))
    )

    Row(
        modifier = modifier.height(maxBarHeight),
        horizontalArrangement = Arrangement.spacedBy(barSpacing, Alignment.CenterHorizontally),
        verticalAlignment = Alignment.CenterVertically
    ) {
        amplitudes.take(5).forEachIndexed { index, rawAmplitude ->
            val animatedAmplitude by animateFloatAsState(
                targetValue = rawAmplitude.coerceIn(0.12f, 1.0f),
                animationSpec = spring(
                    dampingRatio = 0.72f,
                    stiffness = 380f
                ),
                label = "waveform_bar_$index"
            )

            val currentHeight = minBarHeight + (maxBarHeight - minBarHeight) * animatedAmplitude
            val brush = barBrushes.getOrElse(index) { Brush.verticalGradient(listOf(activeColor, PrecisionCyan)) }

            Box(
                modifier = Modifier
                    .width(barWidth)
                    .height(currentHeight)
                    .clip(RoundedCornerShape(2.dp))
                    .background(brush)
            )
        }
    }
}
