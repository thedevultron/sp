from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QObject, Signal
from src.config import ICON_PATH
from src.ui.icons import icon as lucide_icon

class SpeakSystemTray(QObject):
    """Minimal tray — lucide icons, no emojis, Apple/Stripe restrained palette."""

    show_setup_requested = Signal()
    show_settings_requested = Signal()
    toggle_capsule_requested = Signal()
    dictation_requested = Signal()
    companion_requested = Signal()
    purge_requested = Signal()
    refine_requested = Signal(str)
    quit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray = QSystemTrayIcon(parent)
        icon_loaded = False
        try:
            if ICON_PATH.exists():
                icon = QIcon(str(ICON_PATH))
                if not icon.isNull():
                    self.tray.setIcon(icon)
                    try:
                        if QApplication.instance():
                            QApplication.instance().setWindowIcon(icon)
                    except Exception:
                        pass
                    icon_loaded = True
        except Exception as e:
            print(f"[Tray] Icon load error: {e}")
        if not icon_loaded:
            try:
                self.tray.setIcon(QApplication.style().standardIcon(QApplication.style().SP_ComputerIcon))
            except Exception:
                pass
        self.tray.setToolTip("SPEAK  \u00b7  Ctrl+Space to dictate")

        self._build_menu()
        self.tray.activated.connect(self._on_activated)
        try:
            self.tray.messageClicked.connect(self._on_message_clicked)
        except Exception:
            pass

    def _build_menu(self):
        menu = QMenu()
        try:
            menu.setStyleSheet(
                "QMenu { background: #0B1023; border: 1px solid #1FBAD7F7; border-radius: 6px; padding: 6px; }"
                " QMenu::item { padding: 7px 16px; border-radius: 6px; color: #D1E4FA; font-size: 12px; }"
                " QMenu::item:selected { background: #241B4D; color: #FFFFFF; }"
                " QMenu::separator { height: 1px; background: #1FBAD7F7; margin: 6px 8px; }"
            )
        except Exception:
            pass

        def act(text, icon_name, slot):
            a = QAction(text, menu)
            try:
                a.setIcon(lucide_icon(icon_name, size=14, color="#C7D3EA"))
            except Exception:
                pass
            a.triggered.connect(slot)
            menu.addAction(a)
            return a

        act("Show / Hide capsule", "monitor", lambda: self.toggle_capsule_requested.emit())
        menu.addSeparator()
        act("Dictation  (Ctrl + Space)", "mic", lambda: self.dictation_requested.emit())
        act("Companion  (Ctrl + /)", "monitor", lambda: self.companion_requested.emit())
        act("Purge  (Ctrl + Win)", "layers", lambda: self.purge_requested.emit())

        menu_refine = menu.addMenu("Refine")
        try:
            menu_refine.setIcon(lucide_icon("sparkles", size=14, color="#C7D3EA"))
        except Exception:
            pass
        self._menu_refine = menu_refine
        self._fill_refine_menu(menu_refine)

        menu.addSeparator()
        act("Guide", "book-open", lambda: self.show_setup_requested.emit())
        act("Settings", "settings", lambda: self.show_settings_requested.emit())
        menu.addSeparator()
        a_exit = QAction("Exit", menu)
        try:
            a_exit.setIcon(lucide_icon("x", size=14, color="#F0A08A"))
        except Exception:
            pass
        a_exit.triggered.connect(self.quit_requested.emit)
        menu.addAction(a_exit)

        self.tray.setContextMenu(menu)
        self._menu = menu

    def _fill_refine_menu(self, menu_refine):
        """Fill the Refine submenu from Settings (built-ins + enabled customs)."""
        try:
            if menu_refine is None:
                return
            try:
                from src.config import config_vault as _vault
                actions = _vault.get_all_refine_actions()
            except Exception:
                actions = [{"id": "refine", "name": "Refine"}, {"id": "polish", "name": "Polish"}, {"id": "elaborate", "name": "Elaborate"}]
            icons = {"refine": "sparkles", "polish": "wand", "elaborate": "layers"}
            for item in (actions or [])[:6]:
                try:
                    aid = str(item.get("id", "refine"))
                    label = str(item.get("name", aid) or aid)[:24]
                    ico = icons.get(aid, "zap")
                    a = QAction(label, menu_refine)
                    try:
                        a.setIcon(lucide_icon(ico, size=12, color="#C7D3EA"))
                    except Exception:
                        pass
                    a.triggered.connect(lambda _, t=aid: self.refine_requested.emit(t))
                    menu_refine.addAction(a)
                except Exception:
                    continue
        except Exception:
            pass

    def refresh_refine_menu(self):
        """Rebuild Refine submenu from Settings (built-ins + enabled customs). Safe to call after save."""
        try:
            menu_refine = getattr(self, "_menu_refine", None)
            if menu_refine is None:
                return
            try:
                menu_refine.clear()
            except Exception:
                pass
            self._fill_refine_menu(menu_refine)
        except Exception:
            pass

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_capsule_requested.emit()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.toggle_capsule_requested.emit()

    def _on_message_clicked(self):
        self.toggle_capsule_requested.emit()

    def show(self):
        if not self.tray.isSystemTrayAvailable():
            print("[Tray] System tray not available")
        self.tray.show()
        if not self.tray.isVisible():
            print("[Tray] Warning: tray icon not visible")
        else:
            print("[Tray] Tray icon visible")

    def notify(self, title: str, message: str, duration_ms: int = 2800):
        try:
            if not self.tray.isVisible():
                self.tray.show()
            self.tray.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, duration_ms)
        except Exception as e:
            print(f"[Tray] Notify error: {e}")

    def is_visible(self) -> bool:
        return self.tray.isVisible()
