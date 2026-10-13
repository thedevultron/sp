package com.example

import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onRoot
import com.example.data.model.QuickActionType
import com.example.ui.capsule.FloatingCapsuleOverlay
import com.example.ui.theme.FluidCapsuleTheme
import com.github.takahirom.roborazzi.RobolectricDeviceQualifiers
import com.github.takahirom.roborazzi.captureRoboImage
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode

@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(qualifiers = RobolectricDeviceQualifiers.Pixel8, sdk = [36])
class GreetingScreenshotTest {

  @get:Rule val composeTestRule = createComposeRule()

  @Test
  fun capsule_screenshot() {
    composeTestRule.setContent {
      FluidCapsuleTheme {
        FloatingCapsuleOverlay(
          isRecording = false,
          isLiveTalkbackActive = false,
          amplitudes = listOf(0.2f, 0.4f, 0.6f, 0.4f, 0.2f),
          memoryUsageFraction = 0.35f,
          isMinimized = false,
          onToggleMinimize = {},
          onCloseClick = {},
          onRestartContextClick = {},
          onMicClick = {},
          onToggleTalkback = {},
          enableDragging = false
        )
      }
    }

    composeTestRule.onRoot().captureRoboImage(filePath = "src/test/screenshots/capsule.png")
  }
}
