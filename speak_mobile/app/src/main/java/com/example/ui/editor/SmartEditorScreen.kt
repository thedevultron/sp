package com.example.ui.editor

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.widget.Toast
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.TextRange
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.TextFieldValue
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.SpokenReplacementRecord
import com.example.data.model.QuickActionType
import com.example.ui.components.GlassCard
import com.example.ui.components.LucideSparkles
import com.example.ui.components.LucideRotateCcw
import com.example.ui.theme.LocalGlassTokens
import com.example.ui.theme.PrecisionCyan

@Composable
fun SmartEditorScreen(
    currentText: String,
    onTextChange: (String) -> Unit,
    liveStreamingTranscript: String,
    trackedSpokenWords: String = "",
    lastReplacement: SpokenReplacementRecord? = null,
    onApplyTransformation: (QuickActionType, String) -> Unit,
    onUndoReplacement: () -> Unit = {},
    onSaveNote: (String, String) -> Unit,
    isTransforming: Boolean,
    onFocusTextBox: () -> Unit = {},
    modifier: Modifier = Modifier
) {
    val tokens = LocalGlassTokens.current
    val context = LocalContext.current

    var noteTitle by remember { mutableStateOf("Voice Note") }
    var textFieldValue by remember { mutableStateOf(TextFieldValue(currentText, TextRange(currentText.length))) }

    // Keep textFieldValue in sync when external text changes
    LaunchedEffect(currentText) {
        if (textFieldValue.text != currentText) {
            val newCursor = currentText.length.coerceAtLeast(0)
            textFieldValue = TextFieldValue(
                text = currentText,
                selection = TextRange(newCursor)
            )
        }
    }

    val selectedText = remember(textFieldValue) {
        if (textFieldValue.selection.collapsed) ""
        else textFieldValue.text.substring(
            textFieldValue.selection.min,
            textFieldValue.selection.max
        )
    }

    val wordCount = remember(textFieldValue.text) {
        if (textFieldValue.text.isBlank()) 0 else textFieldValue.text.trim().split("\\s+".toRegex()).size
    }
    val charCount = textFieldValue.text.length

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(tokens.background)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .statusBarsPadding()
                .padding(horizontal = 20.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            // Header Bar: Title and Word Counter
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 12.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "Smart Editor",
                        style = MaterialTheme.typography.headlineLarge,
                        color = tokens.textPrimary
                    )
                    Text(
                        text = "$wordCount words • $charCount characters",
                        style = MaterialTheme.typography.labelSmall,
                        color = tokens.textSecondary
                    )
                }

                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    // Copy Action
                    IconButton(
                        onClick = {
                            val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                            clipboard.setPrimaryClip(ClipData.newPlainText("Smart Note", currentText))
                            Toast.makeText(context, "Copied to clipboard", Toast.LENGTH_SHORT).show()
                        },
                        modifier = Modifier.testTag("editor_copy_button")
                    ) {
                        Text(text = "Copy", color = Color.White, fontSize = 13.sp, fontWeight = FontWeight.Medium)
                    }

                    // Share Action
                    IconButton(
                        onClick = {
                            val shareIntent = Intent(Intent.ACTION_SEND).apply {
                                type = "text/plain"
                                putExtra(Intent.EXTRA_TEXT, currentText)
                            }
                            context.startActivity(Intent.createChooser(shareIntent, "Share note"))
                        },
                        modifier = Modifier.testTag("editor_share_button")
                    ) {
                        Text(text = "Share", color = Color.White, fontSize = 13.sp, fontWeight = FontWeight.Medium)
                    }
                }
            }

            // Quick AI Transformation Ribbon
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                // Tracking or Selection State Feedback
                if (selectedText.isNotEmpty()) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 4.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(6.dp)
                                .clip(CircleShape)
                                .background(PrecisionCyan)
                        )
                        Text(
                            text = "Target selection: \"${selectedText.take(28)}${if (selectedText.length > 28) "..." else ""}\"",
                            color = PrecisionCyan,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Medium
                        )
                    }
                } else if (trackedSpokenWords.isNotBlank() && textFieldValue.text.contains(trackedSpokenWords)) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 4.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(6.dp)
                                .clip(CircleShape)
                                .background(Color(0xFF4ADE80))
                        )
                        Text(
                            text = "Spoken segment tracked (${trackedSpokenWords.trim().split("\\s+".toRegex()).size} words): \"${trackedSpokenWords.take(30)}...\"",
                            color = Color(0xFF4ADE80),
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Medium
                        )
                    }
                }

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .horizontalScroll(rememberScrollState()),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    QuickActionType.entries.forEach { action ->
                        val targetSegment = when {
                            selectedText.isNotBlank() -> selectedText
                            trackedSpokenWords.isNotBlank() && textFieldValue.text.contains(trackedSpokenWords) -> trackedSpokenWords
                            else -> textFieldValue.text
                        }
                        QuickActionChip(
                            action = action,
                            onClick = { onApplyTransformation(action, targetSegment) },
                            tokens = tokens
                        )
                    }
                }
            }

            // Undo / Revert In-Place Replacement Banner
            if (lastReplacement != null) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(10.dp))
                        .background(Color(0x1E4ADE80))
                        .border(BorderStroke(0.75.dp, Color(0x554ADE80)), RoundedCornerShape(10.dp))
                        .clickable(onClick = onUndoReplacement)
                        .padding(horizontal = 12.dp, vertical = 6.dp)
                        .testTag("undo_replacement_banner"),
                    contentAlignment = Alignment.CenterStart
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            LucideRotateCcw(tint = Color(0xFF4ADE80), size = 14.dp)
                            Text(
                                text = "Replaced original: \"${lastReplacement.originalSpokenText.take(24)}...\"",
                                color = Color.White,
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Medium
                            )
                        }
                        Text(
                            text = "↺ Undo",
                            color = Color(0xFF4ADE80),
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }

            // Markdown Formatting Toolbar
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                FormatButton("H1", onClick = { onTextChange("# $currentText") })
                FormatButton("H2", onClick = { onTextChange("## $currentText") })
                FormatButton("Bold", onClick = { onTextChange("$currentText **bold**") })
                FormatButton("Italic", onClick = { onTextChange("$currentText *italic*") })
                FormatButton("List", onClick = { onTextChange("$currentText\n- ") })
                FormatButton("Quote", onClick = { onTextChange("$currentText\n> ") })
                FormatButton("Code", onClick = { onTextChange("$currentText\n```\n\n```") })
            }

            // Transforming Feedback Banner
            AnimatedVisibility(
                visible = isTransforming,
                enter = fadeIn(),
                exit = fadeOut()
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(8.dp))
                        .background(Color(0x22FFFFFF))
                        .border(BorderStroke(0.5.dp, Color(0x44FFFFFF)), RoundedCornerShape(8.dp))
                        .padding(horizontal = 12.dp, vertical = 6.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "Refining & replacing original text in place (gemini-3.5-flash-lite)...",
                        color = PrecisionCyan,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Medium
                    )
                }
            }

            // Main Editor Surface
            GlassCard(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f),
                contentPadding = 16.dp
            ) {
                Column(modifier = Modifier.fillMaxSize()) {
                    OutlinedTextField(
                        value = noteTitle,
                        onValueChange = {
                            noteTitle = it
                            onFocusTextBox()
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .onFocusChanged { if (it.isFocused) onFocusTextBox() },
                        placeholder = { Text("Note Title...", color = tokens.textSecondary) },
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedTextColor = tokens.textPrimary,
                            unfocusedTextColor = tokens.textPrimary,
                            focusedBorderColor = Color.Transparent,
                            unfocusedBorderColor = Color.Transparent
                        ),
                        textStyle = MaterialTheme.typography.titleLarge
                    )

                    HorizontalDivider(
                        color = Color(0x22FFFFFF),
                        thickness = 0.5.dp,
                        modifier = Modifier.padding(vertical = 4.dp)
                    )

                    OutlinedTextField(
                        value = textFieldValue,
                        onValueChange = {
                            textFieldValue = it
                            onTextChange(it.text)
                            onFocusTextBox()
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .weight(1f)
                            .onFocusChanged { if (it.isFocused) onFocusTextBox() }
                            .testTag("smart_editor_text_area"),
                        placeholder = {
                            Text(
                                text = "Speak or type your document here. Speech streams in real time...",
                                color = tokens.textSecondary
                            )
                        },
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedTextColor = tokens.textPrimary,
                            unfocusedTextColor = tokens.textPrimary,
                            focusedBorderColor = Color.Transparent,
                            unfocusedBorderColor = Color.Transparent
                        ),
                        textStyle = MaterialTheme.typography.bodyLarge.copy(
                            fontFamily = FontFamily.SansSerif,
                            lineHeight = 24.sp
                        )
                    )
                }
            }

            // Bottom Save & Action Row
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 96.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                TextButton(
                    onClick = { onTextChange("") },
                    modifier = Modifier.testTag("editor_clear_button")
                ) {
                    Text(text = "Clear Text", color = tokens.textSecondary, fontSize = 13.sp)
                }

                Button(
                    onClick = {
                        onSaveNote(noteTitle, currentText)
                        Toast.makeText(context, "Note saved to local database", Toast.LENGTH_SHORT).show()
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color.White,
                        contentColor = Color.Black
                    ),
                    shape = RoundedCornerShape(16.dp),
                    modifier = Modifier.testTag("editor_save_button")
                ) {
                    Text(text = "Save Draft", color = Color.Black, fontSize = 14.sp, fontWeight = FontWeight.SemiBold)
                }
            }
        }
    }
}

@Composable
private fun QuickActionChip(
    action: QuickActionType,
    onClick: () -> Unit,
    tokens: com.example.ui.theme.GlassTokens
) {
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(16.dp))
            .background(Color(0x1AFFFFFF))
            .border(BorderStroke(0.5.dp, Color(0x33FFFFFF)), RoundedCornerShape(16.dp))
            .clickable(onClick = onClick)
            .padding(horizontal = 12.dp, vertical = 6.dp)
            .testTag("quick_action_${action.id}")
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            LucideSparkles(tint = Color.White, size = 14.dp)
            Text(
                text = action.label,
                color = tokens.textPrimary,
                fontSize = 12.sp,
                fontWeight = FontWeight.Medium
            )
        }
    }
}

@Composable
private fun FormatButton(
    label: String,
    onClick: () -> Unit
) {
    val tokens = LocalGlassTokens.current
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(8.dp))
            .background(Color(0x1AFFFFFF))
            .clickable(onClick = onClick)
            .padding(horizontal = 10.dp, vertical = 4.dp)
    ) {
        Text(
            text = label,
            color = tokens.textSecondary,
            fontSize = 11.sp,
            fontFamily = FontFamily.Monospace,
            fontWeight = FontWeight.SemiBold
        )
    }
}

