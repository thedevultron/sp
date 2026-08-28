import asyncio
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QStackedWidget, QWidget, QFrame
)
from PySide6.QtCore import Qt
from google import genai
from src.config import config_vault


class OnboardingWizard(QDialog):
    """First-launch setup dialog with API key validation & interactive tutorial."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DialogRoot")
        self.setWindowTitle("Welcome to SPEAK — Setup & Guide")
        self.setFixedSize(540, 420)
        self._init_ui()

    def _init_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 20, 24, 20)
        main.setSpacing(16)

        # Header Title
        self.lbl_step_title = QLabel("Welcome to SPEAK")
        self.lbl_step_title.setStyleSheet("font-size: 19px; font-weight: 700; color: #DA7756;")
        main.addWidget(self.lbl_step_title)

        # Multi-page Stack
        self.stack = QStackedWidget(self)

        # PAGE 1: Enter Key
        self.page_key = QWidget()
        self._build_page_key(self.page_key)
        self.stack.addWidget(self.page_key)

        # PAGE 2: Quick Tutorial
        self.page_tutorial = QWidget()
        self._build_page_tutorial(self.page_tutorial)
        self.stack.addWidget(self.page_tutorial)

        main.addWidget(self.stack)

        # Navigation Bar
        nav = QHBoxLayout()
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("color: #D97706; font-size: 11px;")
        nav.addWidget(self.lbl_status)
        nav.addStretch()

        self.btn_next = QPushButton("Next →")
        self.btn_next.setObjectName("PrimaryButton")
        self.btn_next.clicked.connect(self._on_next_clicked)
        nav.addWidget(self.btn_next)

        main.addLayout(nav)

    def _build_page_key(self, p):
        lay = QVBoxLayout(p)
        lay.setContentsMargins(0, 8, 0, 0)
        lay.setSpacing(12)

        desc = QLabel(
            "SPEAK is your low-latency voice dictation and desktop multimodal companion.\n"
            "To get started, enter your Google Gemini API key below."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #9C9CA8; line-height: 1.4;")
        lay.addWidget(desc)

        lay.addWidget(QLabel("Google AI Studio API Key:"))
        self.txt_key = QLineEdit()
        self.txt_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_key.setPlaceholderText("AIzaSy...")
        self.txt_key.setText(config_vault.get_primary_key())
        lay.addWidget(self.txt_key)

        btn_test = QPushButton("Test API Key Connection")
        btn_test.setObjectName("SecondaryButton")
        btn_test.clicked.connect(self._test_key)
        lay.addWidget(btn_test)

        lay.addStretch()

    def _build_page_tutorial(self, p):
        lay = QVBoxLayout(p)
        lay.setContentsMargins(0, 8, 0, 0)
        lay.setSpacing(10)

        card = QFrame()
        card.setStyleSheet("background-color: #18181B; border: 1px solid #28282E; border-radius: 8px; padding: 10px;")
        c_lay = QVBoxLayout(card)

        c_lay.addWidget(QLabel("<b>🎙️ Ctrl + Space: Live Voice Dictation</b><br><span style='color:#9C9CA8;'>Types instantly into any active cursor or app window.</span>"))
        c_lay.addWidget(QLabel("<b>👁️ Win + Shift: Multimodal Companion</b><br><span style='color:#9C9CA8;'>Real-time screen vision + voice dialogue with Gemini.</span>"))
        c_lay.addWidget(QLabel("<b>🧠 Ctrl + Win: Hard Purge & Reset</b><br><span style='color:#9C9CA8;'>Clears memory buffer and starts a clean session.</span>"))
        c_lay.addWidget(QLabel("<b>✏️ Screen Pen:</b><br><span style='color:#9C9CA8;'>Click the pen icon on the capsule to highlight. Press <b>Esc</b> to wipe clean.</span>"))

        lay.addWidget(card)

        tip = QLabel("💡 <i>SPEAK runs quietly in your Windows System Tray (near the clock).</i>")
        tip.setStyleSheet("color: #DA7756; font-size: 11px;")
        lay.addWidget(tip)
        lay.addStretch()

    def _test_key(self):
        key = self.txt_key.text().strip()
        if not key:
            self.lbl_status.setText("⚠️ Please enter a key first.")
            return

        self.lbl_status.setText("⏳ Testing key...")
        try:
            client = genai.Client(api_key=key)
            # Synchronous light ping
            resp = client.models.generate_content(
                model="gemini-3.5-transcribe-live",
                contents="Ping"
            )
            if resp:
                self.lbl_status.setStyleSheet("color: #34C759; font-size: 11px;")
                self.lbl_status.setText("✓ API Key Validated Successfully!")
        except Exception as e:
            self.lbl_status.setStyleSheet("color: #FF3B30; font-size: 11px;")
            self.lbl_status.setText(f"❌ Key Error: {str(e)[:45]}...")

    def _on_next_clicked(self):
        if self.stack.currentIndex() == 0:
            key = self.txt_key.text().strip()
            if key:
                config_vault.set_primary_key(key)
            self.stack.setCurrentIndex(1)
            self.lbl_step_title.setText("How to Use SPEAK")
            self.btn_next.setText("Finish & Start SPEAK 🚀")
            self.lbl_status.setText("")
        else:
            config_vault.config["first_run_completed"] = True
            config_vault.save_config()
            self.accept()