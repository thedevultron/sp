from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel,
    QLineEdit, QPushButton, QListWidget, QSlider, QTextEdit,
    QCheckBox, QComboBox, QFrame, QMessageBox, QGroupBox, QListWidgetItem, QSizePolicy,
    QScrollArea, QStackedWidget, QSpinBox, QRadioButton, QButtonGroup,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QRadialGradient
from google import genai
from src.config import config_vault, ICON_PATH
from src.audio_engine import AudioEngine
from src.ui.icons import icon as lucide_icon, pixmap as lucide_pixmap
from src.ui.window_effects import enable_rounded_corners

# Authkit tokens (mirrors capsule_style.qss)
_AUTHKIT_CANVAS = "#05060F"
_AUTHKIT_FROST = "#D1E4FA"
_AUTHKIT_MOON = "#C7D3EA"
_AUTHKIT_FOG = "#9DA7BA"
_AUTHKIT_ICE = "#D8ECF8"
_AUTHKIT_VIOLET = "#663AF3"
_AUTHKIT_BLUEPRINT = "#B6D9FC"

def _small_muted(text: str) -> QLabel:
    l = QLabel(text)
    l.setStyleSheet("color: #9DA7BA; font-size: 11px; background: transparent;")
    l.setWordWrap(True)
    return l

def _eyebrow(text: str) -> QLabel:
    """Authkit all-caps section marker (dotDigital substitute: JetBrains Mono)."""
    l = QLabel(text.upper())
    l.setObjectName("EyebrowLabel")
    l.setAlignment(Qt.AlignmentFlag.AlignCenter)
    l.setStyleSheet(
        "font-family: 'JetBrains Mono', 'Cascadia Code', Consolas, monospace;"
        "font-size: 12px; letter-spacing: 1px; color: #C7D3EA; background: transparent;"
    )
    return l


def _mask_key(key: str) -> str:
    """Display-only mask — never show full key in list widgets / tooltips."""
    try:
        k = (key or "").strip()
        if len(k) <= 10:
            return "••••••••"
        return f"{k[:6]}…{k[-4:]}  ({len(k)} chars)"
    except Exception:
        return "••••••••"

class CompactList(QListWidget):
    def __init__(self, fixed_h=60, parent=None):
        super().__init__(parent)
        self._fh = fixed_h
        self.setFixedHeight(fixed_h)
    def sizeHint(self):
        return QSize(256, self._fh)
    def minimumSizeHint(self):
        return QSize(120, self._fh)

class CompactText(QTextEdit):
    def __init__(self, fixed_h=52, parent=None):
        super().__init__(parent)
        self._fh = fixed_h
        self.setFixedHeight(fixed_h)
    def sizeHint(self):
        return QSize(256, self._fh)
    def minimumSizeHint(self):
        return QSize(120, self._fh)

class SettingsDialog(QDialog):
    """Authkit frosted-glass settings — main window with native min/max/close.
    Drag is native via the OS titlebar (we deliberately do NOT strip WS_BORDER
    or extend the DWM frame, which was breaking move/hit-testing).
    """

    sig_new_session_requested = Signal()
    sig_grant_permission_requested = Signal()

    def __init__(self, parent=None, initial_tab=0, session_manager=None):
        super().__init__(parent)
        self.setObjectName("DialogRoot")
        self.setWindowTitle("SPEAK — Settings  ·  Amir Bagawan")
        # Fullscreen-ready: larger minimum, maximized on launch via main.py
        self.setMinimumSize(960, 600)
        self.resize(1180, 760)
        # MAIN WINDOW chrome: native min + max + close so the OS draws all three
        # and native drag/resize/aero-snap keep working. Do NOT use Frameless or Tool here.
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowSystemMenuHint
            | Qt.WindowType.WindowMinimizeButtonHint
            | Qt.WindowType.WindowMaximizeButtonHint
            | Qt.WindowType.WindowCloseButtonHint
        )
        self.setModal(False)
        self.setSizeGripEnabled(True)
        # Sidebar state + session manager hookup
        self._sidebar_collapsed = False
        self._session_manager = session_manager
        self._nav_buttons: list = []
        # Friendlier: allow Esc to hide to tray (not quit) — handled in reject().
        try:
            if ICON_PATH.exists():
                self.setWindowIcon(QIcon(str(ICON_PATH)))
        except Exception:
            pass
        self._init_ui()
        self._load_values()
        try:
            self.refresh_sessions_ui()
        except Exception:
            pass
        try:
            self.update_permission_banner("unknown", "")
        except Exception:
            pass
        if 0 <= initial_tab < self.tabs.count():
            self.tabs.setCurrentIndex(initial_tab)
            try:
                self._sync_nav(initial_tab)
            except Exception:
                pass

    def _make_scroll_page(self, content: QWidget) -> QScrollArea:
        """Wrap every distinct tab/container in an independent smooth vertical scroll area."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setWidget(content)
        # Smooth per-pixel scrolling (overflow-y: auto equivalent)
        try:
            sb = scroll.verticalScrollBar()
            if sb is not None:
                sb.setSingleStep(18)
                sb.setPageStep(120)
        except Exception:
            pass
        scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
            " QScrollBar:vertical { background: #080B1A; width: 10px; margin: 2px; border-radius: 5px; }"
            " QScrollBar::handle:vertical { background: #2A3350; min-height: 40px; border-radius: 5px; }"
            " QScrollBar::handle:vertical:hover { background: #3A4560; }"
            " QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }"
        )
        return scroll

    def _init_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # Minimalist header — no dividers, single row wordmark + status
        header = QFrame()
        header.setObjectName("SettingsHeader")
        header.setStyleSheet("QFrame#SettingsHeader { background-color: #080B1A; border: none; }")
        header.setFixedHeight(60)
        h = QHBoxLayout(header)
        h.setContentsMargins(16, 10, 16, 10)
        h.setSpacing(12)
        icon_lbl = QLabel()
        try:
            if ICON_PATH.exists():
                pix = QPixmap(str(ICON_PATH)).scaled(34, 34, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                icon_lbl.setPixmap(pix)
            else:
                icon_lbl.setPixmap(lucide_pixmap("mic", size=24, color="#B6D9FC"))
        except Exception:
            icon_lbl.setPixmap(lucide_pixmap("mic", size=24, color="#B6D9FC"))
        icon_lbl.setFixedSize(34, 34)
        icon_lbl.setScaledContents(True)
        h.addWidget(icon_lbl)
        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        t = QLabel("SPEAK")
        t.setObjectName("DisplayHeading")
        t.setStyleSheet("font-family: 'Space Grotesk', 'Inter', sans-serif; font-size: 18px; font-weight: 500; color: #D8ECF8; letter-spacing: 0.2px; background: transparent;")
        sub = QLabel("Voice dictation and companion")
        sub.setStyleSheet("font-size: 11px; color: #9DA7BA; background: transparent;")
        title_box.addWidget(t)
        title_box.addWidget(sub)
        h.addLayout(title_box, 1)
        self.lbl_api_status = QLabel("Ready")
        self.lbl_api_status.setObjectName("BadgeLabel")
        self.lbl_api_status.setStyleSheet("background-color: #1FC7D3EA; color: #C7D3EA; border: 1px solid #1FBAD7F7; border-radius: 6px; padding: 5px 10px; font-size: 11px;")
        h.addWidget(self.lbl_api_status, alignment=Qt.AlignmentFlag.AlignVCenter)
        main.addWidget(header)

        # Inline diagnostic banner (permission pending/denied) with Grant Permission retry
        self.permission_banner = QFrame()
        self.permission_banner.setObjectName("PermissionBanner")
        self.permission_banner.setStyleSheet("QFrame#PermissionBanner { background-color: #2A1F0E; border: 1px solid #6B4A1E; border-radius: 8px; }")
        pb = QHBoxLayout(self.permission_banner)
        pb.setContentsMargins(14, 8, 14, 8)
        pb.setSpacing(10)
        self.lbl_permission = QLabel("")
        self.lbl_permission.setWordWrap(True)
        self.lbl_permission.setStyleSheet("color: #FFB84D; font-size: 12px; background: transparent;")
        pb.addWidget(self.lbl_permission, 1)
        self.btn_grant_permission = QPushButton("Grant Permission")
        self.btn_grant_permission.setIcon(lucide_icon("shield-check", size=13, color="#FFFFFF"))
        self.btn_grant_permission.setFixedHeight(32)
        self.btn_grant_permission.setStyleSheet("QPushButton { background-color: #663AF3; color: #FFFFFF; border: 1px solid #7A52FF; border-radius: 8px; padding: 4px 14px; font-size: 12px; font-weight: 600; } QPushButton:hover { background-color: #7550F5; }")
        self.btn_grant_permission.setToolTip("Trigger native OS authorization + retry capture")
        self.btn_grant_permission.clicked.connect(lambda: self.sig_grant_permission_requested.emit())
        pb.addWidget(self.btn_grant_permission)
        self.btn_banner_dismiss = QPushButton("Later")
        self.btn_banner_dismiss.setFixedHeight(32)
        self.btn_banner_dismiss.setStyleSheet("QPushButton { background: transparent; color: #9DA7BA; border: 1px solid #1FBAD7F7; border-radius: 8px; padding: 4px 12px; } QPushButton:hover { color: #FFFFFF; }")
        self.btn_banner_dismiss.clicked.connect(lambda: self.permission_banner.setVisible(False))
        pb.addWidget(self.btn_banner_dismiss)
        self.permission_banner.setVisible(False)
        banner_wrap = QWidget()
        bw = QVBoxLayout(banner_wrap)
        bw.setContentsMargins(16, 8, 16, 0)
        bw.addWidget(self.permission_banner)
        main.addWidget(banner_wrap)

        # Body: collapsible sidebar + stacked scroll pages (minimalist, no dividers)
        body = QWidget()
        body_lay = QHBoxLayout(body)
        body_lay.setContentsMargins(16, 10, 16, 6)
        body_lay.setSpacing(12)

        # Sidebar navigation
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setStyleSheet("QFrame#Sidebar { background-color: #080B1A; border: 1px solid #1FBAD7F7; border-radius: 12px; }")
        self.sidebar.setFixedWidth(208)
        side_lay = QVBoxLayout(self.sidebar)
        side_lay.setContentsMargins(8, 8, 8, 8)
        side_lay.setSpacing(4)
        collapse_row = QHBoxLayout()
        collapse_row.setContentsMargins(2, 0, 2, 4)
        side_title = QLabel("NAVIGATE")
        side_title.setStyleSheet("color: #9DA7BA; font-size: 10px; letter-spacing: 1px; background: transparent;")
        collapse_row.addWidget(side_title, 1)
        self.btn_collapse = QPushButton()
        self.btn_collapse.setIcon(lucide_icon("chevrons-left", size=14, color="#C7D3EA"))
        self.btn_collapse.setFixedSize(30, 28)
        self.btn_collapse.setToolTip("Collapse sidebar")
        self.btn_collapse.setStyleSheet("QPushButton { background: transparent; border: 1px solid transparent; border-radius: 6px; } QPushButton:hover { background: #14BAD6F7; }")
        self.btn_collapse.clicked.connect(self.toggle_sidebar)
        collapse_row.addWidget(self.btn_collapse)
        side_lay.addLayout(collapse_row)

        self._nav_defs = [
            ("Setup", "lock", "API keys"),
            ("Guide", "book-open", "Shortcuts"),
            ("Preferences", "sliders", "Audio + tools"),
            ("Refine", "sparkles", "Prompts"),
            ("Sessions", "layers", "Live sessions"),
            ("Help", "circle-help", "Docs + fixes"),
        ]
        self._nav_buttons = []
        for idx, (name, ico, tip) in enumerate(self._nav_defs):
            b = QPushButton(f"  {name}")
            try:
                b.setIcon(lucide_icon(ico, size=15, color="#C7D3EA"))
            except Exception:
                pass
            b.setCheckable(True)
            b.setToolTip(tip)
            b.setMinimumHeight(40)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(
                "QPushButton { text-align: left; background: transparent; color: #C7D3EA; border: 1px solid transparent; border-radius: 8px; font-size: 13px; padding: 6px 10px; }"
                " QPushButton:hover { background: #14BAD6F7; color: #FFFFFF; }"
                " QPushButton:checked { background: #241B4D; color: #FFFFFF; border: 1px solid #663AF3; }"
            )
            b.clicked.connect(lambda _, i=idx: self.go_to_page(i))
            side_lay.addWidget(b)
            self._nav_buttons.append(b)
        side_lay.addStretch()
        hint = QLabel("Ctrl+Tab spawns a session")
        hint.setStyleSheet("color: #9DA7BA; font-size: 10px; background: transparent; padding: 4px 6px;")
        hint.setWordWrap(True)
        side_lay.addWidget(hint)
        body_lay.addWidget(self.sidebar)

        # Stacked pages — each wrapped in its own smooth scroll area
        self.stack = QStackedWidget()
        # Keep legacy alias: main.py uses settings_dialog.tabs.setCurrentIndex/count
        self.tabs = self.stack
        self.tab_keys = QWidget()
        self._build_key_tab(self.tab_keys)
        self.tab_guide = QWidget()
        self._build_guide_tab(self.tab_guide)
        self.tab_prefs = QWidget()
        self._build_prefs_tab(self.tab_prefs)
        self._extend_prefs_with_tool_controls(self.tab_prefs)
        self.tab_refine = QWidget()
        self._build_refine_tab(self.tab_refine)
        self.tab_sessions = QWidget()
        self._build_sessions_tab(self.tab_sessions)
        self.tab_help = QWidget()
        self._build_help_tab(self.tab_help)
        # Order preserves legacy indices: 0 Setup, 1 Guide, 2 Prefs, 3 Refine, 4 Sessions, 5 Help
        for content in (self.tab_keys, self.tab_guide, self.tab_prefs, self.tab_refine, self.tab_sessions, self.tab_help):
            content.setStyleSheet("background: transparent;")
            # Inner padding container so scroll content breathes
            pad = QWidget()
            pad_lay = QVBoxLayout(pad)
            pad_lay.setContentsMargins(4, 2, 10, 12)
            pad_lay.setSpacing(8)
            # Reparent content into pad
            content.setParent(pad)
            pad_lay.addWidget(content)
            pad_lay.addStretch()
            self.stack.addWidget(self._make_scroll_page(pad))
        body_lay.addWidget(self.stack, 1)
        main.addWidget(body, 1)

        # Model bar — single minimalist row, no extra dividers
        model_bar = QFrame()
        model_bar.setObjectName("ModelBar")
        model_bar.setStyleSheet("QFrame#ModelBar { background-color: #080B1A; border: none; }")
        ml = QHBoxLayout(model_bar)
        ml.setContentsMargins(16, 6, 16, 6)
        ml.setSpacing(8)
        ml.addWidget(_small_muted("Models"))
        self.lbl_model_dict = QLabel(config_vault.get_dictation_model())
        self.lbl_model_dict.setStyleSheet("background-color: #241B4D; color: #D8ECF8; border: 1px solid #663AF3; border-radius: 6px; padding: 3px 8px; font-size: 11px;")
        self.lbl_model_dict.setToolTip("Dictation model")
        ml.addWidget(self.lbl_model_dict)
        self.lbl_model_comp = QLabel(config_vault.config.get('companion_model', 'gemini-3-flash-live'))
        self.lbl_model_comp.setStyleSheet("background-color: #1FC7D3EA; color: #D1E4FA; border: 1px solid #1FBAD7F7; border-radius: 6px; padding: 3px 8px; font-size: 11px;")
        self.lbl_model_comp.setToolTip(f"Companion + backup {config_vault.config.get('companion_backup_model')}")
        ml.addWidget(self.lbl_model_comp)
        try:
            think_badge = QLabel("Thinking HIGH · Transcription SMART")
            think_badge.setStyleSheet("background-color: #0E2A1D; color: #7EE2A8; border: 1px solid #1E5B3A; border-radius: 6px; padding: 3px 8px; font-size: 11px;")
            think_badge.setToolTip("Live configuration locks (enforced)")
            ml.addWidget(think_badge)
        except Exception:
            pass
        ml.addStretch()
        main.addWidget(model_bar)

        # Bottom bar — ghost Close + Violet Save only
        bottom = QFrame()
        bottom.setObjectName("BottomBar")
        bottom.setStyleSheet("QFrame#BottomBar { background-color: #080B1A; border: none; }")
        bottom.setFixedHeight(70)
        bl = QHBoxLayout(bottom)
        bl.setContentsMargins(18, 12, 18, 12)
        bl.setSpacing(12)
        self.btn_cancel = QPushButton("Close")
        self.btn_cancel.setIcon(lucide_icon("x", size=15, color="#C7D3EA"))
        self.btn_cancel.setIconSize(QSize(15,15))
        self.btn_cancel.setMinimumHeight(42)
        self.btn_cancel.setMinimumWidth(140)
        self.btn_cancel.setStyleSheet("QPushButton { background-color: #14BAD6F7; color: #D1E4FA; border: 1px solid #1FBAD7F7; border-radius: 999px; font-size: 13px; font-weight: 600; padding: 10px 22px; } QPushButton:hover { background-color: #1FBAD6F7; color: #FFFFFF; }")
        self.btn_cancel.setToolTip("Hide to tray")
        self.btn_cancel.clicked.connect(self.reject)
        bl.addWidget(self.btn_cancel)
        bl.addStretch()
        self.btn_save = QPushButton("Save & Launch")
        self.btn_save.setObjectName("PrimaryButton")
        self.btn_save.setIcon(lucide_icon("check", size=16, color="#FFFFFF"))
        self.btn_save.setIconSize(QSize(16,16))
        self.btn_save.setMinimumHeight(42)
        self.btn_save.setMinimumWidth(190)
        self.btn_save.setStyleSheet("QPushButton#PrimaryButton { background-color: #663AF3; border: 1px solid #7A52FF; color: #FFFFFF; font-size: 13px; font-weight: 700; padding: 10px 24px; border-radius: 999px; } QPushButton#PrimaryButton:hover { background-color: #7550F5; } QPushButton#PrimaryButton:pressed { background-color: #552FD1; }")
        self.btn_save.clicked.connect(self._save_and_close)
        bl.addWidget(self.btn_save)
        main.addWidget(bottom)

        self.stack.currentChanged.connect(self._on_tab_changed)
        try:
            self._sync_nav(self.stack.currentIndex())
        except Exception:
            pass

    def toggle_sidebar(self):
        self._sidebar_collapsed = not self._sidebar_collapsed
        try:
            if self._sidebar_collapsed:
                self.sidebar.setFixedWidth(58)
                for b in self._nav_buttons:
                    try:
                        b.setText("")
                    except Exception:
                        pass
                self.btn_collapse.setIcon(lucide_icon("chevrons-right", size=14, color="#C7D3EA"))
                self.btn_collapse.setToolTip("Expand sidebar")
            else:
                self.sidebar.setFixedWidth(208)
                for b, (name, _, __) in zip(self._nav_buttons, self._nav_defs):
                    try:
                        b.setText(f"  {name}")
                    except Exception:
                        pass
                self.btn_collapse.setIcon(lucide_icon("chevrons-left", size=14, color="#C7D3EA"))
                self.btn_collapse.setToolTip("Collapse sidebar")
        except Exception:
            pass

    def go_to_page(self, idx: int):
        try:
            self.stack.setCurrentIndex(idx)
        except Exception:
            pass
        try:
            self._sync_nav(idx)
        except Exception:
            pass

    def _sync_nav(self, idx: int):
        for i, b in enumerate(self._nav_buttons):
            try:
                b.blockSignals(True)
                b.setChecked(i == idx)
                b.blockSignals(False)
            except Exception:
                pass

    def _on_tab_changed(self, idx: int):
        try:
            self._sync_nav(idx)
        except Exception:
            pass

    def update_permission_banner(self, status: str, text: str = ""):
        """Visual fallback: inline diagnostic banner when pending/denied."""
        try:
            st = str(status or "unknown").lower()
            if st in ("pending", "denied"):
                msg = text or ("Screen recording denied — live vision paused. Grant permission to resume." if st == "denied" else "Screen permission pending — waiting for OS approval. Voice continues.")
                try:
                    self.lbl_permission.setText(msg)
                except Exception:
                    pass
                self.permission_banner.setVisible(True)
            else:
                self.permission_banner.setVisible(False)
        except Exception:
            pass

    # ---- Session manager hookup ----
    def set_session_manager(self, mgr):
        self._session_manager = mgr
        try:
            mgr.sessions_changed.connect(lambda: self.refresh_sessions_ui())
        except Exception:
            pass
        try:
            self.refresh_sessions_ui()
        except Exception:
            pass

    def refresh_sessions_ui(self):
        try:
            mgr = getattr(self, "_session_manager", None)
            if mgr is None:
                try:
                    self.lbl_session_count.setText("Active sessions: 0 · Stored: 0 / 5")
                except Exception:
                    pass
                return
            active = mgr.active_count()
            stored = mgr.stored_count()
            mx = mgr.max_stored
            try:
                self.lbl_session_count.setText(f"Active sessions: {active} · Stored: {stored} / {mx}")
            except Exception:
                pass
            try:
                # sync slider/spin without loops
                self.slider_max_sessions.blockSignals(True)
                self.spin_max_sessions.blockSignals(True)
                self.slider_max_sessions.setValue(int(mx))
                self.spin_max_sessions.setValue(int(mx))
                self.slider_max_sessions.blockSignals(False)
                self.spin_max_sessions.blockSignals(False)
            except Exception:
                pass
            try:
                self.list_sessions.clear()
                for meta in mgr.list_metadata():
                    sid = meta.get("session_id", "?")
                    mode = meta.get("mode", "")
                    status = meta.get("status", "")
                    created = meta.get("created", "")
                    words = meta.get("transcript_words", 0)
                    marker = "● " if status == "active" else "○ "
                    item = QListWidgetItem(f"{marker}[{sid}] {mode} · {status} · {words} words · {created}")
                    try:
                        item.setData(Qt.ItemDataRole.UserRole, sid)
                    except Exception:
                        pass
                    self.list_sessions.addItem(item)
            except Exception:
                pass
        except Exception:
            pass

    def _on_max_sessions_changed(self, n: int):
        try:
            n = max(1, min(20, int(n)))
        except Exception:
            n = 5
        try:
            self.slider_max_sessions.blockSignals(True)
            self.spin_max_sessions.blockSignals(True)
            self.slider_max_sessions.setValue(n)
            self.spin_max_sessions.setValue(n)
            self.slider_max_sessions.blockSignals(False)
            self.spin_max_sessions.blockSignals(False)
        except Exception:
            pass
        try:
            mgr = getattr(self, "_session_manager", None)
            if mgr is not None:
                mgr.set_max_stored(n)
        except Exception:
            pass
        try:
            self.refresh_sessions_ui()
        except Exception:
            pass

    def _extend_prefs_with_tool_controls(self, w: QWidget):
        """Append Message Verification toggle + Live locks to Preferences page."""
        try:
            lay = w.layout()
            if lay is None:
                lay = QVBoxLayout(w)
                w.setLayout(lay)
        except Exception:
            return
        # Message Verification toggle
        grp = QGroupBox("Message Verification — typeTextAtCursor")
        gl = QVBoxLayout(grp)
        gl.setSpacing(6)
        gl.addWidget(_small_muted("Controls requireVerification / autoSubmit on every tool call."))
        self.verification_group = QButtonGroup(self)
        self.radio_verification_active = QRadioButton("Verification Active (Default) — requireVerification=True, autoSubmit=False")
        self.radio_verification_active.setToolTip("Type text, wait for user confirmation before Enter.")
        self.radio_auto_send = QRadioButton("Auto-Send — requireVerification=False, autoSubmit=True")
        self.radio_auto_send.setToolTip("Type text and press Enter automatically.")
        for r in (self.radio_verification_active, self.radio_auto_send):
            try:
                r.setStyleSheet("color: #D1E4FA; font-size: 12px;")
            except Exception:
                pass
            self.verification_group.addButton(r)
            gl.addWidget(r)
        try:
            mode = config_vault.get_verification_mode()
            if mode == "auto_send":
                self.radio_auto_send.setChecked(True)
            else:
                self.radio_verification_active.setChecked(True)
        except Exception:
            self.radio_verification_active.setChecked(True)
        lay.addWidget(grp)
        # Live configuration locks (read-only)
        lock_grp = QGroupBox("Live Configuration Locks")
        ll = QVBoxLayout(lock_grp)
        ll.setSpacing(4)
        ll.addWidget(_small_muted("Enforced on every Live connect — not editable."))
        row = QHBoxLayout()
        for txt, tip in (("Transcription: SMART", "High-accuracy context awareness, locked"), ("Thinking: HIGH", "Gemini Live thinking_level HIGH, locked"), ("Tool: typeTextAtCursor", "All typing binds to this schema")):
            badge = QLabel(txt)
            badge.setToolTip(tip)
            badge.setStyleSheet("background-color: #0E2A1D; color: #7EE2A8; border: 1px solid #1E5B3A; border-radius: 6px; padding: 4px 8px; font-size: 11px;")
            row.addWidget(badge)
        row.addStretch()
        ll.addLayout(row)
        lay.addWidget(lock_grp)

    def _build_sessions_tab(self, w: QWidget):
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)
        lay.addWidget(_eyebrow("Multi-Session Engine"))
        info = QLabel("Ctrl + Tab immediately spawns and switches to a new live session. Oldest stored sessions evict first (FIFO) when over the limit.")
        info.setWordWrap(True)
        info.setStyleSheet("color: #9DA7BA; font-size: 11px; background-color: #0F1A33; padding: 7px 10px; border-radius: 6px; border: 1px solid #1FBAD7F7;")
        lay.addWidget(info)
        grp = QGroupBox("Session Controls")
        gl = QVBoxLayout(grp)
        gl.setSpacing(6)
        row = QHBoxLayout()
        row.addWidget(QLabel("Max Stored Sessions"))
        self.slider_max_sessions = QSlider(Qt.Orientation.Horizontal)
        self.slider_max_sessions.setRange(1, 20)
        self.slider_max_sessions.setValue(5)
        self.slider_max_sessions.setToolTip("FIFO eviction threshold (default 5)")
        self.slider_max_sessions.valueChanged.connect(self._on_max_sessions_changed)
        row.addWidget(self.slider_max_sessions, 1)
        self.spin_max_sessions = QSpinBox()
        self.spin_max_sessions.setRange(1, 20)
        self.spin_max_sessions.setValue(5)
        self.spin_max_sessions.valueChanged.connect(self._on_max_sessions_changed)
        row.addWidget(self.spin_max_sessions)
        gl.addLayout(row)
        self.lbl_session_count = QLabel("Active sessions: 0 · Stored: 0 / 5")
        self.lbl_session_count.setStyleSheet("color: #B6D9FC; font-size: 12px; font-weight: 600; background: transparent;")
        gl.addWidget(self.lbl_session_count)
        gl.addWidget(_small_muted("Stored session metadata (newest first). Active session marked ●."))
        self.list_sessions = QListWidget()
        self.list_sessions.setMinimumHeight(120)
        self.list_sessions.setMaximumHeight(220)
        self.list_sessions.setStyleSheet("QListWidget { background-color: #05060F; border: 1px solid #1FBAD7F7; border-radius: 6px; color: #D1E4FA; font-size: 11px; }")
        self.list_sessions.setToolTip("Stored sessions — FIFO evicts oldest when over Max")
        gl.addWidget(self.list_sessions)
        btn_row = QHBoxLayout()
        self.btn_new_session = QPushButton("New Session (Ctrl+Tab)")
        try:
            self.btn_new_session.setIcon(lucide_icon("plus", size=13, color="#FFFFFF"))
        except Exception:
            pass
        self.btn_new_session.setStyleSheet("QPushButton { background-color: #663AF3; color: #FFFFFF; border: 1px solid #7A52FF; border-radius: 8px; padding: 6px 14px; font-weight: 600; } QPushButton:hover { background-color: #7550F5; }")
        self.btn_new_session.setToolTip("Spawn and switch to a new live session now")
        self.btn_new_session.clicked.connect(lambda: self.sig_new_session_requested.emit())
        btn_row.addWidget(self.btn_new_session)
        btn_row.addStretch()
        gl.addLayout(btn_row)
        lay.addWidget(grp)
        lay.addStretch()

    def _build_help_tab(self, w: QWidget):
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)
        lay.addWidget(_eyebrow("Help & Documentation"))
        # Feature Directory
        feat = QGroupBox("Feature Directory — step-by-step")
        fl = QVBoxLayout(feat)
        fl.setSpacing(6)
        for title, steps in [
            ("Screen Share", ["1. Enable Preferences > Live Screen or capsule monitor button.", "2. Grant OS screen permission when the banner appears.", "3. Start Companion (Win+Shift) — frames stream at ~1.5 fps.", "4. Toggle screen mid-session; voice never drops."]),
            ("Live Transcription", ["1. Press Ctrl+Space to dictate.", "2. Speak — interim shows live, finals append with SMART accuracy.", "3. Text types at cursor automatically.", "4. Say refine / polish / elaborate or tap capsule buttons."]),
            ("Smart Insertion", ["1. Place cursor in any app input field.", "2. Dictate or trigger typeTextAtCursor via companion.", "3. Verification Active waits for your Enter; Auto-Send submits instantly.", "4. Tone adapts: formal for docs, friendly for chat, concise for code."]),
        ]:
            t = QLabel(title)
            t.setStyleSheet("color: #D8ECF8; font-size: 12px; font-weight: 600; background: transparent;")
            fl.addWidget(t)
            for s in steps:
                l = QLabel(s)
                l.setWordWrap(True)
                l.setStyleSheet("color: #9DA7BA; font-size: 11px; background: transparent; padding-left: 8px;")
                fl.addWidget(l)
        lay.addWidget(feat)
        # Shortcut Cheat Sheet table
        cheat = QGroupBox("Shortcut Cheat Sheet")
        cl = QVBoxLayout(cheat)
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Keys", "Action"])
        rows = [
            ("Ctrl + Tab", "Spawn + switch to new live session"),
            ("Ctrl + Space", "Dictation on/off (types at cursor)"),
            ("Win + Shift", "Companion voice + screen"),
            ("Ctrl + Win", "Purge memory + hard reset"),
            ("F11 / Maximize", "Fullscreen settings"),
            ("Esc", "Hide to tray (app keeps running)"),
        ]
        try:
            self.shortcut_table = table
        except Exception:
            pass
        table.setRowCount(len(rows))
        for i, (k, a) in enumerate(rows):
            ki = QTableWidgetItem(k)
            ai = QTableWidgetItem(a)
            ki.setFlags(ki.flags() ^ Qt.ItemFlag.ItemIsEditable)
            ai.setFlags(ai.flags() ^ Qt.ItemFlag.ItemIsEditable)
            table.setItem(i, 0, ki)
            table.setItem(i, 1, ai)
        try:
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            table.verticalHeader().setVisible(False)
        except Exception:
            pass
        table.setMinimumHeight(160)
        table.setMaximumHeight(220)
        table.setStyleSheet("QTableWidget { background-color: #05060F; color: #D1E4FA; border: 1px solid #1FBAD7F7; border-radius: 6px; font-size: 11px; } QHeaderView::section { background-color: #0B1023; color: #9DA7BA; border: none; padding: 4px; }")
        cl.addWidget(table)
        lay.addWidget(cheat)
        # Troubleshooting
        trouble = QGroupBox("Troubleshooting — quick fixes")
        tl = QVBoxLayout(trouble)
        for q, a in [
            ("Cursor not typing?", "Focus the target app input first (not SPEAK). Check Verification mode. Retry dictation; InjectionService skips when SPEAK is focused."),
            ("OS permission banner?", "Click Grant Permission. On Windows open Privacy > Screen recording and allow. On macOS allow in System Settings > Privacy > Screen Recording, then retry."),
            ("Mic silent?", "Settings > Preferences > Microphone — pick device, Refresh, restart dictation. Watch capsule wave bars."),
            ("Live connect failing?", "Check API keys (Setup), companion model IDs, and network. Failover rotates keys; 3 fails in 30s stops loudly."),
        ]:
            ql = QLabel(q)
            ql.setStyleSheet("color: #D8ECF8; font-size: 12px; font-weight: 600; background: transparent;")
            tl.addWidget(ql)
            al = QLabel(a)
            al.setWordWrap(True)
            al.setStyleSheet("color: #9DA7BA; font-size: 11px; background: transparent; padding-left: 8px;")
            tl.addWidget(al)
        lay.addWidget(trouble)
        lay.addStretch()

    def _build_key_tab(self, w: QWidget):
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        # Compact info - free tier notice, never mention embedded key value
        try:
            from src._embedded_key import get_embedded_key as _gek
            _has_free = bool(_gek())
        except Exception:
            _has_free = False
        if _has_free:
            free_msg = "Free tier active \u2014 no key needed. Add your own key above for unlimited use. If you add one, yours is used instead."
            info = QLabel(free_msg)
            info.setStyleSheet("color: #7EE2A8; font-size: 11px; background-color: #0E2A1D; padding: 7px 10px; border-radius: 6px; border: 1px solid #1E5B3A;")
        else:
            info = QLabel("Keys stored in Windows Credential Manager. Only sent to Google.")
            info.setStyleSheet("color: #C7D3EA; font-size: 11px; background-color: #0F1A33; padding: 7px 10px; border-radius: 6px; border: 1px solid #1FBAD7F7;")
        info.setWordWrap(True)
        lay.addWidget(info)

        # Primary key
        grp = QGroupBox("Primary API key")
        gl = QVBoxLayout(grp)
        gl.setSpacing(6)
        gl.addWidget(_small_muted("AIzaSy... from Google AI Studio"))
        self.txt_primary = QLineEdit()
        self.txt_primary.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_primary.setPlaceholderText("Paste AIzaSy...")
        self.txt_primary.setClearButtonEnabled(True)
        self.txt_primary.setFixedHeight(36)
        self.txt_primary.setMaxLength(256)
        self.txt_primary.setToolTip("Stored in Windows Credential Manager — never in plain files")
        gl.addWidget(self.txt_primary)
        row = QHBoxLayout()
        self.chk_show_key = QCheckBox("Show")
        self.chk_show_key.toggled.connect(lambda c: self.txt_primary.setEchoMode(QLineEdit.EchoMode.Normal if c else QLineEdit.EchoMode.Password))
        row.addWidget(self.chk_show_key)
        row.addStretch()
        btn_test = QPushButton("Test")
        btn_test.setIcon(lucide_icon("zap", size=12, color="#C7D3EA"))
        btn_test.setObjectName("SecondaryButton")
        btn_test.setFixedHeight(30)
        btn_test.clicked.connect(self._test_primary_key)
        row.addWidget(btn_test)
        gl.addLayout(row)
        lay.addWidget(grp)

        # Backup keys — compact, MASKED display (full key in UserRole only)
        grp2 = QGroupBox("Backup keys — auto switch on quota")
        gl2 = QVBoxLayout(grp2)
        gl2.setSpacing(6)
        gl2.addWidget(_small_muted("Stored in Windows Credential Manager. List shows masked preview only."))
        self.list_backups = CompactList(fixed_h=56)
        self.list_backups.setStyleSheet("QListWidget { background-color: #05060F; }")
        self.list_backups.setToolTip("Masked previews — full keys stay in Credential Manager")
        gl2.addWidget(self.list_backups)
        row2 = QHBoxLayout()
        self.txt_new_backup = QLineEdit()
        self.txt_new_backup.setPlaceholderText("Paste backup key")
        self.txt_new_backup.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_new_backup.setClearButtonEnabled(True)
        self.txt_new_backup.setFixedHeight(36)
        self.txt_new_backup.setMaxLength(256)
        row2.addWidget(self.txt_new_backup, 1)
        btn_add = QPushButton("Add")
        btn_add.setIcon(lucide_icon("plus", size=12, color="#D1E4FA"))
        btn_add.setFixedHeight(34)
        btn_add.clicked.connect(self._add_backup)
        row2.addWidget(btn_add)
        btn_del = QPushButton("Remove")
        btn_del.setIcon(lucide_icon("trash-2", size=12, color="#F0A08A"))
        btn_del.setObjectName("DangerButton")
        btn_del.setFixedHeight(34)
        btn_del.clicked.connect(self._remove_backup)
        row2.addWidget(btn_del)
        gl2.addLayout(row2)
        self.txt_new_backup.returnPressed.connect(self._add_backup)
        lay.addWidget(grp2)

        hint = QLabel("After save, capsule appears only on hotkey. Check Guide for shortcuts.")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #9DA7BA; font-size: 11px; padding: 4px 0; background: transparent;")
        lay.addWidget(hint)
        lay.addStretch()

    def _build_guide_tab(self, w: QWidget):
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(7)

        # Authkit glass rows — no emoji, lucide frost
        def row(icon, title, keys, desc):
            r = QFrame()
            r.setObjectName("GlassCard")
            r.setStyleSheet("QFrame#GlassCard { background-color: #08BAD6F7; border: 1px solid #1FBAD7F7; border-radius: 16px; }")
            rl = QHBoxLayout(r)
            rl.setContentsMargins(10, 7, 10, 7)
            rl.setSpacing(8)
            ic = QLabel()
            ic.setPixmap(lucide_pixmap(icon, size=18, color="#B6D9FC"))
            ic.setFixedSize(18,18)
            rl.addWidget(ic)
            mid = QVBoxLayout()
            mid.setSpacing(2)
            title_l = QLabel(title)
            title_l.setStyleSheet("color: #D8ECF8; font-weight: 600; font-size: 12px; background: transparent;")
            mid.addWidget(title_l)
            desc_l = QLabel(desc)
            desc_l.setStyleSheet("color: #9DA7BA; font-size: 11px; background: transparent;")
            desc_l.setWordWrap(True)
            mid.addWidget(desc_l)
            rl.addLayout(mid, 1)
            badge = QLabel(keys)
            badge.setStyleSheet("background-color: #1FC7D3EA; color: #D1E4FA; border: 1px solid #1FBAD7F7; border-radius: 6px; padding: 4px 7px; font-size: 11px; font-weight: 500;")
            rl.addWidget(badge, alignment=Qt.AlignmentFlag.AlignTop)
            return r

        lay.addWidget(_eyebrow("Shortcuts"))
        lay.addWidget(row("mic", "Dictation", "Ctrl + Space", "Speak. Types at cursor."))
        lay.addWidget(row("monitor", "Companion", "Win + Shift", "Live voice + live screen at 1.5 fps. Toggle screen in capsule."))
        lay.addWidget(row("layers", "Purge", "Ctrl + Win", "Clear memory and session (refine deletes since purge)."))
        lay.addWidget(row("sparkles", "Refine", "Say refine", "Refine / Polish / Elaborate session via Flash Lite. Triggers + prompts editable in Refine tab."))

        tip = QLabel("Capsule (close-only) is hidden until hotkey. Find SPEAK in system tray near the clock.")
        tip.setWordWrap(True)
        tip.setStyleSheet("color: #9DA7BA; font-size: 11px; background-color: #08BAD6F7; padding: 8px 10px; border-radius: 6px; border: 1px solid #1FBAD7F7;")
        lay.addWidget(tip)

        caps = QFrame()
        caps.setObjectName("GlassCard")
        caps.setStyleSheet("QFrame#GlassCard { background-color: #05060F; border: 1px solid #1FBAD7F7; border-radius: 16px; }")
        cl = QVBoxLayout(caps)
        cl.setContentsMargins(8, 6, 8, 6)
        cl.setSpacing(3)
        cl.addWidget(QLabel("<span style='color:#D8ECF8; font-weight:600; font-size:11px;'>Capsule</span>"))
        for txt in [
            "Settings is the main window (min / max / close). Capsule keeps close only.",
            "Dot idle fog, active blueprint, error ember. Bars pulse with mic and Gemini.",
            "Transcript panel: copy, clear, refine/polish/elaborate + customs. Screen button toggles live vision.",
            "Refine deletes the whole session text, then types the result. Say elaborate (or old expand).",
        ]:
            l = QLabel(txt)
            l.setWordWrap(True)
            l.setStyleSheet("color: #9DA7BA; font-size: 11px; background: transparent;")
            cl.addWidget(l)
        lay.addWidget(caps)
        lay.addStretch()

    def _build_prefs_tab(self, w: QWidget):
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        # Top row: Mic | Custom words — side by side to save height (wider dialog allows)
        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        grp_mic = QGroupBox("Microphone")
        ml = QVBoxLayout(grp_mic)
        ml.setSpacing(4)
        ml.setContentsMargins(10, 8, 10, 8)
        self.combo_audio = QComboBox()
        self.combo_audio.setFixedHeight(34)
        self.combo_audio.addItem("Default microphone", userData=None)
        try:
            for idx, name in AudioEngine.get_input_devices():
                self.combo_audio.addItem(f"[{idx}] {name}", userData=idx)
        except Exception:
            pass
        ml.addWidget(self.combo_audio)
        btn_ref = QPushButton("Refresh")
        btn_ref.setIcon(lucide_icon("refresh", size=12, color="#C7D3EA"))
        btn_ref.setFixedHeight(28)
        btn_ref.clicked.connect(self._refresh_audio_devices)
        ml.addWidget(btn_ref)
        ml.addStretch()
        top_row.addWidget(grp_mic, 1)

        grp_vocab = QGroupBox("Custom words and mark")
        vl = QVBoxLayout(grp_vocab)
        vl.setSpacing(4)
        vl.setContentsMargins(10, 8, 10, 8)
        vm_row = QHBoxLayout()
        vm_row.setSpacing(8)
        left_col = QVBoxLayout()
        left_col.setSpacing(3)
        left_col.addWidget(_small_muted("Words"))
        self.txt_custom_words = QLineEdit()
        self.txt_custom_words.setPlaceholderText("e.g. AcmeCorp, Figma")
        self.txt_custom_words.setClearButtonEnabled(True)
        self.txt_custom_words.setFixedHeight(32)
        left_col.addWidget(self.txt_custom_words)
        vm_row.addLayout(left_col, 1)
        right_col = QVBoxLayout()
        right_col.setSpacing(3)
        right_col.addWidget(_small_muted("Mark"))
        self.txt_custom_mark = QLineEdit()
        self.txt_custom_mark.setPlaceholderText("e.g. My Studio")
        self.txt_custom_mark.setMaxLength(120)
        self.txt_custom_mark.setClearButtonEnabled(True)
        self.txt_custom_mark.setFixedHeight(32)
        right_col.addWidget(self.txt_custom_mark)
        vm_row.addLayout(right_col, 1)
        vl.addLayout(vm_row)
        self.list_words = CompactList(fixed_h=36)
        self.list_words.setStyleSheet("QListWidget { background-color: #05060F; }")
        self.list_words.setToolTip("Current custom words")
        vl.addWidget(self.list_words)
        roww = QHBoxLayout()
        roww.setSpacing(6)
        btn_add_word = QPushButton("Add")
        btn_add_word.setIcon(lucide_icon("plus", size=12, color="#D1E4FA"))
        btn_add_word.setFixedHeight(28)
        btn_add_word.clicked.connect(self._add_custom_words)
        roww.addWidget(btn_add_word)
        btn_clear_words = QPushButton("Clear")
        btn_clear_words.setIcon(lucide_icon("trash-2", size=12, color="#9DA7BA"))
        btn_clear_words.setFixedHeight(28)
        btn_clear_words.clicked.connect(self._clear_custom_words)
        roww.addWidget(btn_clear_words)
        roww.addStretch()
        vl.addLayout(roww)
        self.txt_custom_words.returnPressed.connect(self._add_custom_words)
        self.txt_custom_mark.returnPressed.connect(self._add_custom_words)
        top_row.addWidget(grp_vocab, 1.2)
        lay.addLayout(top_row)

        # System prompt — compact, lower height
        grp_prompt = QGroupBox("System prompt")
        pl = QVBoxLayout(grp_prompt)
        pl.setSpacing(4)
        pl.setContentsMargins(10, 8, 10, 8)
        self.txt_prompt = CompactText(fixed_h=52)
        self.txt_prompt.setPlaceholderText("You are SPEAK, a fast companion...")
        pl.addWidget(self.txt_prompt)
        lay.addWidget(grp_prompt)

        # Temperature + screen toggle row
        row2 = QHBoxLayout()
        grp_temp = QGroupBox("Creativity")
        tl = QVBoxLayout(grp_temp)
        tl.setSpacing(4)
        t_row = QHBoxLayout()
        t_row.addWidget(QLabel("Precise"))
        t_row.addStretch()
        self.lbl_temp = QLabel("0.30")
        self.lbl_temp.setStyleSheet("color: #B6D9FC; font-weight: 600; background: transparent;")
        t_row.addWidget(self.lbl_temp)
        t_row.addStretch()
        t_row.addWidget(QLabel("Creative"))
        tl.addLayout(t_row)
        self.slider_temp = QSlider(Qt.Orientation.Horizontal)
        self.slider_temp.setRange(0, 200)
        self.slider_temp.setValue(30)
        self.slider_temp.valueChanged.connect(lambda v: self.lbl_temp.setText(f"{v/100:.2f}"))
        tl.addWidget(self.slider_temp)
        row2.addWidget(grp_temp, 1)

        grp_screen = QGroupBox("Live Screen")
        sl = QVBoxLayout(grp_screen)
        self.chk_screen = QCheckBox("Share live screen in companion")
        self.chk_screen.setChecked(True)
        self.chk_screen.setToolTip("Toggle live screen sharing at ~1.5 fps. When off, companion is voice only.")
        sl.addWidget(self.chk_screen)
        sl.addWidget(_small_muted("Synced with capsule screen button. Takes effect live."))
        row2.addWidget(grp_screen, 1)
        lay.addLayout(row2)

        # Startup
        self.chk_startup = QCheckBox("Launch on Windows startup")
        lay.addWidget(self.chk_startup)
        lay.addStretch()

    def _build_refine_tab(self, w: QWidget):
        from PySide6.QtWidgets import QScrollArea
        outer = QVBoxLayout(w)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(6)
        outer.addWidget(_eyebrow("Refine prompts"))
        info = QLabel("Refine deletes everything typed this session (since purge / dictation start), then types the result. Edit prompts + voice triggers below. Custom actions appear in capsule, tray, and voice.")
        info.setWordWrap(True)
        info.setStyleSheet("color: #9DA7BA; font-size: 11px; background-color: #0F1A33; padding: 7px 10px; border-radius: 6px; border: 1px solid #1FBAD7F7;")
        outer.addWidget(info)
        scroll = QScrollArea(w)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        inner = QWidget()
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(0, 0, 6, 0)
        lay.setSpacing(8)
        self._refine_prompt_edits = {}
        self._refine_trigger_edits = {}
        for aid, title, hint in [
            ("refine", "Refine", "Self-correction aware cleanup"),
            ("polish", "Polish", "Publication-ready polish"),
            ("elaborate", "Elaborate", "Expand with detail (voice: elaborate or expand)"),
        ]:
            grp = QGroupBox(title)
            gl = QVBoxLayout(grp)
            gl.setSpacing(4)
            gl.setContentsMargins(10, 8, 10, 8)
            gl.addWidget(_small_muted(hint))
            te = CompactText(fixed_h=56)
            te.setPlaceholderText(f"Prompt for {title}...")
            gl.addWidget(te)
            self._refine_prompt_edits[aid] = te
            trow = QHBoxLayout()
            trow.setSpacing(6)
            trow.addWidget(_small_muted("Voice triggers (comma-separated):"))
            le = QLineEdit()
            le.setPlaceholderText("e.g. refine" if aid == "refine" else ("e.g. polish" if aid == "polish" else "e.g. elaborate, expand"))
            le.setClearButtonEnabled(True)
            le.setFixedHeight(30)
            le.setMaxLength(120)
            le.setToolTip("Say any of these words to trigger. Lowercase letters/numbers/hyphen only.")
            trow.addWidget(le, 1)
            gl.addLayout(trow)
            self._refine_trigger_edits[aid] = le
            lay.addWidget(grp)
        # Custom actions (up to 3)
        cgrp = QGroupBox("Custom actions (up to 3)")
        cl = QVBoxLayout(cgrp)
        cl.setSpacing(6)
        cl.setContentsMargins(10, 8, 10, 8)
        cl.addWidget(_small_muted("Each: display name, single voice trigger, prompt. Shows in capsule + tray + voice when enabled."))
        self._custom_rows = []
        for i in range(3):
            row = QVBoxLayout()
            row.setSpacing(3)
            top = QHBoxLayout()
            top.setSpacing(6)
            en = QCheckBox(f"Custom {i+1}")
            en.setChecked(False)
            top.addWidget(en)
            nm = QLineEdit()
            nm.setPlaceholderText("Name e.g. Summarize")
            nm.setMaxLength(24)
            nm.setClearButtonEnabled(True)
            nm.setFixedHeight(30)
            top.addWidget(nm, 1)
            tr = QLineEdit()
            tr.setPlaceholderText("trigger e.g. summarize")
            tr.setMaxLength(24)
            tr.setClearButtonEnabled(True)
            tr.setFixedHeight(30)
            tr.setToolTip("Single voice word (a-z, 0-9, hyphen, 2-24 chars). Must be unique.")
            top.addWidget(tr, 1)
            row.addLayout(top)
            pr = CompactText(fixed_h=44)
            pr.setPlaceholderText("Prompt e.g. Summarize the following text in 3 bullets. Output ONLY the summary:")
            row.addWidget(pr)
            cl.addLayout(row)
            self._custom_rows.append({"enabled": en, "name": nm, "trigger": tr, "prompt": pr})
        lay.addWidget(cgrp)
        reset_row = QHBoxLayout()
        reset_row.addStretch()
        self.btn_refine_reset = QPushButton("Reset refine defaults")
        self.btn_refine_reset.setIcon(lucide_icon("refresh", size=12, color="#C7D3EA"))
        self.btn_refine_reset.setFixedHeight(30)
        self.btn_refine_reset.setToolTip("Restore default prompts + triggers (clears customs)")
        self.btn_refine_reset.clicked.connect(self._reset_refine_defaults)
        reset_row.addWidget(self.btn_refine_reset)
        lay.addLayout(reset_row)
        lay.addStretch()
        scroll.setWidget(inner)
        outer.addWidget(scroll, 1)

    def _reset_refine_defaults(self):
        try:
            for aid, te in (getattr(self, "_refine_prompt_edits", {}) or {}).items():
                try:
                    te.setPlainText(config_vault.DEFAULT_REFINE_PROMPTS.get(aid, ""))
                except Exception:
                    pass
            for aid, le in (getattr(self, "_refine_trigger_edits", {}) or {}).items():
                try:
                    le.setText(", ".join(config_vault.DEFAULT_REFINE_TRIGGERS.get(aid, [])))
                except Exception:
                    pass
            for row in getattr(self, "_custom_rows", []) or []:
                try:
                    row["enabled"].setChecked(False)
                    row["name"].clear()
                    row["trigger"].clear()
                    row["prompt"].clear()
                except Exception:
                    pass
            self._update_status("Refine defaults restored (Save to apply)", "orange")
        except Exception:
            pass

    def _refresh_audio_devices(self):
        self.combo_audio.clear()
        self.combo_audio.addItem("Default microphone", userData=None)
        try:
            for idx, name in AudioEngine.get_input_devices():
                self.combo_audio.addItem(f"[{idx}] {name}", userData=idx)
        except Exception as e:
            self.lbl_api_status.setText("Mic scan failed")
            self.lbl_api_status.setStyleSheet("background-color: #2A1414; color: #F0A08A; border: 1px solid #55E46D4C; border-radius: 6px; padding: 5px 10px;")

    def _update_status(self, text: str, color: str):
        self.lbl_api_status.setText(text)
        styles = {
            "green": "background-color: #0E2A1D; color: #7EE2A8; border: 1px solid #1E5B3A; border-radius: 6px; padding: 5px 10px; font-size: 11px;",
            "orange": "background-color: #2A1F0E; color: #FFB84D; border: 1px solid #6B4A1E; border-radius: 6px; padding: 5px 10px; font-size: 11px;",
            "red": "background-color: #2A1414; color: #F0A08A; border: 1px solid #55E46D4C; border-radius: 6px; padding: 5px 10px; font-size: 11px;",
            "muted": "background-color: #1FC7D3EA; color: #C7D3EA; border: 1px solid #1FBAD7F7; border-radius: 6px; padding: 5px 10px; font-size: 11px;",
        }
        self.lbl_api_status.setStyleSheet(styles.get(color, styles["muted"]))

    def _test_primary_key(self):
        k = self.txt_primary.text().strip()
        if not k:
            self._update_status("Enter a key", "orange")
            return
        if len(k) < 20 or len(k) > 256:
            self._update_status("Key length looks wrong", "orange")
            return
        # Basic format guard — avoids pointless network call + clearer UX
        if not k.startswith("AIza"):
            self._update_status("Should start with AIza…", "orange")
            self.lbl_api_status.setToolTip("Gemini keys from AI Studio start with AIza. Double-check paste.")
            return
        else:
            self._update_status("Testing...", "orange")
        self.repaint()
        from PySide6.QtWidgets import QApplication as QA
        QA.processEvents()
        # Probe current refine models (never retired IDs) + generic fallback.
        try:
            test_models = [m for m in config_vault.get_refine_models() if m] + ["gemini-flash-latest"]
        except Exception:
            test_models = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-flash-latest"]
        # Dictation readiness suffix: model + installed-SDK transcription support.
        try:
            _dict_model = config_vault.get_dictation_model()
        except Exception:
            _dict_model = "gemini-3.5-transcribe-live"
        try:
            from src.gemini_client import _dictation_sdk_status as _sdk_probe
            _smart_ok, _vocab_ok, _interim_ok = _sdk_probe()
            _sdk_note = "SDK SMART+vocab+interim OK" if (_smart_ok and _vocab_ok and _interim_ok) else (
                "SDK legacy: VERBATIM-only, no interim — pip install -U \"google-genai>=2.19\" for SMART")
        except Exception:
            _sdk_note = "SDK transcription status unknown"
        last_err = None
        for model in test_models:
            try:
                client = genai.Client(api_key=k)
                resp = client.models.generate_content(model=model, contents="Ping - reply with 'pong'")
                if resp and getattr(resp, "text", None):
                    self._update_status(f"Valid ({model})", "green")
                    self.lbl_api_status.setToolTip(f"{model}: {resp.text[:80]} | Dictation {_dict_model} — {_sdk_note}")
                    return
                elif resp:
                    self._update_status(f"Connected ({model})", "green")
                    return
            except Exception as e:
                last_err = str(e)
                if "NOT_FOUND" in last_err:
                    continue
                break
        err = last_err or "Unknown"
        if "429" in err or "quota" in err.lower():
            self._update_status("Quota hit, format ok", "orange")
        elif "API_KEY_INVALID" in err or "invalid" in err.lower():
            self._update_status("Invalid key", "red")
            self.lbl_api_status.setToolTip(err[:300])
        elif "NOT_FOUND" in err:
            self._update_status("Model not found", "red")
        else:
            self._update_status(f"Error", "red")
            self.lbl_api_status.setToolTip(err[:400])

    def _add_backup(self):
        k = self.txt_new_backup.text().strip()
        if not k:
            return
        if len(k) < 20 or len(k) > 256:
            QMessageBox.warning(self, "Invalid key", "Key length looks wrong (expected ~39 chars starting with AIza).")
            return
        if not k.startswith("AIza"):
            ret = QMessageBox.question(self, "Unusual key", "Backup key does not start with AIza. Add anyway?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if ret != QMessageBox.StandardButton.Yes:
                return
        # Compare against stored full values (UserRole), not masked display text
        for i in range(self.list_backups.count()):
            try:
                stored = self.list_backups.item(i).data(Qt.ItemDataRole.UserRole) or ""
            except Exception:
                stored = ""
            if (stored or "").strip() == k:
                QMessageBox.information(self, "Duplicate", "Already exists.")
                return
        item = QListWidgetItem(_mask_key(k))
        try:
            item.setData(Qt.ItemDataRole.UserRole, k)
            item.setToolTip("Masked — full key stays in Credential Manager")
        except Exception:
            pass
        self.list_backups.addItem(item)
        self.txt_new_backup.clear()
        self._update_status("Backup added", "green")

    def _remove_backup(self):
        row = self.list_backups.currentRow()
        if row >= 0:
            self.list_backups.takeItem(row)
            self._update_status("Removed", "orange")
        else:
            QMessageBox.information(self, "Select", "Select a backup key to remove.")

    def _add_custom_words(self):
        raw = self.txt_custom_words.text().strip()
        if not raw:
            return
        parts = [p.strip() for p in raw.replace(";", ",").replace("\n", ",").split(",") if p.strip()]
        if not parts:
            return
        # Add to list widget avoiding dup
        existing = {self.list_words.item(i).text().strip().lower() for i in range(self.list_words.count())}
        for p in parts:
            if p.lower() not in existing:
                self.list_words.addItem(p)
                existing.add(p.lower())
        self.txt_custom_words.clear()

    def _clear_custom_words(self):
        self.list_words.clear()

    def _load_values(self):
        try:
            self.txt_primary.setText(config_vault.get_primary_key())
        except Exception:
            pass
        try:
            for b in config_vault.get_backup_keys():
                if not (b or "").strip():
                    continue
                item = QListWidgetItem(_mask_key(b))
                try:
                    item.setData(Qt.ItemDataRole.UserRole, b)
                    item.setToolTip("Masked — full key stays in Credential Manager")
                except Exception:
                    pass
                self.list_backups.addItem(item)
        except Exception:
            pass
        cfg = config_vault.config
        self.txt_prompt.setPlainText(cfg.get("system_instruction", "") or config_vault.DEFAULT_CONFIG["system_instruction"])
        try:
            self.slider_temp.setValue(int(float(cfg.get("temperature", 0.3)) * 100))
        except Exception:
            self.slider_temp.setValue(30)
        self.chk_startup.setChecked(bool(cfg.get("windows_startup", False)))
        # Screen share
        try:
            self.chk_screen.setChecked(bool(cfg.get("enable_screen_share", True)))
        except Exception:
            pass
        # Custom words/mark
        try:
            cw = cfg.get("custom_words", []) or []
            for w in cw:
                if str(w).strip():
                    self.list_words.addItem(str(w).strip())
            self.txt_custom_mark.setText(str(cfg.get("custom_mark", "") or ""))
        except Exception:
            pass
        # Refine prompts/triggers/customs (Settings-editable)
        try:
            for aid, te in (getattr(self, "_refine_prompt_edits", {}) or {}).items():
                try:
                    te.setPlainText(config_vault.get_refine_prompt(aid))
                except Exception:
                    pass
            trig = config_vault.get_refine_triggers()
            for aid, le in (getattr(self, "_refine_trigger_edits", {}) or {}).items():
                try:
                    le.setText(", ".join(trig.get(aid, [])))
                except Exception:
                    pass
            customs = config_vault.get_custom_actions(enabled_only=False)
            for i, row in enumerate(getattr(self, "_custom_rows", []) or []):
                try:
                    if i < len(customs):
                        c = customs[i]
                        row["enabled"].setChecked(bool(c.get("enabled", True)))
                        row["name"].setText(str(c.get("name", "")))
                        row["trigger"].setText(str(c.get("trigger", "")))
                        row["prompt"].setPlainText(str(c.get("prompt", "")))
                    else:
                        row["enabled"].setChecked(False)
                        row["name"].clear()
                        row["trigger"].clear()
                        row["prompt"].clear()
                except Exception:
                    pass
        except Exception:
            pass
        dev = cfg.get("audio_device_index", None)
        for i in range(self.combo_audio.count()):
            if self.combo_audio.itemData(i) == dev:
                self.combo_audio.setCurrentIndex(i)
                break
        # Verification mode + max sessions (redesign defaults)
        try:
            mode = config_vault.get_verification_mode()
            if mode == "auto_send":
                self.radio_auto_send.setChecked(True)
            else:
                self.radio_verification_active.setChecked(True)
        except Exception:
            pass
        try:
            mx = config_vault.get_max_stored_sessions()
            self.slider_max_sessions.blockSignals(True)
            self.spin_max_sessions.blockSignals(True)
            self.slider_max_sessions.setValue(int(mx))
            self.spin_max_sessions.setValue(int(mx))
            self.slider_max_sessions.blockSignals(False)
            self.spin_max_sessions.blockSignals(False)
            try:
                mgr = getattr(self, "_session_manager", None)
                if mgr is not None:
                    mgr.set_max_stored(int(mx))
            except Exception:
                pass
        except Exception:
            pass
        if config_vault.get_primary_key():
            self._update_status("Key saved — using yours", "green")
        elif config_vault.is_using_embedded():
            self._update_status("Free tier active", "green")
        else:
            try:
                from src._embedded_key import get_embedded_key
                if get_embedded_key():
                    self._update_status("Free tier active", "green")
                else:
                    self._update_status("Ready", "muted")
            except Exception:
                self._update_status("Ready", "muted")

    def _save_and_close(self):
        primary = self.txt_primary.text().strip()
        if primary and (len(primary) < 20 or len(primary) > 256):
            QMessageBox.warning(self, "Invalid key", "Primary key length looks wrong.")
            return
        # Read full keys from UserRole (display is masked)
        backups: list[str] = []
        for i in range(self.list_backups.count()):
            try:
                stored = self.list_backups.item(i).data(Qt.ItemDataRole.UserRole)
                if stored and str(stored).strip():
                    backups.append(str(stored).strip())
                    continue
            except Exception:
                pass
            # Fallback: if old plain-text item (pre-mask builds), migrate if valid
            try:
                txt = self.list_backups.item(i).text().strip()
                if txt.startswith("AIza") and len(txt) >= 20:
                    backups.append(txt)
            except Exception:
                pass
        # Hidden embedded fallback allows free use - don't force key, but inform
        has_embedded = False
        try:
            has_embedded = config_vault.is_using_embedded() or bool(primary) or bool(backups) or bool(config_vault.get_primary_key())
            # Actually check if embedded exists even when vault empty
            from src._embedded_key import get_embedded_key
            if get_embedded_key():
                has_embedded = True
        except Exception:
            has_embedded = bool(primary or backups or config_vault.get_primary_key())
        if not primary and not backups and not config_vault.get_primary_key() and not has_embedded:
            ret = QMessageBox.question(self, "No API key", "No key entered. You can use free tier (limited) or add your key for unlimited. Save anyway?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if ret != QMessageBox.StandardButton.Yes:
                return
        elif not primary and not backups and config_vault.is_using_embedded():
            # Using hidden free tier - allow save silently
            pass
        # Custom words
        custom_words = [self.list_words.item(i).text().strip() for i in range(self.list_words.count()) if self.list_words.item(i).text().strip()]
        # Also include any pending text field
        pending = self.txt_custom_words.text().strip()
        if pending:
            for p in [x.strip() for x in pending.replace(";", ",").split(",") if x.strip()]:
                if p.lower() not in {w.lower() for w in custom_words}:
                    custom_words.append(p)
        custom_mark = self.txt_custom_mark.text().strip()
        # Refine prompts/triggers/customs — validate + sanitize (security caps)
        refine_prompts: dict = {}
        refine_triggers: dict = {}
        custom_actions: list = []
        try:
            for aid, te in (getattr(self, "_refine_prompt_edits", {}) or {}).items():
                try:
                    v = config_vault._clean_prompt(te.toPlainText())
                    if v:
                        refine_prompts[aid] = v
                except Exception:
                    pass
            for aid, le in (getattr(self, "_refine_trigger_edits", {}) or {}).items():
                try:
                    parts = [config_vault._clean_trigger(p) for p in str(le.text() or "").replace(";", ",").split(",")]
                    parts = [p for p in parts if p][:6]
                    if parts:
                        refine_triggers[aid] = parts
                except Exception:
                    pass
            seen: set = set()
            for aid, lst in refine_triggers.items():
                for t in lst or []:
                    seen.add(t)
            for row in getattr(self, "_custom_rows", []) or []:
                try:
                    en = bool(row["enabled"].isChecked())
                    nm = config_vault._clean_name(row["name"].text())
                    tr = config_vault._clean_trigger(row["trigger"].text())
                    pr = config_vault._clean_prompt(row["prompt"].toPlainText())
                    if not nm and not tr and not pr:
                        continue  # empty row
                    if en and (not nm or not tr or not pr):
                        QMessageBox.warning(self, "Custom action incomplete", "Enabled custom actions need a name, trigger, and prompt.")
                        return
                    if (nm or tr or pr) and not tr:
                        QMessageBox.warning(self, "Custom trigger invalid", "Custom triggers must be 2-24 chars: a-z, 0-9, hyphen.")
                        return
                    if tr and tr in seen:
                        QMessageBox.warning(self, "Duplicate trigger", f"Trigger '{tr}' is already used. Pick a unique word.")
                        return
                    if tr and pr:
                        seen.add(tr)
                        custom_actions.append({"name": nm or tr.title(), "trigger": tr, "prompt": pr, "enabled": en})
                except Exception:
                    continue
            custom_actions = custom_actions[:3]
            # Sanitize through vault (caps + charset + uniqueness) before persist
            refine_prompts = config_vault._sanitize_refine_prompts(refine_prompts)
            refine_triggers = config_vault._sanitize_refine_triggers({**config_vault.get_refine_triggers(), **refine_triggers} if refine_triggers else config_vault.get_refine_triggers())
            # Re-sanitize customs against final triggers for collision safety
            tmp_cfg = dict(config_vault.config)
            tmp_cfg["refine_triggers"] = refine_triggers
            _orig = config_vault.config
            config_vault.config = tmp_cfg
            try:
                custom_actions = config_vault._sanitize_custom_actions(custom_actions)
            finally:
                config_vault.config = _orig
        except Exception:
            refine_prompts, refine_triggers, custom_actions = {}, {}, []
        try:
            config_vault.set_primary_key(primary)
            config_vault.set_backup_keys(backups)
            config_vault.config["system_instruction"] = self.txt_prompt.toPlainText().strip() or config_vault.DEFAULT_CONFIG["system_instruction"]
            config_vault.config["temperature"] = max(0.0, min(2.0, self.slider_temp.value() / 100.0))
            config_vault.config["audio_device_index"] = self.combo_audio.currentData()
            config_vault.config["first_run_completed"] = True
            config_vault.config["custom_words"] = [w for w in custom_words if w][:80]
            config_vault.config["custom_mark"] = custom_mark[:120]
            if refine_prompts:
                # Merge: only overwrite edited built-ins, keep others (preserves customs separately)
                merged_prompts = dict(config_vault.config.get("refine_prompts") or {})
                merged_prompts.update(refine_prompts)
                config_vault.config["refine_prompts"] = config_vault._sanitize_refine_prompts(merged_prompts)
            if refine_triggers:
                config_vault.config["refine_triggers"] = refine_triggers
            config_vault.config["custom_actions"] = custom_actions
            config_vault.config["enable_screen_share"] = bool(self.chk_screen.isChecked())
            # Verification mode + max stored sessions (redesign)
            try:
                if hasattr(self, "radio_auto_send") and self.radio_auto_send.isChecked():
                    config_vault.config["verification_mode"] = "auto_send"
                else:
                    config_vault.config["verification_mode"] = "verification_active"
            except Exception:
                config_vault.config["verification_mode"] = "verification_active"
            try:
                mx = int(self.spin_max_sessions.value()) if hasattr(self, "spin_max_sessions") else 5
                config_vault.config["max_stored_sessions"] = max(1, min(20, mx))
                try:
                    mgr = getattr(self, "_session_manager", None)
                    if mgr is not None:
                        mgr.set_max_stored(max(1, min(20, mx)))
                except Exception:
                    pass
            except Exception:
                config_vault.config["max_stored_sessions"] = 5
            # Live locks are absolute
            config_vault.config["live_thinking_level"] = "HIGH"
            config_vault.config["live_transcription_mode"] = "SMART"
            config_vault.set_startup(self.chk_startup.isChecked())
            config_vault.save_config()
            self._update_status("Saved", "green")
            from PySide6.QtWidgets import QApplication as QA
            QA.processEvents()
        except Exception as e:
            QMessageBox.critical(self, "Save error", f"Failed to save:\n{e}")
            return
        self.accept()

    def paintEvent(self, event):
        # Authkit backdrop: midnight canvas + faint blueprint grid + top spotlight.
        # Cheap, static, DPI-safe: 80px grid at ~6% + radial halo at top-center.
        # Painted under children (QDialog paints background first), no flicker.
        try:
            p = QPainter(self)
            p.fillRect(self.rect(), QColor("#05060F"))
            # Spotlight halo (conic approximated with radial, cool blue-white)
            try:
                cx = self.width() // 2
                halo = QRadialGradient(cx, -20, max(220, self.width() // 2))
                halo.setColorAt(0.0, QColor(124, 145, 182, 70))
                halo.setColorAt(0.45, QColor(124, 145, 182, 26))
                halo.setColorAt(1.0, QColor(124, 145, 182, 0))
                p.fillRect(self.rect(), halo)
            except Exception:
                pass
            # Blueprint grid 80px, 1px at ~6%
            try:
                p.setPen(QColor(186, 215, 247, 15))
                step = 80
                w, h = self.width(), self.height()
                y = 0
                while y <= h:
                    p.drawLine(0, y, w, y)
                    y += step
                x = 0
                while x <= w:
                    p.drawLine(x, 0, x, h)
                    x += step
            except Exception:
                pass
            p.end()
        except Exception:
            try:
                super().paintEvent(event)
            except Exception:
                pass
            return
    def showEvent(self, event):
        super().showEvent(event)
        # FIX (drag): keep native non-client area intact. Only set Win11 rounded
        # corners (DWMWA_WINDOW_CORNER_PREFERENCE). Do NOT call disable_window_border
        # or DwmExtendFrameIntoClientArea here — those strip WS_BORDER and break
        # native titlebar drag / aero-snap on the MAIN window.
        try:
            from PySide6.QtCore import QTimer as _QT
            def _apply():
                try:
                    enable_rounded_corners(self)
                except Exception:
                    pass
                try:
                    self.update()
                except Exception:
                    pass
            _QT.singleShot(0, _apply)
            _QT.singleShot(80, _apply)
        except Exception:
            try:
                enable_rounded_corners(self)
            except Exception:
                pass

