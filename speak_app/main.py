import sys
import asyncio
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
import qasync

from src.config import config_vault, ASSETS_DIR
from src.audio_engine import AudioEngine
from src.screen_engine import ScreenEngine
from src.transcript_buffer import TranscriptBuffer
from src.gemini_client import GeminiLiveManager
from src.hotkeys import GlobalHotkeyListener
from src.tray import SpeakSystemTray
from src.session_manager import SessionManager
from src.permission_manager import permission_manager
from src.ui.floating_capsule import FloatingCapsuleWidget
from src.ui.settings_dialog import SettingsDialog
from src.ui.window_effects import enable_rounded_corners


class _Tee:
    """Split stdout/stderr to console + log file (never raises)."""
    def __init__(self, *streams):
        self._streams = [s for s in streams if s is not None]

    def write(self, data):
        for s in self._streams:
            try:
                s.write(data)
            except Exception:
                pass

    def flush(self):
        for s in self._streams:
            try:
                s.flush()
            except Exception:
                pass

    def isatty(self):
        return False


def _install_file_logging():
    """Tee console to %APPDATA%/SPEAK_AI/logs/speak-<stamp>.log (keep last 5).

    Real diagnostics beat symptom descriptions: after any failure, open the
    newest log and search [GeminiLive] / [ScreenEngine] / [AudioEngine].
    """
    try:
        import datetime as _dt
        from src.config import CONFIG_DIR
        logdir = CONFIG_DIR / "logs"
        try:
            logdir.mkdir(parents=True, exist_ok=True)
        except Exception:
            return None
        try:
            olds = sorted(logdir.glob("speak-*.log"), key=lambda p: p.stat().st_mtime)
            for p in olds[:-4]:
                try:
                    p.unlink()
                except Exception:
                    pass
        except Exception:
            pass
        try:
            stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
            fh = open(logdir / f"speak-{stamp}.log", "w", encoding="utf-8", buffering=1)
        except Exception:
            return None
        try:
            sys.stdout = _Tee(sys.stdout, fh)
            sys.stderr = _Tee(sys.stderr, fh)
        except Exception:
            pass
        try:
            print(f"[Log] writing to {fh.name}")
        except Exception:
            pass
        return str(fh.name)
    except Exception:
        return None


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
    FIX: always uses the LIVE height (expanded sheet included) so the
    transcript panel never extends underneath the taskbar (vertical cutoff).
    """
    screen = app.screenAt(capsule.geometry().center()) or app.primaryScreen()
    if not screen:
        return
    avail = screen.availableGeometry()
    if capsule.isVisible():
        w = capsule.width()
        h = capsule.height()
        # If sheet just toggled, height may still be stale — use sizeHint when bigger
        try:
            hint_h = capsule.sizeHint().height()
            if hint_h and hint_h > h:
                h = hint_h
        except Exception:
            pass
    else:
        # Not yet shown: force layout pass so sizeHint is accurate (DPI-safe)
        capsule.ensurePolished()
        w = capsule.sizeHint().width() or capsule.minimumWidth() or 680
        h = capsule.sizeHint().height() or capsule.minimumHeight() or 118
        if w > avail.width() - 40:
            w = max(600, avail.width() - 40)
        w = min(w, capsule.maximumWidth())
        # Never taller than available area (prevents under-taskbar growth)
        h = min(h, max(120, avail.height() - 16))
        capsule.resize(w, h)
    # Clamp height first so y calc is correct
    h = min(h, max(120, avail.height() - 16))
    x = avail.x() + int((avail.width() - w) / 2)
    y = avail.y() + avail.height() - h - 18
    x = max(avail.x() + 8, min(x, avail.x() + avail.width() - w - 8))
    y = max(avail.y() + 8, y)
    capsule.move(x, y)


def show_capsule(capsule: FloatingCapsuleWidget, app: QApplication):
    """Show, then re-position with the REAL post-show geometry.
    Fixes the 'cut off capsule' bug where it was positioned with a stale size."""
    from PySide6.QtCore import QTimer
    position_capsule(capsule, app)
    capsule.show()
    capsule.raise_()
    try:
        capsule.adjustSize()
    except Exception:
        pass
    def _reclamp():
        try:
            position_capsule(capsule, app)
        except Exception:
            pass
        try:
            capsule.update()
        except Exception:
            pass
        # Re-elide status now that the real width is known (fixes half-cut text)
        try:
            if hasattr(capsule, "_refresh_status_elision"):
                capsule._refresh_status_elision()
        except Exception:
            pass
    QTimer.singleShot(0, _reclamp)
    QTimer.singleShot(60, _reclamp)
    QTimer.singleShot(180, _reclamp)


def show_mini(capsule: FloatingCapsuleWidget, app: QApplication):
    """Primary reveal: the mini pill first (click/max expands to full).

    Same window, no recreation — minimize_to_mini only swaps which chrome
    is visible, so focus and session state survive the transition.
    """
    from PySide6.QtCore import QTimer
    try:
        if not capsule.isVisible():
            position_capsule(capsule, app)
            capsule.show()
            capsule.raise_()
    except Exception:
        pass
    try:
        capsule.minimize_to_mini()
    except Exception:
        pass
    try:
        position_capsule(capsule, app)
    except Exception:
        pass
    def _reclamp():
        try:
            position_capsule(capsule, app)
        except Exception:
            pass
        try:
            capsule.update()
        except Exception:
            pass
    QTimer.singleShot(60, _reclamp)
    QTimer.singleShot(180, _reclamp)


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
    transcript = TranscriptBuffer(autosave=config_vault.config.get("transcript_autosave", True))
    gemini = GeminiLiveManager(audio, screen, transcript_buffer=transcript)

    # 1b. Multi-Session Engine (FIFO, default 5)
    try:
        session_manager = SessionManager(max_stored=config_vault.get_max_stored_sessions())
    except Exception:
        session_manager = SessionManager(max_stored=5)
    # Seed first session record so count indicator is live from launch
    try:
        session_manager.spawn_session(mode="idle", model=config_vault.config.get("companion_model", ""))
        session_manager.mark_stored(session_manager.active_id())
    except Exception:
        pass

    # 1c. Proactive permission handshake BEFORE mic/screen worker init.
    # Screen AND microphone are both checked so the app never sends blank
    # frames or dead mic audio silently.
    try:
        perm_status = screen.check_permission()
        print(f"[Main] Screen permission pre-check: {perm_status}")
    except Exception as e:
        perm_status = "pending"
        print(f"[Main] Permission pre-check note: {e}")
    try:
        from src.permission_manager import mic_permission_manager as _mic_pm
        mic_status = _mic_pm.check_permission()
        print(f"[Main] Mic permission pre-check: {mic_status}")
    except Exception as e:
        mic_status = "pending"
        print(f"[Main] Mic pre-check note: {e}")

    # 2. UI Components — main window launches natively fullscreen (maximized)
    capsule = FloatingCapsuleWidget()
    try:
        settings_dialog = SettingsDialog(session_manager=session_manager)
    except TypeError:
        settings_dialog = SettingsDialog()
        try:
            settings_dialog.set_session_manager(session_manager)
        except Exception:
            pass
    tray = SpeakSystemTray()
    # Sync capsule screen toggle with config
    try:
        capsule.set_screen_enabled(bool(config_vault.config.get("enable_screen_share", True)))
    except Exception:
        pass

    # 3. CAPSULE HIDDEN ON STARTUP - only appears on hotkey/tray
    capsule.hide()
    # Pre-position so when it is shown it is already above taskbar
    position_capsule(capsule, app)
    try:
        app.primaryScreen().availableGeometryChanged.connect(lambda _: position_capsule(capsule, app))
        # Keep capsule inside the screen whenever sheet/resize/maximize changes it.
        # Uses the new sig_geometry_changed (no monkey-patching toggle_sheet).
        try:
            capsule.sig_geometry_changed.connect(lambda: position_capsule(capsule, app))
        except Exception:
            pass
        # Backward-compat: if an old capsule without the signal is ever used,
        # still re-clamp after toggle.
        try:
            if not hasattr(capsule, "sig_geometry_changed"):
                orig_toggle = capsule.toggle_sheet
                def wrapped_toggle():
                    orig_toggle()
                    from PySide6.QtCore import QTimer
                    QTimer.singleShot(40, lambda: position_capsule(capsule, app))
                capsule.toggle_sheet = wrapped_toggle
        except Exception:
            pass
    except Exception:
        pass

    # 4. SETTINGS DIALOG IS THE MAIN WINDOW — native fullscreen on launch
    try:
        settings_dialog.showMaximized()
        enable_rounded_corners(settings_dialog)
    except Exception:
        try:
            settings_dialog.show()
        except Exception:
            pass
    # Surface permission banner immediately if handshake did not grant.
    # Screen takes priority; mic shows when screen is fine but mic is blocked.
    try:
        diag = screen.permission_diagnostic()
        st = diag.get("status", perm_status)
        if st in ("granted", "unknown") and mic_status in ("denied", "pending"):
            try:
                from src.permission_manager import mic_permission_manager as _mpm2
                merr = _mpm2.last_error
            except Exception:
                merr = ""
            settings_dialog.update_permission_banner(
                mic_status,
                ("Microphone denied — dictation and companion cannot hear you. Click Grant Permission, allow mic access, then Grant again." if mic_status == "denied" else "Microphone permission pending — waiting for OS approval.") + (f" ({merr[:100]})" if merr else ""))
        else:
            settings_dialog.update_permission_banner(st, diag.get("banner_text", "") or diag.get("last_error", ""))
    except Exception:
        try:
            settings_dialog.update_permission_banner(perm_status, "")
        except Exception:
            pass
    settings_dialog.raise_()
    settings_dialog.activateWindow()

    def _on_grant_permission():
        """Explicit native OS authorization request + retry (never silent fail)."""
        try:
            settings_dialog._update_status("Requesting permission...", "orange")
        except Exception:
            pass
        try:
            # Offload blocking native prompt so UI stays responsive
            import threading as _th
            def _work():
                try:
                    st = screen.request_permission()
                except Exception as e:
                    st = "pending"
                    print(f"[Main] grant note: {e}")
                # Mic rides along: one Grant click requests both permissions
                try:
                    from src.permission_manager import mic_permission_manager as _mpm
                    _mst = _mpm.request_permission()
                    print(f"[Main] Mic grant result: {_mst}")
                except Exception as e:
                    print(f"[Main] mic grant note: {e}")
                try:
                    from PySide6.QtCore import QMetaObject as _QM, Qt as _Qt, Q_ARG as _QA
                    # Marshal back to GUI thread via signal-safe call
                    def _apply():
                        try:
                            diag2 = screen.permission_diagnostic()
                            settings_dialog.update_permission_banner(diag2.get("status", st), diag2.get("banner_text", "") or diag2.get("last_error", ""))
                            if diag2.get("status") == "granted":
                                tray.notify("Screen Ready", "Screen recording granted — live vision resumed.")
                                try:
                                    settings_dialog._update_status("Screen granted", "green")
                                except Exception:
                                    pass
                            else:
                                tray.notify("Permission Pending", "OS dialog shown — approve, then click Grant Permission again.")
                        except Exception as e:
                            print(f"[Main] banner apply note: {e}")
                    # Use singleShot to hop to GUI thread
                    from PySide6.QtCore import QTimer
                    QTimer.singleShot(0, _apply)
                except Exception:
                    pass
            _th.Thread(target=_work, daemon=True).start()
        except Exception as e:
            print(f"[Main] grant note: {e}")

    try:
        settings_dialog.sig_grant_permission_requested.connect(_on_grant_permission)
    except Exception:
        pass

    # When user clicks Save & Launch, refresh refine UI + notify - capsule stays hidden until hotkey
    def on_settings_saved():
        # Center capsule position but keep it hidden until hotkey/tray
        position_capsule(capsule, app)
        # Sync session threshold from Settings
        try:
            session_manager.set_max_stored(config_vault.get_max_stored_sessions())
        except Exception:
            pass
        try:
            settings_dialog.refresh_sessions_ui()
        except Exception:
            pass
        # New refine prompts/triggers/customs take effect immediately in capsule + tray
        try:
            if hasattr(capsule, "refresh_refine_actions"):
                capsule.refresh_refine_actions()
        except Exception:
            pass
        try:
            if hasattr(tray, "refresh_refine_menu"):
                tray.refresh_refine_menu()
        except Exception:
            pass
        # Don't auto-show capsule - user wants it only on shortcut
        # Just notify readiness
        tray.notify("SPEAK Ready", "Settings saved! Press Ctrl + Space to dictate or Ctrl + / for companion. Capsule will appear on hotkey.")
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
    # Additive transcript wiring (if capsule supports it)
    def _refine_display(act: str) -> str:
        try:
            a = str(act or "refine").strip().lower()
            if a in ("elaborate", "expand"):
                return "Elaborate"
            if a in ("refine", "polish"):
                return a.title()
            for c in config_vault.config.get("custom_actions", []) or []:
                if isinstance(c, dict) and c.get("id") == a:
                    return str(c.get("name", a) or a)[:24].title()
        except Exception:
            pass
        return str(act or "refine").title()
    def _on_refine_done(act, txt):
        try:
            capsule.set_refining(False)
        except Exception:
            pass
        try:
            words = len(str(txt or "").split())
            tray.notify(f"{_refine_display(act)} done", f"Session replaced \u2014 {words} words in target app.", 3500)
        except Exception:
            pass
        try:
            capsule.set_transcript(txt)
        except Exception:
            pass
    try:
        gemini.transcript_updated.connect(capsule.set_transcript)
        gemini.interim_updated.connect(capsule.set_interim)
        gemini.refine_started.connect(lambda act: capsule.set_refining(True, act))
        gemini.refine_completed.connect(_on_refine_done)
        gemini.refine_failed.connect(lambda err: (capsule.set_refining(False), tray.notify("Refine failed", str(err or "")[:120], 3500)))
        # init view
        capsule.set_transcript(transcript.full_text)
        # Session metadata live sync (chars/words for stored list)
        def _sync_session_stats(text: str):
            try:
                sid = session_manager.active_id()
                if not sid:
                    return
                c = len(str(text or ""))
                w = len(str(text or "").split()) if str(text or "").strip() else 0
                session_manager.update_transcript_stats(sid, c, w)
                try:
                    settings_dialog.refresh_sessions_ui()
                except Exception:
                    pass
            except Exception:
                pass
        try:
            gemini.transcript_updated.connect(_sync_session_stats)
        except Exception:
            pass
    except Exception as e:
        print(f"[Main] Transcript wiring {e}")

    # 7. Capsule Actions
    def open_settings(tab_index=0):
        try:
            settings_dialog.tabs.setCurrentIndex(tab_index)
        except Exception:
            pass
        if settings_dialog.isHidden():
            try:
                # Re-enter fullscreen natively
                if settings_dialog.isMaximized():
                    settings_dialog.showMaximized()
                else:
                    settings_dialog.showMaximized()
            except Exception:
                settings_dialog.show()
            app.processEvents()
        # Refresh permission banner every open (OS grant may have changed)
        try:
            st = screen.check_permission()
            diag = screen.permission_diagnostic()
            settings_dialog.update_permission_banner(diag.get("status", st), diag.get("banner_text", "") or diag.get("last_error", ""))
        except Exception:
            pass
        settings_dialog.raise_()
        settings_dialog.activateWindow()

    capsule.sig_open_settings.connect(lambda: open_settings(0))
    capsule.sig_open_tutorial.connect(lambda: open_settings(1))
    capsule.sig_close_session.connect(lambda: loop.create_task(gemini.stop_session()))
    # Live-screen toggle: capsule <-> gemini <-> settings checkbox (two-way, no loops)
    def _on_capsule_screen_toggle():
        try:
            new_state = not bool(getattr(gemini, "_screen_enabled", True))
            gemini.set_screen_enabled(new_state)
            try:
                capsule.set_screen_enabled(bool(gemini._screen_enabled))
            except Exception:
                pass
            try:
                if hasattr(settings_dialog, "chk_screen"):
                    settings_dialog.chk_screen.blockSignals(True)
                    settings_dialog.chk_screen.setChecked(bool(gemini._screen_enabled))
                    settings_dialog.chk_screen.blockSignals(False)
            except Exception:
                pass
            tray.notify("Live screen", "ON — live vision, bursts on change" if gemini._screen_enabled else "OFF — voice only", 1500)
        except Exception as e:
            print(f"[Main] capsule screen toggle note: {e}")
    try:
        capsule.sig_toggle_screen.connect(_on_capsule_screen_toggle)
    except Exception as e:
        print(f"[Main] screen toggle wiring {e}")
    # Additive refine wiring
    try:
        capsule.sig_refine.connect(lambda act: loop.create_task(gemini.trigger_refine(act)))
        capsule.sig_clear_transcript.connect(lambda: loop.create_task(gemini.purge_and_hard_reset()))
        capsule.sig_copy_transcript.connect(lambda: tray.notify("Copied", "Transcript copied to clipboard.", 1800))
    except Exception:
        pass

    # 8. Hotkeys -> Reveal MINI Capsule & Trigger AI (taskbar-aware)
    # Ctrl+Space dictation, Ctrl+/ companion, Ctrl+Win purge,
    # Ctrl+Tab spawns + switches to a new live session, Esc stops live only.
    # All triggers open the mini pill first; click/max expands to full.
    def trigger_dictation():
        show_mini(capsule, app)
        capsule.activateWindow()
        loop.create_task(gemini.start_dictation_mode())

    def trigger_companion():
        show_mini(capsule, app)
        capsule.activateWindow()
        loop.create_task(gemini.start_companion_mode())

    def trigger_purge():
        # Show mini briefly to give feedback even if it was hidden
        show_mini(capsule, app)
        capsule.activateWindow()
        loop.create_task(gemini.purge_and_hard_reset())

    def trigger_stop_live():
        # Esc: stop whatever is live (dictation/companion) — app keeps running.
        try:
            if not getattr(gemini, "_is_active", False):
                return
        except Exception:
            return
        print("[Main] Esc -> stop live session only")
        loop.create_task(gemini.stop_session())
        try:
            tray.notify("Stopped", "Live session stopped (Esc). App keeps running in tray.", 2000)
        except Exception:
            pass

    def trigger_new_session():
        """Ctrl+Tab: immediately spawn + switch to a new live session."""
        try:
            rec = session_manager.spawn_session(mode=gemini._current_mode if gemini._is_active else "companion")
            print(f"[Main] Ctrl+Tab new session {rec.session_id}")
        except Exception as e:
            print(f"[Main] session spawn note: {e}")
        try:
            settings_dialog.refresh_sessions_ui()
        except Exception:
            pass
        # Stop current live audio/screen, start fresh companion so the new
        # session is live immediately (FIFO already enforced by manager).
        async def _restart():
            try:
                await gemini.stop_session()
            except Exception:
                pass
            await asyncio.sleep(0.25)
            show_mini(capsule, app)
            try:
                capsule.activateWindow()
            except Exception:
                pass
            try:
                await gemini.start_companion_mode()
            except Exception as e:
                print(f"[Main] new session start note: {e}")
            try:
                settings_dialog.refresh_sessions_ui()
            except Exception:
                pass
            try:
                tray.notify("New Session", f"Switched to live session {session_manager.active_id() or ''} (Ctrl+Tab).")
            except Exception:
                pass
        loop.create_task(_restart())

    hotkeys = GlobalHotkeyListener()
    hotkeys.sig_toggle_dictation.connect(trigger_dictation)
    hotkeys.sig_toggle_companion.connect(trigger_companion)
    hotkeys.sig_purge_reset.connect(trigger_purge)
    try:
        hotkeys.sig_new_session.connect(trigger_new_session)
    except Exception:
        pass
    try:
        hotkeys.sig_stop_live.connect(trigger_stop_live)
    except Exception:
        pass
    hotkeys.start()
    # Window-level Ctrl+Tab fallback (when global hook is suppressed by focus)
    try:
        from PySide6.QtGui import QShortcut, QKeySequence
        sc = QShortcut(QKeySequence("Ctrl+Tab"), settings_dialog)
        sc.setContext(Qt.ShortcutContext.ApplicationShortcut)
        sc.activated.connect(trigger_new_session)
        # keep ref
        settings_dialog._ctrl_tab_shortcut = sc
    except Exception as e:
        print(f"[Main] window Ctrl+Tab note: {e}")
    try:
        settings_dialog.sig_new_session_requested.connect(trigger_new_session)
    except Exception:
        pass

    # 9. Tray Actions
    tray.show_setup_requested.connect(lambda: open_settings(1))
    tray.show_settings_requested.connect(lambda: open_settings(0))
    # Keep Settings checkbox <-> gemini <-> capsule in sync (no signal loops)
    def _on_settings_screen_toggle(checked: bool):
        try:
            gemini.set_screen_enabled(bool(checked))
        except Exception:
            pass
        try:
            capsule.set_screen_enabled(bool(checked))
        except Exception:
            pass
    try:
        if hasattr(settings_dialog, 'chk_screen'):
            settings_dialog.chk_screen.toggled.connect(_on_settings_screen_toggle)
    except Exception:
        pass

    def toggle_capsule():
        if capsule.isVisible():
            capsule.hide()
        else:
            show_mini(capsule, app)
            capsule.activateWindow()

    tray.toggle_capsule_requested.connect(toggle_capsule)
    tray.dictation_requested.connect(trigger_dictation)
    tray.companion_requested.connect(trigger_companion)
    tray.purge_requested.connect(trigger_purge)
    try:
        tray.refine_requested.connect(lambda act: loop.create_task(gemini.trigger_refine(act)))
    except Exception:
        pass

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
    # Loud permission verdicts (never silent blank frames / dead mic)
    try:
        if mic_status in ("denied", "pending"):
            await asyncio.sleep(0.4)
            tray.notify("Microphone blocked", "Allow mic access: Settings will offer Grant, or open Windows Privacy > Microphone.", 4500)
    except Exception:
        pass
    try:
        if perm_status in ("denied", "pending"):
            await asyncio.sleep(0.4)
            tray.notify("Screen blocked", "Live vision paused — click Grant Permission in Settings.", 4500)
    except Exception:
        pass
    # Unmissable ask: modal permission dialog when mic or screen is blocked.
    # (A banner alone was overlooked — blank vision with no prompt.)
    try:
        if mic_status in ("denied", "pending") or perm_status in ("denied", "pending"):
            from src.ui.permission_dialog import PermissionAskDialog
            dlg = PermissionAskDialog(settings_dialog)
            try:
                dlg.exec()
            except Exception:
                try:
                    dlg.show()
                except Exception:
                    pass
            # Re-read verdicts after the user grants/closes
            try:
                diag = screen.permission_diagnostic()
                settings_dialog.update_permission_banner(diag.get("status", perm_status), diag.get("banner_text", "") or diag.get("last_error", ""))
            except Exception:
                pass
    except Exception as e:
        print(f"[Main] permission modal note: {e}")

    # Keep event loop alive forever (qasync requires this)
    while True:
        await asyncio.sleep(3600)


def main():
    # File log first: every run leaves evidence at %APPDATA%/SPEAK_AI/logs/.
    try:
        _install_file_logging()
    except Exception:
        pass
    # Must be called before QApplication is created per Qt docs
    try:
        from PySide6.QtGui import QGuiApplication
        QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    except Exception:
        pass
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("SPEAK")
    app.setOrganizationName("Amir Bagawan")

    # ---- Single-instance guard: prevents double hotkeys / double mic ----
    _lock = None
    try:
        from PySide6.QtCore import QLockFile
        from PySide6.QtCore import QStandardPaths
        import os as _os
        from pathlib import Path as _Path
        lock_dir = _Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.TempLocation)) / "SPEAK_AI"
        try:
            lock_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        lock_path = str(lock_dir / "speak_single_instance.lock")
        _lock = QLockFile(lock_path)
        try:
            _lock.setStaleLockTime(0)
        except Exception:
            pass
        if not _lock.tryLock(100):
            # Another instance is running — nudge it via tray-less message and exit.
            # Use a native message box (no new deps) so the user understands.
            try:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(
                    None, "SPEAK already running",
                    "SPEAK is already running.\nCheck the system tray near the clock (press Ctrl+Space to show the capsule)."
                )
            except Exception:
                pass
            sys.exit(0)
    except SystemExit:
        raise
    except Exception as e:
        print(f"[Main] single-instance guard note: {e}")
        _lock = None

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
            _msg = str(e)
            if "Event loop stopped before Future completed" in _msg:
                pass  # benign qasync teardown race on app exit, not a failure
            else:
                print(f"[Main] Fatal error: {e}")
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    main()
