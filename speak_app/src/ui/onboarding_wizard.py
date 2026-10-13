import asyncio
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QStackedWidget, QWidget, QFrame
from PySide6.QtCore import Qt, QSize
from google import genai
from src.config import config_vault
from src.ui.icons import icon as lucide_icon
from src.ui.window_effects import enable_rounded_corners

class OnboardingWizard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DialogRoot")
        self.setWindowTitle("Welcome to SPEAK")
        self.setFixedSize(520, 400)
        self._init_ui()

    def _init_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(22, 18, 22, 18)
        main.setSpacing(14)
        self.lbl_step_title = QLabel("Welcome to SPEAK")
        self.lbl_step_title.setObjectName("DisplayHeading")
        self.lbl_step_title.setStyleSheet("font-family: 'Space Grotesk', 'Inter', sans-serif; font-size: 20px; font-weight: 500; color: #D8ECF8; background: transparent;")
        main.addWidget(self.lbl_step_title)
        self.stack = QStackedWidget(self)
        self.page_key = QWidget()
        self._build_page_key(self.page_key)
        self.stack.addWidget(self.page_key)
        self.page_permissions = QWidget()
        self._build_page_permissions(self.page_permissions)
        self.stack.addWidget(self.page_permissions)
        self.page_tutorial = QWidget()
        self._build_page_tutorial(self.page_tutorial)
        self.stack.addWidget(self.page_tutorial)
        main.addWidget(self.stack)
        nav = QHBoxLayout()
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("color: #9DA7BA; font-size: 11px; background: transparent;")
        nav.addWidget(self.lbl_status)
        nav.addStretch()
        self.btn_next = QPushButton("Next")
        self.btn_next.setObjectName("PrimaryButton")
        self.btn_next.setIcon(lucide_icon("chevron-down", size=12, color="#FFFFFF"))
        self.btn_next.clicked.connect(self._on_next_clicked)
        nav.addWidget(self.btn_next)
        main.addLayout(nav)

    def _build_page_key(self, p):
        lay = QVBoxLayout(p)
        lay.setContentsMargins(0, 8, 0, 0)
        lay.setSpacing(10)
        desc = QLabel("Low-latency dictation and voice companion with live screen. Enter your API key to start.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #9DA7BA; font-size: 12px; background: transparent;")
        lay.addWidget(desc)
        lay.addWidget(QLabel("API key"))
        self.txt_key = QLineEdit()
        self.txt_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_key.setPlaceholderText("Paste Gemini API key...")
        self.txt_key.setText(config_vault.get_primary_key())
        self.txt_key.setClearButtonEnabled(True)
        lay.addWidget(self.txt_key)
        btn_test = QPushButton("Test")
        btn_test.setIcon(lucide_icon("zap", size=12, color="#C7D3EA"))
        btn_test.setObjectName("SecondaryButton")
        btn_test.clicked.connect(self._test_key)
        lay.addWidget(btn_test)
        lay.addStretch()

    def _build_page_permissions(self, p):
        """Mic + screen pre-flight: the installer cannot grant these (Windows
        requires in-app approval), so first run checks them HERE with a
        re-check button before the user ever starts a session."""
        lay = QVBoxLayout(p)
        lay.setContentsMargins(0, 8, 0, 0)
        lay.setSpacing(10)
        desc = QLabel("Windows must allow the mic and screen capture. If anything is blocked, use Grant in Settings (or the startup prompt) — voice keeps working while screen waits.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #9DA7BA; font-size: 12px; background: transparent;")
        lay.addWidget(desc)
        card = QFrame()
        card.setObjectName("GlassCard")
        card.setStyleSheet("QFrame#GlassCard { background-color: #08BAD6F7; border: 1px solid #1FBAD7F7; border-radius: 16px; padding: 10px; }")
        c_lay = QVBoxLayout(card)
        c_lay.setSpacing(8)
        self.lbl_perm_mic = QLabel("Microphone: checking…")
        self.lbl_perm_mic.setStyleSheet("color: #C7D3EA; font-size: 12px; background: transparent;")
        c_lay.addWidget(self.lbl_perm_mic)
        self.lbl_perm_screen = QLabel("Screen: checking…")
        self.lbl_perm_screen.setStyleSheet("color: #C7D3EA; font-size: 12px; background: transparent;")
        c_lay.addWidget(self.lbl_perm_screen)
        lay.addWidget(card)
        btn_row = QHBoxLayout()
        btn_check = QPushButton("Check again")
        btn_check.setIcon(lucide_icon("refresh", size=12, color="#C7D3EA"))
        btn_check.setObjectName("SecondaryButton")
        btn_check.clicked.connect(self._check_permissions)
        btn_row.addWidget(btn_check)
        btn_row.addStretch()
        lay.addLayout(btn_row)
        lay.addStretch()
        try:
            self._check_permissions()
        except Exception:
            pass

    def _check_permissions(self):
        try:
            from src.permission_manager import mic_permission_manager, permission_manager
            mic_st = mic_permission_manager.check_permission()
            scr_st = permission_manager.check_permission()
        except Exception as e:
            try:
                self.lbl_perm_mic.setText(f"Check failed: {str(e)[:60]}")
            except Exception:
                pass
            return
        try:
            ok_c, bad_c = "#7EE2A8", "#F0A08A"
            self.lbl_perm_mic.setStyleSheet(f"color: {ok_c if mic_st == 'granted' else bad_c}; font-size: 12px; background: transparent;")
            self.lbl_perm_mic.setText(f"Microphone: {mic_st}" + ("" if mic_st == "granted" else " — allow in Windows Privacy > Microphone, then Check again"))
            self.lbl_perm_screen.setStyleSheet(f"color: {ok_c if scr_st == 'granted' else bad_c}; font-size: 12px; background: transparent;")
            self.lbl_perm_screen.setText(f"Screen: {scr_st}" + ("" if scr_st == "granted" else " — approve when prompted, then Check again"))
        except Exception:
            pass

    def _build_page_tutorial(self, p):
        lay = QVBoxLayout(p)
        lay.setContentsMargins(0, 8, 0, 0)
        lay.setSpacing(10)
        card = QFrame()
        card.setObjectName("GlassCard")
        card.setStyleSheet("QFrame#GlassCard { background-color: #08BAD6F7; border: 1px solid #1FBAD7F7; border-radius: 16px; padding: 10px; }")
        c_lay = QVBoxLayout(card)
        c_lay.setSpacing(8)
        rows = [
            ("mic", "Ctrl + Space \u2014 Dictation", "Types at cursor in any app."),
            ("monitor", "Ctrl + / \u2014 Companion", "Live voice + motion-burst screen."),
            ("layers", "Ctrl + Win \u2014 Purge", "Clear memory and tokens."),
        ]
        for ico, title, desc in rows:
            row = QHBoxLayout()
            ic = QLabel()
            from src.ui.icons import pixmap as lucide_pixmap
            ic.setPixmap(lucide_pixmap(ico, size=14, color="#B6D9FC"))
            ic.setFixedSize(16,16)
            row.addWidget(ic)
            l = QLabel(f"<span style='color:#D8ECF8; font-weight:600; font-size:12px;'>{title}</span><br><span style='color:#9DA7BA; font-size:11px;'>{desc}</span>")
            l.setTextFormat(Qt.TextFormat.RichText)
            row.addWidget(l, 1)
            c_lay.addLayout(row)
        lay.addWidget(card)
        tip = QLabel("Runs in system tray near the clock. Capsule keeps close only; Settings has min / max / close.")
        tip.setWordWrap(True)
        tip.setStyleSheet("color: #9DA7BA; font-size: 11px; background: transparent;")
        lay.addWidget(tip)
        lay.addStretch()

    def _test_key(self):
        key = self.txt_key.text().strip()
        if not key:
            self.lbl_status.setText("Enter a key first.")
            return
        self.lbl_status.setText("Testing...")
        try:
            client = genai.Client(api_key=key)
            try:
                _ping_model = (config_vault.get_refine_models() or [""])[0] or "gemini-3.5-flash-lite"
            except Exception:
                _ping_model = "gemini-3.5-flash-lite"
            resp = client.models.generate_content(model=_ping_model, contents="Ping")
            if resp:
                self.lbl_status.setStyleSheet("color: #7EE2A8; font-size: 11px; background: transparent;")
                self.lbl_status.setText("Validated")
        except Exception as e:
            self.lbl_status.setStyleSheet("color: #F0A08A; font-size: 11px; background: transparent;")
            _msg = str(e)
            # Never surface raw provider errors (may echo internal IDs) — classify only.
            if "429" in _msg or "quota" in _msg.lower():
                self.lbl_status.setText("Quota hit — key format ok")
            elif "API_KEY_INVALID" in _msg or "invalid" in _msg.lower():
                self.lbl_status.setText("Invalid key")
            else:
                self.lbl_status.setText("Key check failed")

    def _on_next_clicked(self):
        if self.stack.currentIndex() == 0:
            key = self.txt_key.text().strip()
            if key:
                config_vault.set_primary_key(key)
            self.stack.setCurrentIndex(1)
            self.lbl_step_title.setText("Permissions")
            self.lbl_status.setText("")
        elif self.stack.currentIndex() == 1:
            self.stack.setCurrentIndex(2)
            self.lbl_step_title.setText("Guide")
            self.btn_next.setText("Finish")
            self.btn_next.setIcon(lucide_icon("check", size=12, color="#FFFFFF"))
            self.lbl_status.setText("")
        else:
            config_vault.config["first_run_completed"] = True
            config_vault.save_config()
            self.accept()

    def showEvent(self, event):
        super().showEvent(event)
        try:
            enable_rounded_corners(self)
        except Exception:
            pass
