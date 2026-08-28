from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel,
    QLineEdit, QPushButton, QListWidget, QSlider, QTextEdit,
    QCheckBox, QComboBox, QFrame, QScrollArea, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush
from google import genai
from src.config import config_vault, ICON_PATH
from src.audio_engine import AudioEngine


class SettingsDialog(QDialog):
    """SPEAK Main Window - Friendly Setup, Guide & Preferences.
    Now the primary window when launching main.py - centered, polished, obvious.
    """

    def __init__(self, parent=None, initial_tab=0):
        super().__init__(parent)
        self.setObjectName("DialogRoot")
        self.setWindowTitle("SPEAK — AI Voice & Vision")
        self.setMinimumSize(640, 560)
        self.resize(740, 660)
        # Normal window (not stay-on-top) so it behaves as main app window
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Window)
        self.setModal(False)
        # Set icon
        try:
            if ICON_PATH.exists():
                self.setWindowIcon(QIcon(str(ICON_PATH)))
        except Exception:
            pass
        self._init_ui()
        self._load_values()
        if 0 <= initial_tab < self.tabs.count():
            self.tabs.setCurrentIndex(initial_tab)

    def _init_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # ===== FRIENDLY HEADER =====
        header = QFrame()
        header.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #1C1C22, stop:1 #252530); border: none; border-bottom: 1px solid #28282E;")
        header.setFixedHeight(78)
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(20, 14, 20, 14)
        h_lay.setSpacing(14)

        # Icon
        icon_lbl = QLabel()
        try:
            if ICON_PATH.exists():
                pix = QPixmap(str(ICON_PATH)).scaled(44, 44, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                icon_lbl.setPixmap(pix)
        except Exception:
            icon_lbl.setText("🎙️")
            icon_lbl.setStyleSheet("font-size: 28px;")
        icon_lbl.setFixedSize(44, 44)
        h_lay.addWidget(icon_lbl)

        # Title + subtitle
        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        title = QLabel("SPEAK")
        title.setStyleSheet("font-size: 20px; font-weight: 800; color: #F1F5F9; letter-spacing: 0.5px;")
        subtitle = QLabel("Voice Dictation & Screen Companion — Press Ctrl+Space to talk")
        subtitle.setStyleSheet("font-size: 11px; color: #94A3B8;")
        subtitle.setWordWrap(True)
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        h_lay.addLayout(title_box, 1)

        # Status pill on right
        self.lbl_api_status = QLabel("● Ready")
        self.lbl_api_status.setStyleSheet("background: rgba(52,199,89,0.12); color: #34C759; border: 1px solid rgba(52,199,89,0.3); border-radius: 12px; padding: 6px 12px; font-size: 11px; font-weight: 600;")
        self.lbl_api_status.setToolTip("API Key status")
        h_lay.addWidget(self.lbl_api_status, alignment=Qt.AlignmentFlag.AlignVCenter)

        main.addWidget(header)

        # ===== TABS =====
        self.tabs = QTabWidget(self)
        self.tabs.setDocumentMode(False)
        # Tab icons are obvious with text; QSS handles styling

        self.tab_keys = self._wrap_scrollable_tab(self._build_key_tab)
        self.tabs.addTab(self.tab_keys, "🔑  API & Setup")

        self.tab_tutorial = self._wrap_scrollable_tab(self._build_tutorial_tab)
        self.tabs.addTab(self.tab_tutorial, "📖  Guide & Hotkeys")

        self.tab_params = self._wrap_scrollable_tab(self._build_params_tab)
        self.tabs.addTab(self.tab_params, "⚙️  Preferences")

        # Add padding around tabs
        tabs_container = QWidget()
        tabs_lay = QVBoxLayout(tabs_container)
        tabs_lay.setContentsMargins(16, 12, 16, 0)
        tabs_lay.addWidget(self.tabs)
        main.addWidget(tabs_container, 1)

        # ===== MODEL INFO FOOTER (shows which models are active) =====
        model_bar = QFrame()
        model_bar.setStyleSheet("background: #18181B; border-top: 1px solid #28282E; border-bottom: 1px solid #28282E;")
        m_lay = QHBoxLayout(model_bar)
        m_lay.setContentsMargins(16, 8, 16, 8)
        m_lay.setSpacing(12)
        m_lay.addWidget(QLabel("<span style='color:#6B7280; font-size:10px;'>ACTIVE MODELS</span>"))
        # Dictation model badge
        self.lbl_model_dict = QLabel(f"🎙️ {config_vault.get_dictation_model()}")
        self.lbl_model_dict.setStyleSheet("background: rgba(218,119,86,0.1); color: #DA7756; border: 1px solid rgba(218,119,86,0.2); border-radius: 6px; padding: 4px 8px; font-size: 10px; font-weight: 600;")
        self.lbl_model_dict.setToolTip("Dictation model (Ctrl+Space) — No backup, single live model")
        m_lay.addWidget(self.lbl_model_dict)
        self.lbl_model_comp = QLabel(f"👁️ {config_vault.config.get('companion_model', 'gemini-3-flash-live')}")
        self.lbl_model_comp.setStyleSheet("background: rgba(96,165,250,0.1); color: #60A5FA; border: 1px solid rgba(96,165,250,0.2); border-radius: 6px; padding: 4px 8px; font-size: 10px; font-weight: 600;")
        backup = config_vault.config.get('companion_backup_model', 'gemini-2.5-flash-preview-native-audio-dialog')
        self.lbl_model_comp.setToolTip(f"Companion model (Win+Shift) — Primary: {config_vault.config.get('companion_model')} | Backup: {backup}")
        m_lay.addWidget(self.lbl_model_comp)
        m_lay.addStretch()
        main.addWidget(model_bar)

        # ===== BOTTOM ACTION BAR =====
        bottom = QFrame()
        bottom.setStyleSheet("background: #1C1C22; border: none; border-top: 1px solid #28282E;")
        bottom.setFixedHeight(62)
        btn_box = QHBoxLayout(bottom)
        btn_box.setContentsMargins(16, 10, 16, 10)
        btn_box.setSpacing(10)

        self.btn_cancel = QPushButton("✕  Close to Tray")
        self.btn_cancel.setMinimumHeight(40)
        self.btn_cancel.setToolTip("Hide this window to system tray. SPEAK keeps running. Use tray icon or hotkeys to reopen.")
        self.btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(self.btn_cancel)

        btn_box.addStretch()

        self.btn_save = QPushButton("💾  Save & Launch SPEAK 🚀")
        self.btn_save.setObjectName("PrimaryButton")
        self.btn_save.setMinimumHeight(40)
        self.btn_save.setMinimumWidth(220)
        self.btn_save.setToolTip("Save API key & settings. Capsule will appear only when you press hotkeys.")
        self.btn_save.clicked.connect(self._save_and_close)
        btn_box.addWidget(self.btn_save)

        main.addWidget(bottom)

    def _wrap_scrollable_tab(self, builder_func) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)
        builder_func(layout)
        scroll.setWidget(content_widget)
        return scroll

    def _build_key_tab(self, layout: QVBoxLayout):
        # Welcome card
        welcome = QFrame()
        welcome.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #1E1E24, stop:1 #1C1C22); border: 1px solid #28282E; border-radius: 12px;")
        w_lay = QVBoxLayout(welcome)
        w_lay.setContentsMargins(16, 14, 16, 14)
        w_lay.setSpacing(6)
        w_lay.addWidget(QLabel("<b style='color:#F1F5F9; font-size:14px;'>👋 Welcome to SPEAK</b>"))
        w_lay.addWidget(QLabel("<span style='color:#9C9CA8; font-size:12px; line-height:1.5;'>SPEAK runs quietly in your system tray. When you press a hotkey, the floating capsule appears above your taskbar. Add your Gemini API key below to get started.</span>"))
        layout.addWidget(welcome)

        info = QLabel(
            "🔒 Your keys are encrypted in Windows Credential Vault (keyring). They are only sent to Google Gemini API."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #94A3B8; font-size: 11px; background: rgba(218,119,86,0.06); padding: 8px 10px; border-radius: 6px; border: 1px solid rgba(218,119,86,0.12);")
        layout.addWidget(info)

        # Primary key group
        grp = QGroupBox("🔑 Primary Gemini API Key")
        grp.setStyleSheet("QGroupBox { font-weight: 600; color: #F1F5F9; }")
        g_lay = QVBoxLayout(grp)
        g_lay.setSpacing(8)
        g_lay.addWidget(QLabel("Paste your AIzaSy... key from Google AI Studio:"))
        self.txt_primary = QLineEdit()
        self.txt_primary.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_primary.setPlaceholderText("AIzaSy... paste here")
        self.txt_primary.setClearButtonEnabled(True)
        g_lay.addWidget(self.txt_primary)
        row_key_opts = QHBoxLayout()
        self.chk_show_key = QCheckBox("👁 Show key")
        self.chk_show_key.toggled.connect(lambda checked: self.txt_primary.setEchoMode(QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password))
        row_key_opts.addWidget(self.chk_show_key)
        row_key_opts.addStretch()
        g_lay.addLayout(row_key_opts)
        btn_test = QPushButton("⚡  Test API Connection")
        btn_test.setObjectName("SecondaryButton")
        btn_test.clicked.connect(self._test_primary_key)
        g_lay.addWidget(btn_test)
        layout.addWidget(grp)

        # Backup keys
        grp2 = QGroupBox("🛡️ Backup Keys (optional) — Auto-rotation on quota 429")
        g2_lay = QVBoxLayout(grp2)
        g2_lay.addWidget(QLabel("If primary hits quota, SPEAK auto-switches to next backup key."))
        self.list_backups = QListWidget()
        self.list_backups.setMinimumHeight(96)
        self.list_backups.setToolTip("Backup keys for auto-failover")
        g2_lay.addWidget(self.list_backups)
        row = QHBoxLayout()
        self.txt_new_backup = QLineEdit()
        self.txt_new_backup.setPlaceholderText("Paste backup AIzaSy... key...")
        self.txt_new_backup.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_new_backup.setClearButtonEnabled(True)
        row.addWidget(self.txt_new_backup, 1)
        btn_add = QPushButton("➕ Add")
        btn_add.clicked.connect(self._add_backup)
        row.addWidget(btn_add)
        btn_del = QPushButton("🗑 Remove")
        btn_del.setObjectName("DangerButton")
        btn_del.clicked.connect(self._remove_backup)
        row.addWidget(btn_del)
        g2_lay.addLayout(row)
        self.txt_new_backup.returnPressed.connect(self._add_backup)
        layout.addWidget(grp2)

        # Capsule hint
        hint = QLabel("💡 <b>Capsule hidden until hotkey:</b> After saving, press <b>Ctrl+Space</b> to see the floating pill above taskbar.")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #60A5FA; font-size: 11px; background: rgba(96,165,250,0.08); padding: 8px; border-radius: 6px; border: 1px solid rgba(96,165,250,0.15);")
        layout.addWidget(hint)
        layout.addStretch()

    def _build_tutorial_tab(self, layout: QVBoxLayout):
        card = QFrame()
        card.setStyleSheet("background-color: #18181B; border: 1px solid #28282E; border-radius: 12px; padding: 14px;")
        c_lay = QVBoxLayout(card)
        c_lay.setSpacing(16)

        def add_item(icon, title, desc, badge):
            row = QHBoxLayout()
            badge_lbl = QLabel(badge)
            badge_lbl.setStyleSheet("background: rgba(218,119,86,0.15); color: #DA7756; border: 1px solid rgba(218,119,86,0.3); border-radius: 6px; padding: 4px 8px; font-size: 10px; font-weight: 700;")
            badge_lbl.setFixedHeight(26)
            row.addWidget(badge_lbl)
            row.addSpacing(6)
            title_lbl = QLabel(f"<b style='color:#F1F5F9; font-size:13px;'>{icon} {title}</b>")
            title_lbl.setWordWrap(True)
            row.addWidget(title_lbl, 1)
            c_lay.addLayout(row)
            desc_lbl = QLabel(f"<span style='color:#9C9CA8; font-size:12px; line-height:1.5;'>{desc}</span>")
            desc_lbl.setWordWrap(True)
            desc_lbl.setTextFormat(Qt.TextFormat.RichText)
            desc_lbl.setIndent(4)
            c_lay.addWidget(desc_lbl)

        add_item("🎙️", "Live Voice Dictation", "Click into any app (Word, Chrome, Discord), hold <b>Ctrl</b> and tap <b>Space</b>, then speak. Text types instantly at your cursor. Capsule appears while dictating.", "Ctrl + Space")
        add_item("👁️", "Screen Companion (Vision + Voice)", "Press <b>Win + Shift</b> to start live screen sharing + voice chat with <b>gemini-3-flash-live</b> (backup <b>2.5 native audio</b>). Gemini sees your screen at ~1.5 fps and talks back.", "Win + Shift")
        add_item("🧠", "Purge & Hard Reset", "Press <b>Ctrl + Win</b> to wipe conversation memory and reset token bar to 0%. Use when context is stale.", "Ctrl + Win")
        add_item("✏️", "Screen Pen Tool", "In the capsule, click <b>Draw</b> to draw over screen. <b>Esc</b> to wipe, <b>1/2/3</b> colors, <b>Right-click</b> to clear.", "Capsule → Draw")
        layout.addWidget(card)

        tip = QLabel("📌 <b>New:</b> Capsule is <u>hidden</u> until you press a hotkey — not always visible. Find SPEAK anytime via system tray (near clock).")
        tip.setWordWrap(True)
        tip.setStyleSheet("color: #DA7756; font-size: 11px; background: rgba(218,119,86,0.08); padding: 10px; border-radius: 8px; border: 1px solid rgba(218,119,86,0.15);")
        layout.addWidget(tip)

        hk_card = QFrame()
        hk_card.setStyleSheet("background: #141416; border: 1px solid #28282E; border-radius: 8px; padding: 12px;")
        hk_lay = QVBoxLayout(hk_card)
        hk_lay.addWidget(QLabel("<b style='color:#F1F5F9; font-size:13px;'>🎛️ Capsule Buttons Explained</b>"))
        for txt in [
            "<span style='color:#94A3B8; font-size:11px;'>• <b style='color:#F1F5F9;'>✏️ Draw</b> = Draw on screen &nbsp;• <b style='color:#F1F5F9;'>⚙️ Settings</b> = Open this window &nbsp;• <b style='color:#F1F5F9;'>📖 Guide</b> = This help &nbsp;• <b style='color:#F87171;'>✕ Hide</b> = Hide capsule (back to tray)</span>",
            "<span style='color:#94A3B8; font-size:11px;'>• Status dot: <b style='color:#94A3B8;'>● Idle</b> / <b style='color:#E2886B;'>● Active</b> / <b style='color:#EF4444;'>● Error</b> &nbsp;• Wave bars pulse with mic & Gemini audio</span>",
            "<span style='color:#94A3B8; font-size:11px;'>• <b>Tray icon</b> (near clock) → Right-click for all actions: Show/Hide, Dictation, Companion, Purge, Settings, Exit</span>",
        ]:
            l = QLabel(txt)
            l.setWordWrap(True)
            l.setTextFormat(Qt.TextFormat.RichText)
            hk_lay.addWidget(l)
        layout.addWidget(hk_card)
        layout.addStretch()

    def _build_params_tab(self, layout: QVBoxLayout):
        # Mic
        grp_mic = QGroupBox("🎤 Input Microphone")
        mic_lay = QVBoxLayout(grp_mic)
        self.combo_audio = QComboBox()
        self.combo_audio.addItem("🎧 Default System Microphone", userData=None)
        try:
            for idx, name in AudioEngine.get_input_devices():
                self.combo_audio.addItem(f"[{idx}] {name}", userData=idx)
        except Exception:
            pass
        mic_lay.addWidget(self.combo_audio)
        btn_refresh = QPushButton("↻  Refresh Microphones")
        btn_refresh.setToolTip("Rescan audio devices")
        btn_refresh.clicked.connect(self._refresh_audio_devices)
        mic_lay.addWidget(btn_refresh)
        layout.addWidget(grp_mic)

        # Models display (read-only, obvious)
        grp_models = QGroupBox("🧠 AI Models (as requested)")
        mod_lay = QVBoxLayout(grp_models)
        mod_lay.setSpacing(8)
        dict_lbl = QLabel(f"🎙️ <b>Dictation:</b> <span style='color:#DA7756;'>{config_vault.get_dictation_model()}</span> <span style='color:#6B7280;'>(no backup - single live model)</span>")
        dict_lbl.setWordWrap(True)
        mod_lay.addWidget(dict_lbl)
        comp_lbl = QLabel(f"👁️ <b>Companion:</b> <span style='color:#60A5FA;'>{config_vault.config.get('companion_model')}</span> <span style='color:#6B7280;'>+ backup</span> <span style='color:#94A3B8;'>{config_vault.config.get('companion_backup_model')}</span>")
        comp_lbl.setWordWrap(True)
        mod_lay.addWidget(comp_lbl)
        mod_lay.addWidget(QLabel("<span style='color:#6B7280; font-size:10px;'>Change in config.json if needed - models are pinned per your spec.</span>"))
        layout.addWidget(grp_models)

        # System prompt
        grp_prompt = QGroupBox("💬 System Prompt (Companion Personality)")
        p_lay = QVBoxLayout(grp_prompt)
        self.txt_prompt = QTextEdit()
        self.txt_prompt.setMinimumHeight(96)
        self.txt_prompt.setMaximumHeight(140)
        self.txt_prompt.setPlaceholderText("You are SPEAK, a fast, helpful companion...")
        p_lay.addWidget(self.txt_prompt)
        layout.addWidget(grp_prompt)

        # Temperature
        grp_temp = QGroupBox("🌡️ Creativity (Temperature)")
        t_lay = QVBoxLayout(grp_temp)
        temp_row = QHBoxLayout()
        temp_row.addWidget(QLabel("Precise"))
        temp_row.addStretch()
        self.lbl_temp = QLabel("0.30")
        self.lbl_temp.setStyleSheet("color: #DA7756; font-weight: 700; font-size: 13px;")
        temp_row.addWidget(self.lbl_temp)
        temp_row.addStretch()
        temp_row.addWidget(QLabel("Creative"))
        t_lay.addLayout(temp_row)
        self.slider_temp = QSlider(Qt.Orientation.Horizontal)
        self.slider_temp.setRange(0, 200)
        self.slider_temp.setValue(30)
        self.slider_temp.valueChanged.connect(lambda v: self.lbl_temp.setText(f"{v/100:.2f}"))
        t_lay.addWidget(self.slider_temp)
        t_lay.addWidget(QLabel("<span style='color:#6B7280; font-size:10px;'>0.0 = deterministic, 2.0 = wild. Recommended 0.2-0.5 for dictation, 0.7+ for companion.</span>"))
        layout.addWidget(grp_temp)

        self.chk_startup = QCheckBox("🚀 Launch SPEAK automatically on Windows Startup")
        layout.addWidget(self.chk_startup)
        layout.addStretch()

    def _refresh_audio_devices(self):
        self.combo_audio.clear()
        self.combo_audio.addItem("🎧 Default System Microphone", userData=None)
        try:
            for idx, name in AudioEngine.get_input_devices():
                self.combo_audio.addItem(f"[{idx}] {name}", userData=idx)
        except Exception as e:
            self.lbl_api_status.setText(f"Mic scan error: {e}")
            self.lbl_api_status.setStyleSheet("background: rgba(239,68,68,0.12); color: #EF4444; border: 1px solid rgba(239,68,68,0.3); border-radius: 12px; padding: 6px 12px;")

    def _update_status(self, text: str, color: str):
        self.lbl_api_status.setText(text)
        if color == "green":
            self.lbl_api_status.setStyleSheet("background: rgba(52,199,89,0.12); color: #34C759; border: 1px solid rgba(52,199,89,0.3); border-radius: 12px; padding: 6px 12px; font-size: 11px; font-weight: 600;")
        elif color == "orange":
            self.lbl_api_status.setStyleSheet("background: rgba(245,158,11,0.12); color: #F59E0B; border: 1px solid rgba(245,158,11,0.3); border-radius: 12px; padding: 6px 12px; font-size: 11px; font-weight: 600;")
        elif color == "red":
            self.lbl_api_status.setStyleSheet("background: rgba(239,68,68,0.12); color: #EF4444; border: 1px solid rgba(239,68,68,0.3); border-radius: 12px; padding: 6px 12px; font-size: 11px; font-weight: 600;")
        else:
            self.lbl_api_status.setStyleSheet("background: rgba(156,163,175,0.12); color: #9CA3AF; border: 1px solid rgba(156,163,175,0.3); border-radius: 12px; padding: 6px 12px; font-size: 11px; font-weight: 600;")

    def _test_primary_key(self):
        k = self.txt_primary.text().strip()
        if not k:
            self._update_status("⚠️ Enter a key first", "orange")
            return
        # Allow new key format (AQ... also valid per our earlier test)
        if len(k) < 20:
            self._update_status("⚠️ Looks invalid (too short)", "orange")
        else:
            self._update_status("⏳ Testing...", "orange")
        self.repaint()
        from PySide6.QtWidgets import QApplication as QA
        QA.processEvents()
        # Use gemini-3.5-flash-lite for testing as requested (verified working)
        test_models = ["gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-2.5-flash", "gemini-flash-latest"]
        last_err = None
        for model in test_models:
            try:
                client = genai.Client(api_key=k)
                resp = client.models.generate_content(model=model, contents="Ping - reply with 'pong'")
                if resp and getattr(resp, "text", None):
                    self._update_status(f"✓ Valid! ({model})", "green")
                    self.lbl_api_status.setToolTip(f"Connected via {model}: {resp.text[:80]}")
                    return
                elif resp:
                    self._update_status(f"✓ Connected ({model})", "green")
                    return
                else:
                    self._update_status(f"⚠️ Connected ({model}), no text", "orange")
                    return
            except Exception as e:
                last_err = str(e)
                # If model not found, try next model
                if "NOT_FOUND" in last_err and "is no longer available" in last_err:
                    continue
                # For other errors, break and show
                break
        # If all models failed
        err = last_err or "Unknown error"
        if "429" in err or "quota" in err.lower():
            self._update_status("⚠️ Quota exceeded, format valid", "orange")
        elif "API_KEY_INVALID" in err or "invalid" in err.lower() or "API key not valid" in err:
            self._update_status(f"❌ Invalid key", "red")
            self.lbl_api_status.setToolTip(err[:300])
        elif "NOT_FOUND" in err:
            self._update_status(f"❌ Model not found", "red")
            self.lbl_api_status.setToolTip(err[:300])
        else:
            self._update_status(f"❌ Error: {err[:40]}", "red")
            self.lbl_api_status.setToolTip(err[:400])

    def _add_backup(self):
        k = self.txt_new_backup.text().strip()
        if not k:
            return
        if len(k) < 20:
            QMessageBox.warning(self, "Invalid Key", "Backup key looks too short.")
            return
        for i in range(self.list_backups.count()):
            if self.list_backups.item(i).text().strip() == k:
                QMessageBox.information(self, "Duplicate", "This backup key already exists.")
                return
        self.list_backups.addItem(k)
        self.txt_new_backup.clear()
        self._update_status("✓ Backup added", "green")

    def _remove_backup(self):
        row = self.list_backups.currentRow()
        if row >= 0:
            self.list_backups.takeItem(row)
            self._update_status("Removed", "orange")
        else:
            QMessageBox.information(self, "Select Item", "Please select a backup key to remove.")

    def _load_values(self):
        try:
            self.txt_primary.setText(config_vault.get_primary_key())
        except Exception:
            pass
        try:
            for b in config_vault.get_backup_keys():
                self.list_backups.addItem(b)
        except Exception:
            pass
        cfg = config_vault.config
        self.txt_prompt.setPlainText(cfg.get("system_instruction", ""))
        try:
            self.slider_temp.setValue(int(float(cfg.get("temperature", 0.3)) * 100))
        except Exception:
            self.slider_temp.setValue(30)
        self.chk_startup.setChecked(bool(cfg.get("windows_startup", False)))
        dev = cfg.get("audio_device_index", None)
        for i in range(self.combo_audio.count()):
            if self.combo_audio.itemData(i) == dev:
                self.combo_audio.setCurrentIndex(i)
                break
        # Update status pill based on key presence
        if config_vault.get_primary_key():
            self._update_status("✓ Key saved", "green")
        else:
            self._update_status("● Ready", "green")

    def _save_and_close(self):
        primary = self.txt_primary.text().strip()
        if primary and len(primary) < 20:
            QMessageBox.warning(self, "Invalid Key", "Primary API key looks too short or invalid.")
            return
        backups = [self.list_backups.item(i).text().strip() for i in range(self.list_backups.count()) if self.list_backups.item(i).text().strip()]
        if not primary and not backups and not config_vault.get_primary_key():
            ret = QMessageBox.question(self, "No API Key", "No API key entered. SPEAK will not work without a key.\nSave anyway and add later?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if ret != QMessageBox.StandardButton.Yes:
                return
        try:
            config_vault.set_primary_key(primary)
            config_vault.set_backup_keys(backups)
            config_vault.config["system_instruction"] = self.txt_prompt.toPlainText().strip() or config_vault.DEFAULT_CONFIG["system_instruction"]
            config_vault.config["temperature"] = max(0.0, min(2.0, self.slider_temp.value() / 100.0))
            config_vault.config["audio_device_index"] = self.combo_audio.currentData()
            config_vault.config["first_run_completed"] = True
            config_vault.set_startup(self.chk_startup.isChecked())
            config_vault.save_config()
            self._update_status("✓ Saved! Capsule hidden", "green")
            from PySide6.QtWidgets import QApplication as QA
            QA.processEvents()
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save:\n{e}")
            return
        self.accept()
