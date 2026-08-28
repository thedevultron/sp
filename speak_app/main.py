import sys
import asyncio
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
import qasync

from src.config import config_vault, ASSETS_DIR
from src.audio_engine import AudioEngine
from src.screen_engine import ScreenEngine
from src.gemini_client import GeminiLiveManager
from src.hotkeys import GlobalHotkeyListener
from src.tray import SpeakSystemTray
from src.ui.floating_capsule import FloatingCapsuleWidget
from src.ui.screen_canvas import ScreenCanvasOverlay
from src.ui.settings_dialog import SettingsDialog


def apply_stylesheet(app: QApplication):
    qss = ASSETS_DIR / "capsule_style.qss"
    if qss.exists():
        try:
            with open(qss, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
        except Exception as e:
            print(f"[Style] Failed to load QSS: {e}")


def position_capsule(capsule: FloatingCapsuleWidget, app: QApplication):
    """Positions the floating capsule centered directly above the Windows taskbar.
    Uses availableGeometry() so the pill is never hidden behind the taskbar.
    Works correctly on multi-monitor and high-DPI setups.
    """
    screen = app.primaryScreen()
    if not screen:
        return
    avail = screen.availableGeometry()
    if capsule.isVisible():
        w = capsule.width()
        h = capsule.height()
    else:
        w = capsule.sizeHint().width() or capsule.minimumWidth() or 380
        h = capsule.sizeHint().height() or capsule.height() or 58
        if w < 340:
            w = 380
        if w > avail.width() - 20:
            w = max(380, avail.width() - 40)
        if h < 30:
            h = 58
    if w < 200:
        w = 380
    if h < 20:
        h = 58
    x = avail.x() + int((avail.width() - w) / 2)
    y = avail.y() + avail.height() - h - 18
    x = max(avail.x() + 8, min(x, avail.x() + avail.width() - w - 8))
    y = max(avail.y() + 8, y)
    capsule.move(x, y)


def center_window_on_screen(window, app: QApplication):
    """Centers any window/dialog on the primary screen available geometry."""
    screen = app.primaryScreen()
    if not screen:
        return
    avail = screen.availableGeometry()
    geo = window.frameGeometry()
    x = avail.x() + int((avail.width() - geo.width()) / 2)
    y = avail.y() + int((avail.height() - geo.height()) / 2)
    # Ensure not under taskbar, clamp
    window.move(max(avail.x(), x), max(avail.y(), y))


async def main_async(app: QApplication):
    loop = asyncio.get_running_loop()

    # 1. Initialize Engines
    audio = AudioEngine()
    audio.set_loop(loop)
    screen = ScreenEngine()
    gemini = GeminiLiveManager(audio, screen)

    # 2. UI Components
    capsule = FloatingCapsuleWidget()
    canvas = ScreenCanvasOverlay()
    settings_dialog = SettingsDialog()
    tray = SpeakSystemTray()

    # 3. CAPSULE HIDDEN ON STARTUP - only appears on hotkey/tray
    capsule.hide()
    # Pre-position so when it is shown it is already above taskbar
    position_capsule(capsule, app)
    try:
        app.primaryScreen().availableGeometryChanged.connect(lambda _: position_capsule(capsule, app))
    except Exception:
        pass

    # 4. SETTINGS DIALOG IS THE MAIN WINDOW - always show on launch, centered
    # This is the "Windows dialog box" user expects when double-clicking main.py
    settings_dialog.show()
    # Center it nicely after show (size is known after show)
    app.processEvents()
    center_window_on_screen(settings_dialog, app)
    settings_dialog.raise_()
    settings_dialog.activateWindow()

    # When user clicks Save & Launch, hide dialog (not capsule) and notify - capsule stays hidden until hotkey
    def on_settings_saved():
        # Center capsule position but keep it hidden until hotkey/tray
        position_capsule(capsule, app)
        # Don't auto-show capsule - user wants it only on shortcut
        # Just notify readiness
        tray.notify("SPEAK Ready", "Settings saved! Press Ctrl + Space to dictate or Win+Shift for companion. Capsule will appear on hotkey.")
        # Keep settings dialog hidden after save (user can reopen via tray/capsule)
        # Dialog already accepted/closed by SettingsDialog._save_and_close()

    settings_dialog.accepted.connect(on_settings_saved)
    # If user closes dialog with X, just hide it, keep app running in tray
    settings_dialog.rejected.connect(lambda: tray.notify("SPEAK Running", "SPEAK is in system tray. Press hotkeys or click tray icon for settings."))

    # 5. Connect Audio Wave Visualizer (only visible when capsule shown)
    audio.amplitude_changed.connect(capsule.wave_visualizer.set_mic_rms)
    audio.gemini_output_amplitude.connect(capsule.wave_visualizer.set_gemini_rms)

    # 6. Connect Status & Alerts
    gemini.status_changed.connect(capsule.set_status)
    gemini.token_usage_updated.connect(capsule.token_bar.set_tokens)
    gemini.error_occurred.connect(lambda err: tray.notify("SPEAK Alert", err))

    # 7. Capsule Actions
    def on_toggle_canvas():
        if canvas.isHidden():
            canvas.show_canvas()
        else:
            canvas.hide()

    def open_settings(tab_index=0):
        try:
            settings_dialog.tabs.setCurrentIndex(tab_index)
        except Exception:
            pass
        if settings_dialog.isHidden():
            settings_dialog.show()
            app.processEvents()
            center_window_on_screen(settings_dialog, app)
        settings_dialog.raise_()
        settings_dialog.activateWindow()

    capsule.sig_toggle_canvas.connect(on_toggle_canvas)
    capsule.sig_open_settings.connect(lambda: open_settings(0))
    capsule.sig_open_tutorial.connect(lambda: open_settings(1))
    capsule.sig_close_session.connect(lambda: loop.create_task(gemini.stop_session()))

    # 8. Hotkeys -> Reveal Capsule & Trigger AI (taskbar-aware)
    def trigger_dictation():
        position_capsule(capsule, app)
        capsule.show()
        capsule.raise_()
        capsule.activateWindow()
        loop.create_task(gemini.start_dictation_mode())

    def trigger_companion():
        position_capsule(capsule, app)
        capsule.show()
        capsule.raise_()
        capsule.activateWindow()
        loop.create_task(gemini.start_companion_mode())

    def trigger_purge():
        # Show capsule briefly to give feedback even if it was hidden
        position_capsule(capsule, app)
        capsule.show()
        capsule.raise_()
        capsule.activateWindow()
        loop.create_task(gemini.purge_and_hard_reset())

    hotkeys = GlobalHotkeyListener()
    hotkeys.sig_toggle_dictation.connect(trigger_dictation)
    hotkeys.sig_toggle_companion.connect(trigger_companion)
    hotkeys.sig_purge_reset.connect(trigger_purge)
    hotkeys.start()

    # 9. Tray Actions
    tray.show_setup_requested.connect(lambda: open_settings(1))
    tray.show_settings_requested.connect(lambda: open_settings(0))

    def toggle_capsule():
        if capsule.isVisible():
            capsule.hide()
        else:
            position_capsule(capsule, app)
            capsule.show()
            capsule.raise_()
            capsule.activateWindow()

    tray.toggle_capsule_requested.connect(toggle_capsule)
    tray.dictation_requested.connect(trigger_dictation)
    tray.companion_requested.connect(trigger_companion)
    tray.purge_requested.connect(trigger_purge)

    async def quit_app():
        try:
            hotkeys.stop()
        except Exception:
            pass
        try:
            await gemini.stop_session()
        except Exception:
            pass
        await asyncio.sleep(0.15)
        app.quit()

    tray.quit_requested.connect(lambda: loop.create_task(quit_app()))
    tray.show()
    # Delay notify slightly so tray is registered on Windows
    await asyncio.sleep(0.6)
    tray.notify("SPEAK Running", "Settings window is open. Capsule is hidden until you press Ctrl+Space. Find SPEAK in system tray.")

    # Keep event loop alive forever (qasync requires this)
    while True:
        await asyncio.sleep(3600)


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    try:
        app.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    except Exception:
        pass

    apply_stylesheet(app)

    try:
        from PySide6.QtGui import QIcon
        from src.config import ICON_PATH
        if ICON_PATH.exists():
            app.setWindowIcon(QIcon(str(ICON_PATH)))
    except Exception:
        pass

    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    with loop:
        try:
            loop.run_until_complete(main_async(app))
        except (KeyboardInterrupt, SystemExit):
            pass
        except Exception as e:
            print(f"[Main] Fatal error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
