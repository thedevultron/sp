from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QObject, Signal
from src.config import ICON_PATH


class SpeakSystemTray(QObject):
    """Windows Taskbar & System Tray manager - fixed icon loading and reliability."""

    show_setup_requested = Signal()
    show_settings_requested = Signal()
    toggle_capsule_requested = Signal()
    dictation_requested = Signal()
    companion_requested = Signal()
    purge_requested = Signal()
    quit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray = QSystemTrayIcon(parent)
        # Robust icon loading: try multiple fallbacks, ensure QIcon has QApp context
        icon_loaded = False
        try:
            if ICON_PATH.exists():
                icon = QIcon(str(ICON_PATH))
                if not icon.isNull():
                    self.tray.setIcon(icon)
                    # Also set app icon if possible
                    try:
                        if QApplication.instance():
                            QApplication.instance().setWindowIcon(icon)
                    except Exception:
                        pass
                    icon_loaded = True
        except Exception as e:
            print(f"[Tray] Icon load error: {e}")

        if not icon_loaded:
            # Fallback to style icon
            try:
                self.tray.setIcon(QApplication.style().standardIcon(QApplication.style().SP_ComputerIcon))
            except Exception:
                pass

        self.tray.setToolTip("SPEAK — Voice & Vision AI  •  Ctrl+Space to dictate")

        self._build_menu()
        self.tray.activated.connect(self._on_activated)
        # Handle message clicked
        try:
            self.tray.messageClicked.connect(self._on_message_clicked)
        except Exception:
            pass

    def _build_menu(self):
        menu = QMenu()
        # Styling for menu polish
        try:
            menu.setStyleSheet("QMenu { background: #1C1C22; border: 1px solid #28282E; border-radius: 8px; padding: 6px; } QMenu::item { padding: 7px 20px; border-radius: 6px; } QMenu::item:selected { background: #2A2A32; color: #DA7756; } QMenu::separator { height: 1px; background: #28282E; margin: 6px 8px; }")
        except Exception:
            pass

        act_capsule = QAction("👁 Show / Hide Capsule", menu)
        act_capsule.triggered.connect(self.toggle_capsule_requested.emit)
        menu.addAction(act_capsule)

        menu.addSeparator()

        act_dictate = QAction("🎙 Live Voice Dictation  (Ctrl + Space)", menu)
        act_dictate.triggered.connect(self.dictation_requested.emit)
        menu.addAction(act_dictate)

        act_comp = QAction("👁️ Live Companion Mode  (Win + Shift)", menu)
        act_comp.triggered.connect(self.companion_requested.emit)
        menu.addAction(act_comp)

        act_purge = QAction("🧠 Purge Context Buffer  (Ctrl + Win)", menu)
        act_purge.triggered.connect(self.purge_requested.emit)
        menu.addAction(act_purge)

        menu.addSeparator()

        act_setup = QAction("📖 Setup Wizard & Tutorial…", menu)
        act_setup.triggered.connect(self.show_setup_requested.emit)
        menu.addAction(act_setup)

        act_settings = QAction("⚙️ Settings & API Vault…", menu)
        act_settings.triggered.connect(self.show_settings_requested.emit)
        menu.addAction(act_settings)

        menu.addSeparator()

        act_exit = QAction("❌ Exit SPEAK", menu)
        act_exit.triggered.connect(self.quit_requested.emit)
        menu.addAction(act_exit)

        self.tray.setContextMenu(menu)
        self._menu = menu

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_capsule_requested.emit()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.toggle_capsule_requested.emit()
        elif reason == QSystemTrayIcon.ActivationReason.Context:
            pass

    def _on_message_clicked(self):
        self.toggle_capsule_requested.emit()

    def show(self):
        if not self.tray.isSystemTrayAvailable():
            print("[Tray] System tray not available on this platform")
        self.tray.show()
        # Verify visible
        if not self.tray.isVisible():
            print("[Tray] Warning: tray icon not visible after show()")
        else:
            print("[Tray] Tray icon visible")

    def notify(self, title: str, message: str, duration_ms: int = 2800):
        try:
            # Ensure tray is shown first
            if not self.tray.isVisible():
                self.tray.show()
            self.tray.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, duration_ms)
        except Exception as e:
            print(f"[Tray] Notify error: {e}")

    def is_visible(self) -> bool:
        return self.tray.isVisible()
