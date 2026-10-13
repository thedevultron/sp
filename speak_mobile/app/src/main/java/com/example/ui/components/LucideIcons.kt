package com.example.ui.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

object LucideIcons {
    val StrokeWidth: Dp = 1.75.dp
}

@Composable
fun LucideMic(
    modifier: Modifier = Modifier,
    tint: Color = Color.White,
    size: Dp = 20.dp
) {
    Canvas(modifier = modifier.size(size)) {
        val stroke = LucideIcons.StrokeWidth.toPx()
        val w = this.size.width
        val h = this.size.height

        // Mic capsule
        val capW = w * 0.38f
        val capH = h * 0.52f
        val capL = (w - capW) / 2f
        val capT = h * 0.12f
        val radius = capW / 2f

        drawRoundRect(
            color = tint,
            topLeft = Offset(capL, capT),
            size = Size(capW, capH),
            cornerRadius = CornerRadius(radius, radius),
            style = Stroke(width = stroke)
        )

        // Mic cradle arc
        val path = Path().apply {
            moveTo(w * 0.20f, h * 0.44f)
            cubicTo(
                w * 0.20f, h * 0.72f,
                w * 0.80f, h * 0.72f,
                w * 0.80f, h * 0.44f
            )
        }
        drawPath(
            path = path,
            color = tint,
            style = Stroke(width = stroke, cap = StrokeCap.Round, join = StrokeJoin.Round)
        )

        // Mic stem & base
        drawLine(
            color = tint,
            start = Offset(w * 0.5f, h * 0.72f),
            end = Offset(w * 0.5f, h * 0.88f),
            strokeWidth = stroke,
            cap = StrokeCap.Round
        )
        drawLine(
            color = tint,
            start = Offset(w * 0.32f, h * 0.88f),
            end = Offset(w * 0.68f, h * 0.88f),
            strokeWidth = stroke,
            cap = StrokeCap.Round
        )
    }
}

@Composable
fun LucideClose(
    modifier: Modifier = Modifier,
    tint: Color = Color.White,
    size: Dp = 20.dp
) {
    Canvas(modifier = modifier.size(size)) {
        val stroke = LucideIcons.StrokeWidth.toPx()
        val w = this.size.width
        val h = this.size.height
        val pad = w * 0.26f

        drawLine(
            color = tint,
            start = Offset(pad, pad),
            end = Offset(w - pad, h - pad),
            strokeWidth = stroke,
            cap = StrokeCap.Round
        )
        drawLine(
            color = tint,
            start = Offset(w - pad, pad),
            end = Offset(pad, h - pad),
            strokeWidth = stroke,
            cap = StrokeCap.Round
        )
    }
}

@Composable
fun LucideRotateCcw(
    modifier: Modifier = Modifier,
    tint: Color = Color.White,
    size: Dp = 20.dp
) {
    Canvas(modifier = modifier.size(size)) {
        val stroke = LucideIcons.StrokeWidth.toPx()
        val w = this.size.width
        val h = this.size.height

        val arcPath = Path().apply {
            // Arc going counter-clockwise
            moveTo(w * 0.28f, h * 0.38f)
            cubicTo(
                w * 0.38f, h * 0.18f,
                w * 0.78f, h * 0.22f,
                w * 0.82f, h * 0.52f
            )
            cubicTo(
                w * 0.86f, h * 0.82f,
                w * 0.46f, h * 0.90f,
                w * 0.26f, h * 0.72f
            )
        }
        drawPath(
            path = arcPath,
            color = tint,
            style = Stroke(width = stroke, cap = StrokeCap.Round, join = StrokeJoin.Round)
        )

        // Arrow head pointing left
        val arrow = Path().apply {
            moveTo(w * 0.12f, h * 0.38f)
            lineTo(w * 0.30f, h * 0.38f)
            lineTo(w * 0.30f, h * 0.20f)
        }
        drawPath(
            path = arrow,
            color = tint,
            style = Stroke(width = stroke, cap = StrokeCap.Round, join = StrokeJoin.Round)
        )
    }
}

@Composable
fun LucideEye(
    modifier: Modifier = Modifier,
    tint: Color = Color.White,
    size: Dp = 20.dp
) {
    Canvas(modifier = modifier.size(size)) {
        val stroke = LucideIcons.StrokeWidth.toPx()
        val w = this.size.width
        val h = this.size.height

        val eyePath = Path().apply {
            moveTo(w * 0.10f, h * 0.50f)
            cubicTo(
                w * 0.30f, h * 0.22f,
                w * 0.70f, h * 0.22f,
                w * 0.90f, h * 0.50f
            )
            cubicTo(
                w * 0.70f, h * 0.78f,
                w * 0.30f, h * 0.78f,
                w * 0.10f, h * 0.50f
            )
            close()
        }
        drawPath(
            path = eyePath,
            color = tint,
            style = Stroke(width = stroke, cap = StrokeCap.Round, join = StrokeJoin.Round)
        )

        // Pupil
        drawCircle(
            color = tint,
            radius = w * 0.14f,
            center = Offset(w * 0.50f, h * 0.50f),
            style = Stroke(width = stroke)
        )
    }
}

@Composable
fun LucideSparkles(
    modifier: Modifier = Modifier,
    tint: Color = Color.White,
    size: Dp = 20.dp
) {
    Canvas(modifier = modifier.size(size)) {
        val stroke = LucideIcons.StrokeWidth.toPx()
        val w = this.size.width
        val h = this.size.height

        // Main 4-point star
        val star = Path().apply {
            val cx = w * 0.44f
            val cy = h * 0.46f
            val r = w * 0.36f

            moveTo(cx, cy - r)
            cubicTo(cx, cy, cx, cy, cx + r, cy)
            cubicTo(cx, cy, cx, cy, cx, cy + r)
            cubicTo(cx, cy, cx, cy, cx - r, cy)
            cubicTo(cx, cy, cx, cy, cx, cy - r)
            close()
        }
        drawPath(
            path = star,
            color = tint,
            style = Stroke(width = stroke, cap = StrokeCap.Round, join = StrokeJoin.Round)
        )

        // Secondary small sparkle top right
        drawLine(
            color = tint,
            start = Offset(w * 0.82f, h * 0.18f),
            end = Offset(w * 0.82f, h * 0.32f),
            strokeWidth = stroke * 0.9f,
            cap = StrokeCap.Round
        )
        drawLine(
            color = tint,
            start = Offset(w * 0.75f, h * 0.25f),
            end = Offset(w * 0.89f, h * 0.25f),
            strokeWidth = stroke * 0.9f,
            cap = StrokeCap.Round
        )
    }
}

@Composable
fun LucideHome(
    modifier: Modifier = Modifier,
    tint: Color = Color.White,
    size: Dp = 20.dp
) {
    Canvas(modifier = modifier.size(size)) {
        val stroke = LucideIcons.StrokeWidth.toPx()
        val w = this.size.width
        val h = this.size.height

        val house = Path().apply {
            moveTo(w * 0.15f, h * 0.44f)
            lineTo(w * 0.50f, h * 0.15f)
            lineTo(w * 0.85f, h * 0.44f)
            lineTo(w * 0.85f, h * 0.86f)
            lineTo(w * 0.15f, h * 0.86f)
            close()
        }
        drawPath(
            path = house,
            color = tint,
            style = Stroke(width = stroke, cap = StrokeCap.Round, join = StrokeJoin.Round)
        )

        // Door
        val door = Path().apply {
            moveTo(w * 0.38f, h * 0.86f)
            lineTo(w * 0.38f, h * 0.58f)
            lineTo(w * 0.62f, h * 0.58f)
            lineTo(w * 0.62f, h * 0.86f)
        }
        drawPath(
            path = door,
            color = tint,
            style = Stroke(width = stroke, cap = StrokeCap.Round, join = StrokeJoin.Round)
        )
    }
}

@Composable
fun LucideFileText(
    modifier: Modifier = Modifier,
    tint: Color = Color.White,
    size: Dp = 20.dp
) {
    Canvas(modifier = modifier.size(size)) {
        val stroke = LucideIcons.StrokeWidth.toPx()
        val w = this.size.width
        val h = this.size.height

        val page = Path().apply {
            moveTo(w * 0.22f, h * 0.14f)
            lineTo(w * 0.58f, h * 0.14f)
            lineTo(w * 0.78f, h * 0.34f)
            lineTo(w * 0.78f, h * 0.86f)
            lineTo(w * 0.22f, h * 0.86f)
            close()
        }
        drawPath(
            path = page,
            color = tint,
            style = Stroke(width = stroke, cap = StrokeCap.Round, join = StrokeJoin.Round)
        )

        // Fold corner
        val fold = Path().apply {
            moveTo(w * 0.58f, h * 0.14f)
            lineTo(w * 0.58f, h * 0.34f)
            lineTo(w * 0.78f, h * 0.34f)
        }
        drawPath(
            path = fold,
            color = tint,
            style = Stroke(width = stroke, cap = StrokeCap.Round, join = StrokeJoin.Round)
        )

        // Lines of text
        drawLine(
            color = tint,
            start = Offset(w * 0.34f, h * 0.50f),
            end = Offset(w * 0.66f, h * 0.50f),
            strokeWidth = stroke,
            cap = StrokeCap.Round
        )
        drawLine(
            color = tint,
            start = Offset(w * 0.34f, h * 0.64f),
            end = Offset(w * 0.56f, h * 0.64f),
            strokeWidth = stroke,
            cap = StrokeCap.Round
        )
    }
}

@Composable
fun LucideSettings(
    modifier: Modifier = Modifier,
    tint: Color = Color.White,
    size: Dp = 20.dp
) {
    Canvas(modifier = modifier.size(size)) {
        val stroke = LucideIcons.StrokeWidth.toPx()
        val w = this.size.width
        val h = this.size.height

        drawCircle(
            color = tint,
            radius = w * 0.16f,
            center = Offset(w * 0.5f, h * 0.5f),
            style = Stroke(width = stroke)
        )

        drawCircle(
            color = tint,
            radius = w * 0.34f,
            center = Offset(w * 0.5f, h * 0.5f),
            style = Stroke(width = stroke)
        )

        for (i in 0 until 8) {
            val angle = Math.toRadians((i * 45).toDouble())
            val cx = (w * 0.5f + Math.cos(angle) * (w * 0.34f)).toFloat()
            val cy = (h * 0.5f + Math.sin(angle) * (h * 0.34f)).toFloat()
            val ex = (w * 0.5f + Math.cos(angle) * (w * 0.44f)).toFloat()
            val ey = (h * 0.5f + Math.sin(angle) * (h * 0.44f)).toFloat()
            drawLine(
                color = tint,
                start = Offset(cx, cy),
                end = Offset(ex, ey),
                strokeWidth = stroke * 1.1f,
                cap = StrokeCap.Round
            )
        }
    }
}

@Composable
fun LucideMinus(
    modifier: Modifier = Modifier,
    tint: Color = Color.White,
    size: Dp = 20.dp
) {
    Canvas(modifier = modifier.size(size)) {
        val stroke = LucideIcons.StrokeWidth.toPx()
        val w = this.size.width
        val h = this.size.height

        drawLine(
            color = tint,
            start = Offset(w * 0.22f, h * 0.50f),
            end = Offset(w * 0.78f, h * 0.50f),
            strokeWidth = stroke * 1.25f,
            cap = StrokeCap.Round
        )
    }
}

@Composable
fun LucideMaximize(
    modifier: Modifier = Modifier,
    tint: Color = Color.White,
    size: Dp = 20.dp
) {
    Canvas(modifier = modifier.size(size)) {
        val stroke = LucideIcons.StrokeWidth.toPx()
        val w = this.size.width
        val h = this.size.height
        val pad = w * 0.22f

        // Top-left corner
        drawLine(color = tint, start = Offset(pad, pad + w * 0.2f), end = Offset(pad, pad), strokeWidth = stroke, cap = StrokeCap.Round)
        drawLine(color = tint, start = Offset(pad, pad), end = Offset(pad + w * 0.2f, pad), strokeWidth = stroke, cap = StrokeCap.Round)

        // Bottom-right corner
        drawLine(color = tint, start = Offset(w - pad, h - pad - w * 0.2f), end = Offset(w - pad, h - pad), strokeWidth = stroke, cap = StrokeCap.Round)
        drawLine(color = tint, start = Offset(w - pad, h - pad), end = Offset(w - pad - w * 0.2f, h - pad), strokeWidth = stroke, cap = StrokeCap.Round)
    }
}

@Composable
fun LucideAudioWave(
    modifier: Modifier = Modifier,
    tint: Color = Color.White,
    size: Dp = 20.dp
) {
    Canvas(modifier = modifier.size(size)) {
        val stroke = LucideIcons.StrokeWidth.toPx()
        val w = this.size.width
        val h = this.size.height

        // 5 equalizer audio bars representing voice talkback
        val bar1H = h * 0.32f
        val bar2H = h * 0.70f
        val bar3H = h * 0.88f
        val bar4H = h * 0.58f
        val bar5H = h * 0.36f

        val centerY = h * 0.5f

        drawLine(color = tint, start = Offset(w * 0.16f, centerY - bar1H / 2f), end = Offset(w * 0.16f, centerY + bar1H / 2f), strokeWidth = stroke * 1.1f, cap = StrokeCap.Round)
        drawLine(color = tint, start = Offset(w * 0.33f, centerY - bar2H / 2f), end = Offset(w * 0.33f, centerY + bar2H / 2f), strokeWidth = stroke * 1.1f, cap = StrokeCap.Round)
        drawLine(color = tint, start = Offset(w * 0.50f, centerY - bar3H / 2f), end = Offset(w * 0.50f, centerY + bar3H / 2f), strokeWidth = stroke * 1.15f, cap = StrokeCap.Round)
        drawLine(color = tint, start = Offset(w * 0.67f, centerY - bar4H / 2f), end = Offset(w * 0.67f, centerY + bar4H / 2f), strokeWidth = stroke * 1.1f, cap = StrokeCap.Round)
        drawLine(color = tint, start = Offset(w * 0.84f, centerY - bar5H / 2f), end = Offset(w * 0.84f, centerY + bar5H / 2f), strokeWidth = stroke * 1.1f, cap = StrokeCap.Round)
    }
}

@Composable
fun LucideLayers(
    modifier: Modifier = Modifier,
    tint: Color = Color.White,
    size: Dp = 20.dp
) {
    Canvas(modifier = modifier.size(size)) {
        val stroke = LucideIcons.StrokeWidth.toPx()
        val w = this.size.width
        val h = this.size.height

        val layer1 = Path().apply {
            moveTo(w * 0.50f, h * 0.18f)
            lineTo(w * 0.88f, h * 0.36f)
            lineTo(w * 0.50f, h * 0.54f)
            lineTo(w * 0.12f, h * 0.36f)
            close()
        }
        drawPath(layer1, color = tint, style = Stroke(width = stroke, cap = StrokeCap.Round, join = StrokeJoin.Round))

        val layer2 = Path().apply {
            moveTo(w * 0.12f, h * 0.52f)
            lineTo(w * 0.50f, h * 0.70f)
            lineTo(w * 0.88f, h * 0.52f)
        }
        drawPath(layer2, color = tint, style = Stroke(width = stroke, cap = StrokeCap.Round, join = StrokeJoin.Round))

        val layer3 = Path().apply {
            moveTo(w * 0.12f, h * 0.68f)
            lineTo(w * 0.50f, h * 0.86f)
            lineTo(w * 0.88f, h * 0.68f)
        }
        drawPath(layer3, color = tint, style = Stroke(width = stroke, cap = StrokeCap.Round, join = StrokeJoin.Round))
    }
}

@Composable
fun LucideCopy(
    modifier: Modifier = Modifier,
    tint: Color = Color.White,
    size: Dp = 20.dp
) {
    Canvas(modifier = modifier.size(size)) {
        val stroke = LucideIcons.StrokeWidth.toPx()
        val w = this.size.width
        val h = this.size.height

        // Back page
        drawRoundRect(
            color = tint,
            topLeft = Offset(w * 0.15f, h * 0.15f),
            size = Size(w * 0.55f, h * 0.55f),
            cornerRadius = CornerRadius(w * 0.08f, w * 0.08f),
            style = Stroke(width = stroke)
        )
        // Front page
        drawRoundRect(
            color = tint,
            topLeft = Offset(w * 0.30f, h * 0.30f),
            size = Size(w * 0.55f, h * 0.55f),
            cornerRadius = CornerRadius(w * 0.08f, w * 0.08f),
            style = Stroke(width = stroke)
        )
    }
}

@Composable
fun LucideCheck(
    modifier: Modifier = Modifier,
    tint: Color = Color.White,
    size: Dp = 20.dp
) {
    Canvas(modifier = modifier.size(size)) {
        val stroke = LucideIcons.StrokeWidth.toPx()
        val w = this.size.width
        val h = this.size.height

        val check = Path().apply {
            moveTo(w * 0.20f, h * 0.52f)
            lineTo(w * 0.42f, h * 0.74f)
            lineTo(w * 0.82f, h * 0.28f)
        }
        drawPath(check, color = tint, style = Stroke(width = stroke * 1.2f, cap = StrokeCap.Round, join = StrokeJoin.Round))
    }
}

@Composable
fun LucideUndo(
    modifier: Modifier = Modifier,
    tint: Color = Color.White,
    size: Dp = 20.dp
) {
    LucideRotateCcw(modifier = modifier, tint = tint, size = size)
}

@Composable
fun LucideCamera(
    modifier: Modifier = Modifier,
    tint: Color = Color.White,
    size: Dp = 20.dp
) {
    Canvas(modifier = modifier.size(size)) {
        val stroke = LucideIcons.StrokeWidth.toPx()
        val w = this.size.width
        val h = this.size.height

        val body = Path().apply {
            moveTo(w * 0.15f, h * 0.32f)
            lineTo(w * 0.32f, h * 0.32f)
            lineTo(w * 0.38f, h * 0.20f)
            lineTo(w * 0.62f, h * 0.20f)
            lineTo(w * 0.68f, h * 0.32f)
            lineTo(w * 0.85f, h * 0.32f)
            cubicTo(w * 0.90f, h * 0.32f, w * 0.90f, h * 0.35f, w * 0.90f, h * 0.40f)
            lineTo(w * 0.90f, h * 0.82f)
            cubicTo(w * 0.90f, h * 0.86f, w * 0.86f, h * 0.86f, w * 0.82f, h * 0.86f)
            lineTo(w * 0.18f, h * 0.86f)
            cubicTo(w * 0.14f, h * 0.86f, w * 0.10f, h * 0.86f, w * 0.10f, h * 0.82f)
            lineTo(w * 0.10f, h * 0.40f)
            cubicTo(w * 0.10f, h * 0.35f, w * 0.10f, h * 0.32f, w * 0.15f, h * 0.32f)
            close()
        }
        drawPath(body, color = tint, style = Stroke(width = stroke, cap = StrokeCap.Round, join = StrokeJoin.Round))
        drawCircle(color = tint, radius = w * 0.18f, center = Offset(w * 0.50f, h * 0.58f), style = Stroke(width = stroke))
    }
}

