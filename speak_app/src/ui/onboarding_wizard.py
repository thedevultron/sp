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
        desc = QLabel("Low-latency dictation and voice companion with live screen. Enter your Gemini API key to start.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #9DA7BA; font-size: 12px; background: transparent;")
        lay.addWidget(desc)
        lay.addWidget(QLabel("API key"))
        self.txt_key = QLineEdit()
        self.txt_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_key.setPlaceholderText("AIzaSy...")
        self.txt_key.setText(config_vault.get_primary_key())
        self.txt_key.setClearButtonEnabled(True)
        lay.addWidget(self.txt_key)
        btn_test = QPushButton("Test")
        btn_test.setIcon(lucide_icon("zap", size=12, color="#C7D3EA"))
        btn_test.setObjectName("SecondaryButton")
        btn_test.clicked.connect(self._test_key)
        lay.addWidget(btn_test)
        lay.addStretch()

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
            ("monitor", "Win + Shift \u2014 Companion", "Live voice + live screen at 1.5 fps."),
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
            resp = client.models.generate_content(model="gemini-2.0-flash-lite", contents="Ping")
            if resp:
                self.lbl_status.setStyleSheet("color: #7EE2A8; font-size: 11px; background: transparent;")
                self.lbl_status.setText("Validated")
        except Exception as e:
            self.lbl_status.setStyleSheet("color: #F0A08A; font-size: 11px; background: transparent;")
            self.lbl_status.setText(f"Error: {str(e)[:46]}")

    def _on_next_clicked(self):
        if self.stack.currentIndex() == 0:
            key = self.txt_key.text().strip()
            if key:
                config_vault.set_primary_key(key)
            self.stack.setCurrentIndex(1)
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
