package com.example.ui.components

import androidx.compose.animation.animateColorAsState
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.theme.LocalGlassTokens

enum class MainDestination(val title: String) {
    HOME("Speak"),
    EDITOR("Editor"),
    SESSIONS("Sessions"),
    SETTINGS("Settings")
}

@Composable
fun ElevatedBottomBar(
    currentDestination: MainDestination,
    onDestinationSelected: (MainDestination) -> Unit,
    modifier: Modifier = Modifier
) {
    val tokens = LocalGlassTokens.current

    Box(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 10.dp),
        contentAlignment = Alignment.BottomCenter
    ) {
        // Frosted Midnight Dock Bar
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(62.dp)
                .shadow(16.dp, RoundedCornerShape(32.dp), ambientColor = Color(0x40000000), spotColor = Color(0x60000000))
                .clip(RoundedCornerShape(32.dp))
                .background(tokens.surfaceGlass)
                .border(BorderStroke(0.5.dp, tokens.borderGlass), RoundedCornerShape(32.dp))
                .padding(horizontal = 8.dp),
            contentAlignment = Alignment.Center
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Tab 1: Speak Live Console
                NavItem(
                    label = "Speak",
                    isSelected = currentDestination == MainDestination.HOME,
                    onClick = { onDestinationSelected(MainDestination.HOME) },
                    testTag = "nav_home_button"
                ) { tint ->
                    LucideMic(tint = tint, size = 20.dp)
                }

                // Tab 2: Smart Editor
                NavItem(
                    label = "Editor",
                    isSelected = currentDestination == MainDestination.EDITOR,
                    onClick = { onDestinationSelected(MainDestination.EDITOR) },
                    testTag = "nav_editor_button"
                ) { tint ->
                    LucideFileText(tint = tint, size = 20.dp)
                }

                // Tab 3: Multi-Session Engine
                NavItem(
                    label = "Sessions",
                    isSelected = currentDestination == MainDestination.SESSIONS,
                    onClick = { onDestinationSelected(MainDestination.SESSIONS) },
                    testTag = "nav_sessions_button"
                ) { tint ->
                    LucideLayers(tint = tint, size = 20.dp)
                }

                // Tab 4: Vault & Settings
                NavItem(
                    label = "Settings",
                    isSelected = currentDestination == MainDestination.SETTINGS,
                    onClick = { onDestinationSelected(MainDestination.SETTINGS) },
                    testTag = "nav_settings_button"
                ) { tint ->
                    LucideSettings(tint = tint, size = 20.dp)
                }
            }
        }
    }
}

@Composable
private fun NavItem(
    label: String,
    isSelected: Boolean,
    onClick: () -> Unit,
    testTag: String,
    icon: @Composable (tint: Color) -> Unit
) {
    val tokens = LocalGlassTokens.current
    val tint by animateColorAsState(
        targetValue = if (isSelected) Color.White else tokens.textSecondary,
        label = "nav_tint"
    )

    val itemBg = if (isSelected) Color(0x22663AF3) else Color.Transparent

    Column(
        modifier = Modifier
            .clip(RoundedCornerShape(16.dp))
            .background(itemBg)
            .clickable(onClick = onClick)
            .padding(horizontal = 14.dp, vertical = 6.dp)
            .testTag(testTag),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        icon(tint)
        Spacer(modifier = Modifier.height(2.dp))
        Text(
            text = label,
            color = tint,
            fontSize = 11.sp,
            fontWeight = if (isSelected) FontWeight.SemiBold else FontWeight.Normal
        )
    }
}
