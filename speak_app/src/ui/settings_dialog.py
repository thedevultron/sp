"""SPEAK — Settings dialog. Authkit midnight: single central QSS, rounded cards,
animated sidebar + page fades, tooltip on every control.

Integration contract preserved for main.py:
  - Page order: 0=Setup 1=Guide 2=Prefs 3=Refine 4=Sessions 5=Help
  - self.tabs legacy alias (setCurrentIndex / count)
  - Signals: sig_new_session_requested, sig_grant_permission_requested
  - Public attrs: chk_screen, _update_status, update_permission_banner,
    refresh_sessions_ui, set_session_manager, btn_new_session, tabs, ...
  - Save/close/validation logic unchanged (zero behavior changes).
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel,
    QLineEdit, QPushButton, QListWidget, QSlider, QTextEdit,
    QCheckBox, QComboBox, QFrame, QMessageBox, QListWidgetItem,
    QScrollArea, QStackedWidget, QSpinBox, QRadioButton, QButtonGroup,
    QTableWidget, QTableWidgetItem, QHeaderView, QGraphicsOpacityEffect,
)
from PySide6.QtCore import (
    Qt, QSize, Signal, QTimer,
    QPropertyAnimation, QVariantAnimation, QEasingCurve, QAbstractAnimation,
)
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

# ---------------------------------------------------------------------------
# Central design system — one QSS source of truth for the whole dialog.
# Dialog-scoped: overrides capsule_style.qss only inside this widget tree.
# ---------------------------------------------------------------------------
DIALOG_QSS = """
/* ---- Base ---- */
QDialog#DialogRoot { background-color: #05060F; }
QLabel { background: transparent; color: #C7D3EA; font-size: 12px; }
QLabel#DisplayHeading {
    font-family: 'Space Grotesk', 'Inter', 'Segoe UI', sans-serif;
    font-size: 17px; font-weight: 600; color: #D8ECF8; letter-spacing: 0.2px;
}
QLabel#MutedLabel { color: #9DA7BA; font-size: 11px; }
QLabel#HintLabel { color: #7C91B6; font-size: 10px; }
QLabel#EyebrowLabel {
    font-family: 'JetBrains Mono', 'Cascadia Code', Consolas, monospace;
    font-size: 11px; letter-spacing: 2px; color: #7C91B6; background: transparent;
}
QLabel#CardTitle { color: #D8ECF8; font-size: 13px; font-weight: 600; }
QLabel#StatLabel { color: #B6D9FC; font-size: 12px; font-weight: 600; }
QLabel#WarnLabel { color: #FFB84D; font-size: 12px; }

/* ---- Scroll plumbing: content floats on the painted backdrop ---- */
QScrollArea { background: transparent; border: none; }
QScrollArea > QWidget > QWidget { background: transparent; }
QWidget#PageRoot { background: transparent; }

/* ---- Scrollbars: thin rounded, hover-bright, clear of the text ---- */
QScrollBar:vertical {
    background: transparent; width: 8px;
    margin: 2px 2px 2px 0px; border-radius: 4px;
}
QScrollBar::handle:vertical { background: #232C4E; min-height: 32px; border-radius: 4px; }
QScrollBar::handle:vertical:hover { background: #35426F; }
QScrollBar::handle:vertical:pressed { background: #46557F; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; width: 0px; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
QScrollBar:horizontal {
    background: transparent; height: 8px;
    margin: 0px 2px 2px 2px; border-radius: 4px;
}
QScrollBar::handle:horizontal { background: #232C4E; min-width: 32px; border-radius: 4px; }
QScrollBar::handle:horizontal:hover { background: #35426F; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; height: 0px; }
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }

/* ---- Cards: frost panel, 14px radius, text padded inside ---- */
QFrame#Card {
    background-color: #0A0E1CF0;
    border: 1px solid #1ABAD7F7;
    border-radius: 14px;
}
QFrame#Sidebar {
    background-color: #070B18F0;
    border: 1px solid #1ABAD7F7;
    border-radius: 14px;
}
QFrame#SettingsHeader, QFrame#ModelBar, QFrame#BottomBar {
    background: transparent; border: none;
}
QFrame#PermissionBanner {
    background-color: #2A1F0EE8;
    border: 1px solid #6B4A1E;
    border-radius: 12px;
}

/* ---- Info strips ---- */
QLabel#StripInfo {
    background-color: #0F1A33E8; color: #A8BEE8;
    border: 1px solid #1FBAD7F7; border-radius: 10px;
    padding: 9px 12px; font-size: 11px;
}
QLabel#StripOk {
    background-color: #0E2A1DE8; color: #7EE2A8;
    border: 1px solid #1E5B3A; border-radius: 10px;
    padding: 9px 12px; font-size: 11px;
}
QLabel#StripWarn {
    background-color: #2A1F0EE8; color: #FFB84D;
    border: 1px solid #6B4A1E; border-radius: 10px;
    padding: 9px 12px; font-size: 11px;
}

/* ---- Chips / kbd badges (tooltip-worthy small boxes) ---- */
QLabel#Chip {
    background-color: #14BAD7F7; color: #C7D3EA;
    border: 1px solid #1FBAD7F7; border-radius: 8px;
    padding: 4px 10px; font-size: 11px; font-weight: 500;
}
QLabel#ChipViolet {
    background-color: #241B4D; color: #D8ECF8;
    border: 1px solid #663AF3; border-radius: 8px;
    padding: 4px 10px; font-size: 11px; font-weight: 500;
}
QLabel#ChipGreen {
    background-color: #0E2A1D; color: #7EE2A8;
    border: 1px solid #1E5B3A; border-radius: 8px;
    padding: 4px 10px; font-size: 11px; font-weight: 500;
}
QLabel#Kbd {
    background-color: #10182E; color: #B6D9FC;
    border: 1px solid #27335A; border-radius: 8px;
    padding: 4px 10px;
    font-family: 'JetBrains Mono', Consolas, monospace;
    font-size: 11px; font-weight: 500;
}

/* ---- Inputs: 10px radius, generous inner padding ---- */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QComboBox {
    background-color: #070B18;
    border: 1px solid #1FBAD7F7;
    border-radius: 10px;
    padding: 8px 12px;
    color: #FFFFFF; font-size: 12px;
    selection-background-color: #663AF3;
    selection-color: #FFFFFF;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #663AF3;
    background-color: #0A1126;
}
QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
    background-color: #0A0D1D; color: #9DA7BA; border: 1px solid #0FBAD7F7;
}
QLineEdit::placeholder, QTextEdit::placeholder, QPlainTextEdit::placeholder { color: #71809F; }
QComboBox::drop-down { border: none; width: 26px; }
QComboBox QAbstractItemView {
    background-color: #0A0F20;
    border: 1px solid #33BAD7F7;
    border-radius: 10px;
    selection-background-color: #241B4D;
    selection-color: #FFFFFF;
    padding: 6px; outline: none;
}
QSpinBox::up-button, QSpinBox::down-button {
    background: transparent; border: none; width: 18px;
}

/* ---- Buttons: ghost default, violet CTA pill, danger ghost ---- */
QPushButton {
    background-color: #10BAD7F7;
    border: 1px solid #1FBAD7F7;
    border-radius: 10px;
    padding: 8px 16px;
    color: #D1E4FA; font-size: 12px; font-weight: 600;
}
QPushButton:hover {
    background-color: #1CBAD7F7;
    border-color: #33BAD7F7;
    color: #FFFFFF;
}
QPushButton:pressed { background-color: #0ABAD7F7; }
QPushButton:disabled { background-color: #0A0D1D; color: #5E6B85; border: 1px solid #0FBAD7F7; }

QPushButton#PrimaryButton {
    background-color: #663AF3;
    border: 1px solid #7A52FF;
    color: #FFFFFF; font-weight: 700;
    border-radius: 999px; padding: 9px 22px;
}
QPushButton#PrimaryButton:hover { background-color: #7550F5; border-color: #8A68FF; }
QPushButton#PrimaryButton:pressed { background-color: #552FD1; }
QPushButton#PrimaryButton:disabled { background-color: #1A2038; color: #9DA7BA; border: 1px solid #0FBAD7F7; }

QPushButton#SecondaryButton {
    background: transparent;
    border: 1px solid #1FBAD7F7;
    border-radius: 999px;
    color: #D1E4FA; padding: 9px 20px;
}
QPushButton#SecondaryButton:hover { background-color: #14BAD7F7; color: #FFFFFF; }

QPushButton#DangerButton {
    background: transparent;
    border: 1px solid #33E46D4C;
    color: #F0A08A;
}
QPushButton#DangerButton:hover {
    background-color: #14E46D4C;
    border-color: #55E46D4C;
    color: #FFFFFF;
}

QPushButton#NavButton {
    text-align: left;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 10px;
    padding: 9px 12px;
    color: #9DA7BA; font-size: 12px; font-weight: 500;
}
QPushButton#NavButton:hover { background-color: #14BAD7F7; color: #D8ECF8; }
QPushButton#NavButton:checked {
    background-color: #151138;
    border: 1px solid #2E663AF3;
    color: #FFFFFF; font-weight: 600;
}

QPushButton#GhostIconButton {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 6px;
}
QPushButton#GhostIconButton:hover {
    background-color: #14BAD7F7;
    border-color: transparent;
    color: #D8ECF8;
}

/* ---- Checkboxes / radios: rounded, violet checked ---- */
QCheckBox {
    spacing: 9px; color: #C7D3EA; font-size: 12px;
    padding: 3px 0px; background: transparent;
}
QCheckBox::indicator {
    width: 18px; height: 18px;
    border: 1px solid #1FBAD7F7;
    border-radius: 5px;
    background-color: #070B18;
}
QCheckBox::indicator:hover { border: 1px solid #663AF3; }
QCheckBox::indicator:checked { background-color: #663AF3; border: 1px solid #663AF3; }

QRadioButton {
    spacing: 9px; color: #C7D3EA; font-size: 12px;
    padding: 3px 0px; background: transparent;
}
QRadioButton::indicator {
    width: 16px; height: 16px;
    border: 1px solid #1FBAD7F7;
    border-radius: 9px;
    background-color: #070B18;
}
QRadioButton::indicator:hover { border: 1px solid #663AF3; }
QRadioButton::indicator:checked { background-color: #663AF3; border: 1px solid #663AF3; }

/* ---- Sliders: thin track, violet fill, white handle ---- */
QSlider::groove:horizontal {
    height: 4px; border-radius: 2px; background: #1A2340;
}
QSlider::sub-page:horizontal { background: #663AF3; border-radius: 2px; }
QSlider::add-page:horizontal { background: #1A2340; border-radius: 2px; }
QSlider::handle:horizontal {
    background: #FFFFFF;
    width: 14px; height: 14px;
    margin: -5px 0px;
    border-radius: 7px;
}
QSlider::handle:horizontal:hover { background: #D8ECF8; }
QSlider::handle:horizontal:pressed { background: #C7D3EA; }

/* ---- Lists: 10px, padded items, soft selection ---- */
QListWidget {
    background-color: #070B18;
    border: 1px solid #1ABAD7F7;
    border-radius: 10px;
    padding: 5px;
    outline: none;
    color: #C7D3EA; font-size: 11px;
}
QListWidget::item {
    background: transparent;
    border-radius: 7px;
    padding: 7px 10px;
    margin: 1px 0px;
    border: 1px solid transparent;
    color: #C7D3EA;
}
QListWidget::item:hover { background-color: #14BAD7F7; color: #FFFFFF; }
QListWidget::item:selected {
    background-color: #221A48;
    color: #FFFFFF;
    border: 1px solid #33663AF3;
}
QListWidget::item:selected:hover { background-color: #2A2055; }

/* ---- Table (Help cheat sheet) ---- */
QTableWidget {
    background-color: #070B18;
    border: 1px solid #1ABAD7F7;
    border-radius: 10px;
    gridline-color: #0FBAD7F7;
    color: #C7D3EA; font-size: 11px;
    selection-background-color: #241B4D;
    selection-color: #FFFFFF;
}
QTableWidget::item { padding: 6px 10px; border: none; }
QHeaderView::section {
    background-color: #0A0F20;
    color: #7C91B6;
    border: none;
    border-bottom: 1px solid #14BAD7F7;
    padding: 7px 10px;
    font-size: 10px; font-weight: 600;
}

/* ---- Tooltip: dark, hairline border, rounded ---- */
QToolTip {
    background-color: #0D1330;
    color: #D8ECF8;
    border: 1px solid #33BAD7F7;
    border-radius: 8px;
    padding: 7px 11px;
    font-size: 11px;
}
"""


def _small_muted(text: str) -> QLabel:
    l = QLabel(text)
    l.setObjectName("MutedLabel")
    l.setWordWrap(True)
    return l


def _eyebrow(text: str) -> QLabel:
    """All-caps section marker (dotDigital substitute: JetBrains Mono)."""
    l = QLabel(text.upper())
    l.setObjectName("EyebrowLabel")
    l.setAlignment(Qt.AlignmentFlag.AlignLeft)
    return l


def _strip(text: str, tone: str = "info") -> QLabel:
    """Inline notice strip — info / ok / warn."""
    l = QLabel(text)
    l.setObjectName({"ok": "StripOk", "warn": "StripWarn"}.get(tone, "StripInfo"))
    l.setWordWrap(True)
    return l


def _chip(text: str, tone: str = "frost") -> QLabel:
    """Small badge box (model / lock / status chips)."""
    l = QLabel(text)
    l.setObjectName({"violet": "ChipViolet", "green": "ChipGreen"}.get(tone, "Chip"))
    return l


def _kbd(text: str) -> QLabel:
    """Shortcut kbd badge for guide rows."""
    l = QLabel(text)
    l.setObjectName("Kbd")
    return l


def _card(title: str | None = None):
    """Rounded frost card with 14px radius — title renders INSIDE the card."""
    frame = QFrame()
    frame.setObjectName("Card")
    lay = QVBoxLayout(frame)
    lay.setContentsMargins(16, 13, 16, 14)
    lay.setSpacing(8)
    if title:
        t = QLabel(title)
        t.setObjectName("CardTitle")
        lay.addWidget(t)
    return frame, lay


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
    """Height-bounded list: minimum floor, optional cap — text never clipped."""

    def __init__(self, min_h=56, max_h=None, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(min_h)
        if max_h:
            self.setMaximumHeight(max_h)


class CompactText(QTextEdit):
    """Height-bounded text box: minimum floor, optional cap."""

    def __init__(self, min_h=88, max_h=None, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(min_h)
        if max_h:
            self.setMaximumHeight(max_h)
        self.setAcceptRichText(False)


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
        self._sidebar_anim = None
        self._page_anim = None
        self._session_manager = session_manager
        self._nav_buttons: list = []
        # Friendlier: allow Esc to hide to tray (not quit) — handled in reject().
        try:
            if ICON_PATH.exists():
                self.setWindowIcon(QIcon(str(ICON_PATH)))
        except Exception:
            pass
        self._init_ui()
        # Single central design system — one stylesheet, zero scattered inlines.
        self.setStyleSheet(DIALOG_QSS)
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
        """Wrap every page in an independent smooth vertical scroll area.
        Scrollbar look comes from the central DIALOG_QSS; content keeps a wide
        right gutter so text always sits fully inside its box, never under
        the scrollbar.
        """
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
        return scroll

    def _init_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # Minimalist header — single row wordmark + status, no dividers.
        header = QFrame()
        header.setObjectName("SettingsHeader")
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
        sub = QLabel("Voice dictation and companion")
        sub.setObjectName("MutedLabel")
        title_box.addWidget(t)
        title_box.addWidget(sub)
        h.addLayout(title_box, 1)
        self.lbl_api_status = _chip("Ready")
        self.lbl_api_status.setToolTip("Live API status — re-checks after Test or Save")
        h.addWidget(self.lbl_api_status, alignment=Qt.AlignmentFlag.AlignVCenter)
        main.addWidget(header)

        # Inline diagnostic banner (permission pending/denied) with Grant Permission retry
        self.permission_banner = QFrame()
        self.permission_banner.setObjectName("PermissionBanner")
        pb = QHBoxLayout(self.permission_banner)
        pb.setContentsMargins(14, 9, 14, 9)
        pb.setSpacing(10)
        self.lbl_permission = QLabel("")
        self.lbl_permission.setObjectName("WarnLabel")
        self.lbl_permission.setWordWrap(True)
        pb.addWidget(self.lbl_permission, 1)
        self.btn_grant_permission = QPushButton("Grant Permission")
        self.btn_grant_permission.setIcon(lucide_icon("shield-check", size=13, color="#FFFFFF"))
        self.btn_grant_permission.setObjectName("PrimaryButton")
        self.btn_grant_permission.setMinimumHeight(32)
        self.btn_grant_permission.setToolTip("Trigger native OS authorization, then retry capture automatically")
        self.btn_grant_permission.clicked.connect(lambda: self.sig_grant_permission_requested.emit())
        pb.addWidget(self.btn_grant_permission)
        self.btn_banner_dismiss = QPushButton("Later")
        self.btn_banner_dismiss.setMinimumHeight(32)
        self.btn_banner_dismiss.setToolTip("Dismiss for now — SPEAK keeps waiting for the OS in the background")
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
        body_lay.setContentsMargins(16, 10, 16, 10)
        body_lay.setSpacing(14)

        # Sidebar navigation
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setMinimumWidth(208)
        self.sidebar.setMaximumWidth(208)
        side_lay = QVBoxLayout(self.sidebar)
        side_lay.setContentsMargins(10, 10, 10, 10)
        side_lay.setSpacing(4)
        collapse_row = QHBoxLayout()
        collapse_row.setContentsMargins(2, 0, 2, 4)
        side_title = _eyebrow("Navigate")
        collapse_row.addWidget(side_title, 1)
        self.btn_collapse = QPushButton()
        self.btn_collapse.setIcon(lucide_icon("chevrons-left", size=14, color="#C7D3EA"))
        self.btn_collapse.setObjectName("GhostIconButton")
        self.btn_collapse.setFixedSize(30, 28)
        self.btn_collapse.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_collapse.setToolTip("Collapse sidebar for more room")
        self.btn_collapse.clicked.connect(self.toggle_sidebar)
        collapse_row.addWidget(self.btn_collapse)
        side_lay.addLayout(collapse_row)

        self._nav_defs = [
            ("Setup", "lock", "API keys — paste, test, and manage backups"),
            ("Guide", "book-open", "Shortcuts and capsule tour"),
            ("Preferences", "sliders", "Microphone, words, prompt, screen sharing"),
            ("Refine", "sparkles", "Prompts, voice triggers, custom actions"),
            ("Sessions", "layers", "Live sessions and stored history"),
            ("Help", "circle-help", "Feature guides, cheatsheet, quick fixes"),
        ]
        self._nav_buttons = []
        for idx, (name, ico, tip) in enumerate(self._nav_defs):
            b = QPushButton(name)
            try:
                b.setIcon(lucide_icon(ico, size=15, color="#C7D3EA"))
            except Exception:
                pass
            b.setCheckable(True)
            b.setObjectName("NavButton")
            b.setToolTip(tip)
            b.setMinimumHeight(38)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda _, i=idx: self.go_to_page(i))
            side_lay.addWidget(b)
            self._nav_buttons.append(b)
        side_lay.addStretch()
        hint = QLabel("Ctrl+Tab spawns a session")
        hint.setObjectName("HintLabel")
        hint.setWordWrap(True)
        hint.setToolTip("Ctrl+Tab instantly creates and switches to a fresh live session")
        side_lay.addWidget(hint)
        body_lay.addWidget(self.sidebar)

        # Stacked pages — each wrapped in its own smooth scroll area.
        # Wide 20px right gutter: text never runs under the scrollbar.
        self.stack = QStackedWidget()
        # Keep legacy alias: main.py uses settings_dialog.tabs.setCurrentIndex/count
        self.tabs = self.stack
        self.tab_keys = QWidget()
        self.tab_keys.setObjectName("PageRoot")
        self._build_key_tab(self.tab_keys)
        self.tab_guide = QWidget()
        self.tab_guide.setObjectName("PageRoot")
        self._build_guide_tab(self.tab_guide)
        self.tab_prefs = QWidget()
        self.tab_prefs.setObjectName("PageRoot")
        self._build_prefs_tab(self.tab_prefs)
        self.tab_refine = QWidget()
        self.tab_refine.setObjectName("PageRoot")
        self._build_refine_tab(self.tab_refine)
        self.tab_sessions = QWidget()
        self.tab_sessions.setObjectName("PageRoot")
        self._build_sessions_tab(self.tab_sessions)
        self.tab_help = QWidget()
        self.tab_help.setObjectName("PageRoot")
        self._build_help_tab(self.tab_help)
        # Order preserves legacy indices: 0 Setup, 1 Guide, 2 Prefs, 3 Refine, 4 Sessions, 5 Help
        for content in (self.tab_keys, self.tab_guide, self.tab_prefs, self.tab_refine, self.tab_sessions, self.tab_help):
            # Inner padding container so scroll content breathes
            pad = QWidget()
            pad_lay = QVBoxLayout(pad)
            pad_lay.setContentsMargins(6, 4, 20, 16)
            pad_lay.setSpacing(8)
            # Reparent content into pad
            content.setParent(pad)
            pad_lay.addWidget(content)
            pad_lay.addStretch()
            self.stack.addWidget(self._make_scroll_page(pad))
        body_lay.addWidget(self.stack, 1)
        main.addWidget(body, 1)

        # Engine bar — single minimalist row, no extra dividers.
        # Never shows model identifiers; the AI Engine is automatic.
        model_bar = QFrame()
        model_bar.setObjectName("ModelBar")
        ml = QHBoxLayout(model_bar)
        ml.setContentsMargins(16, 6, 16, 8)
        ml.setSpacing(8)
        models_lbl = _small_muted("Engine")
        ml.addWidget(models_lbl)
        self.lbl_engine = _chip("AI Engine", "violet")
        self.lbl_engine.setToolTip("The AI Engine is automatic — no model selection needed")
        ml.addWidget(self.lbl_engine)
        try:
            self.lbl_think = _chip(f"Thinking {config_vault.get_live_thinking_level()} · Transcription SMART", "green")
            self.lbl_think.setToolTip("Reasoning depth (Settings > Preferences) · Transcription locked SMART")
            ml.addWidget(self.lbl_think)
        except Exception:
            pass
        ml.addStretch()
        main.addWidget(model_bar)

        # Bottom bar — ghost Close + violet Save
        bottom = QFrame()
        bottom.setObjectName("BottomBar")
        bottom.setFixedHeight(70)
        bl = QHBoxLayout(bottom)
        bl.setContentsMargins(18, 12, 18, 12)
        bl.setSpacing(12)
        self.btn_cancel = QPushButton("Close")
        self.btn_cancel.setIcon(lucide_icon("x", size=15, color="#C7D3EA"))
        self.btn_cancel.setIconSize(QSize(15, 15))
        self.btn_cancel.setObjectName("SecondaryButton")
        self.btn_cancel.setMinimumHeight(42)
        self.btn_cancel.setMinimumWidth(140)
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setToolTip("Hide to tray — SPEAK keeps running")
        self.btn_cancel.clicked.connect(self.reject)
        bl.addWidget(self.btn_cancel)
        bl.addStretch()
        self.btn_save = QPushButton("Save & Launch")
        self.btn_save.setObjectName("PrimaryButton")
        self.btn_save.setIcon(lucide_icon("check", size=16, color="#FFFFFF"))
        self.btn_save.setIconSize(QSize(16, 16))
        self.btn_save.setMinimumHeight(42)
        self.btn_save.setMinimumWidth(190)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setToolTip("Validate settings, save, and launch SPEAK into the tray")
        self.btn_save.clicked.connect(self._save_and_close)
        bl.addWidget(self.btn_save)
        main.addWidget(bottom)

        self.stack.currentChanged.connect(self._on_tab_changed)
        try:
            self._sync_nav(self.stack.currentIndex())
        except Exception:
            pass

    def toggle_sidebar(self):
        """Collapse/expand with a smooth 190 ms width animation (not a snap)."""
        self._sidebar_collapsed = not self._sidebar_collapsed
        collapsed = self._sidebar_collapsed
        target = 58 if collapsed else 208
        try:
            for b, (name, _ico, tip) in zip(self._nav_buttons, self._nav_defs):
                b.setText("" if collapsed else name)
                b.setToolTip(tip)
            self.btn_collapse.setIcon(lucide_icon(
                "chevrons-right" if collapsed else "chevrons-left",
                size=14, color="#C7D3EA"))
            self.btn_collapse.setToolTip(
                "Expand sidebar" if collapsed else "Collapse sidebar for more room")
        except Exception:
            pass
        try:
            prev = getattr(self, "_sidebar_anim", None)
            if prev is not None:
                try:
                    prev.stop()
                except Exception:
                    pass
        except Exception:
            pass
        try:
            start = max(1, self.sidebar.width())
            anim = QVariantAnimation(self)
            anim.setDuration(190)
            anim.setStartValue(start)
            anim.setEndValue(target)
            anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

            def _widen(v):
                try:
                    self.sidebar.setMinimumWidth(int(v))
                    self.sidebar.setMaximumWidth(int(v))
                except Exception:
                    pass

            anim.valueChanged.connect(_widen)
            anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
            self._sidebar_anim = anim
        except Exception:
            try:
                self.sidebar.setMinimumWidth(target)
                self.sidebar.setMaximumWidth(target)
            except Exception:
                pass

    def _animate_page_in(self, page: QWidget):
        """170 ms fade on the incoming page — soft switch, no hard cut."""
        if page is None:
            return
        try:
            try:
                page.setGraphicsEffect(None)
            except Exception:
                pass
            eff = QGraphicsOpacityEffect(page)
            page.setGraphicsEffect(eff)
            anim = QPropertyAnimation(eff, b"opacity", page)
            anim.setDuration(170)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)

            def _cleanup(p=page):
                try:
                    if p.graphicsEffect() is not None:
                        p.setGraphicsEffect(None)
                except Exception:
                    pass

            anim.finished.connect(_cleanup)
            anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
            self._page_anim = anim
        except Exception:
            try:
                page.setGraphicsEffect(None)
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
        try:
            self._animate_page_in(self.stack.widget(idx))
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
                    line = f"{marker}[{sid}] {mode} · {status} · {words} words · {created}"
                    item = QListWidgetItem(line)
                    try:
                        item.setData(Qt.ItemDataRole.UserRole, sid)
                        item.setToolTip(f"Session {sid}\nMode: {mode} · Status: {status}\n{words} words · {created}")
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

    def _build_key_tab(self, w: QWidget):
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        # Compact info - free tier notice, never mention embedded key value
        try:
            from src._embedded_key import get_embedded_key as _gek
            _has_free = bool(_gek())
        except Exception:
            _has_free = False
        if _has_free:
            lay.addWidget(_strip("Free tier active — no key needed. Add your own key above for unlimited use. If you add one, yours is used instead.", "ok"))
        else:
            lay.addWidget(_strip("Keys stored in Windows Credential Manager. Only sent to Google.", "info"))

        # Primary key
        card, cl = _card("Primary API key")
        cl.addWidget(_small_muted("Gemini API key from Google AI Studio (aistudio.google.com)"))
        self.txt_primary = QLineEdit()
        self.txt_primary.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_primary.setPlaceholderText("Paste API key...")
        self.txt_primary.setClearButtonEnabled(True)
        self.txt_primary.setMinimumHeight(38)
        self.txt_primary.setMaxLength(256)
        self.txt_primary.setToolTip("Your Google AI Studio key. Stored in Windows Credential Manager — never in plain files.")
        cl.addWidget(self.txt_primary)
        row = QHBoxLayout()
        row.setSpacing(10)
        self.chk_show_key = QCheckBox("Show")
        self.chk_show_key.setToolTip("Reveal or mask the pasted key")
        self.chk_show_key.toggled.connect(lambda c: self.txt_primary.setEchoMode(QLineEdit.EchoMode.Normal if c else QLineEdit.EchoMode.Password))
        row.addWidget(self.chk_show_key)
        row.addStretch()
        btn_test = QPushButton("Test")
        btn_test.setIcon(lucide_icon("zap", size=13, color="#B6D9FC"))
        btn_test.setObjectName("SecondaryButton")
        btn_test.setMinimumHeight(32)
        btn_test.setToolTip("Ping Google with this key to verify it works before saving")
        btn_test.clicked.connect(self._test_primary_key)
        row.addWidget(btn_test)
        cl.addLayout(row)
        lay.addWidget(card)

        # Backup keys — MASKED display (full key in UserRole only)
        card2, c2 = _card("Backup keys — auto switch on quota")
        c2.addWidget(_small_muted("Stored in Windows Credential Manager. List shows masked preview only."))
        self.list_backups = CompactList(min_h=64, max_h=150)
        self.list_backups.setToolTip("Backup keys — SPEAK rotates to the next one automatically when quota hits")
        c2.addWidget(self.list_backups)
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        self.txt_new_backup = QLineEdit()
        self.txt_new_backup.setPlaceholderText("Paste backup key")
        self.txt_new_backup.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_new_backup.setClearButtonEnabled(True)
        self.txt_new_backup.setMinimumHeight(36)
        self.txt_new_backup.setMaxLength(256)
        self.txt_new_backup.setToolTip("Add a spare key — used automatically when the primary runs out")
        row2.addWidget(self.txt_new_backup, 1)
        btn_add = QPushButton("Add")
        btn_add.setIcon(lucide_icon("plus", size=12, color="#D1E4FA"))
        btn_add.setMinimumHeight(34)
        btn_add.setToolTip("Append this key to the backup pool")
        btn_add.clicked.connect(self._add_backup)
        row2.addWidget(btn_add)
        btn_del = QPushButton("Remove")
        btn_del.setIcon(lucide_icon("trash-2", size=12, color="#F0A08A"))
        btn_del.setObjectName("DangerButton")
        btn_del.setMinimumHeight(34)
        btn_del.setToolTip("Remove the selected backup key")
        btn_del.clicked.connect(self._remove_backup)
        row2.addWidget(btn_del)
        c2.addLayout(row2)
        self.txt_new_backup.returnPressed.connect(self._add_backup)
        lay.addWidget(card2)

        # AI Engine — fully automatic, no model selection exposed.
        mcard, mcl = _card("AI Engine")
        mcl.addWidget(_small_muted("The engine picks the best configuration automatically. Reasoning depth is adjustable in Preferences."))
        lay.addWidget(mcard)

        hint = _small_muted("After save, capsule appears only on hotkey. Check Guide for shortcuts.")
        hint.setToolTip("The floating capsule stays hidden until you press Ctrl+Space or Ctrl+/")
        lay.addWidget(hint)
        lay.addStretch()

    def _build_guide_tab(self, w: QWidget):
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        def grow_row(icon, title, keys, desc):
            r, rl = _card(None)
            rl.setContentsMargins(14, 12, 14, 12)
            row_l = QHBoxLayout()
            row_l.setContentsMargins(0, 0, 0, 0)
            row_l.setSpacing(12)
            ic = QLabel()
            ic.setPixmap(lucide_pixmap(icon, size=18, color="#B6D9FC"))
            ic.setFixedSize(18, 18)
            ic.setToolTip(title)
            row_l.addWidget(ic, alignment=Qt.AlignmentFlag.AlignTop)
            mid = QVBoxLayout()
            mid.setSpacing(3)
            title_l = QLabel(title)
            title_l.setObjectName("CardTitle")
            mid.addWidget(title_l)
            desc_l = QLabel(desc)
            desc_l.setObjectName("MutedLabel")
            desc_l.setWordWrap(True)
            mid.addWidget(desc_l)
            row_l.addLayout(mid, 1)
            badge = _kbd(keys)
            badge.setToolTip(f"Press {keys}")
            row_l.addWidget(badge, alignment=Qt.AlignmentFlag.AlignTop)
            rl.addLayout(row_l)
            return r

        lay.addWidget(_eyebrow("Shortcuts"))
        lay.addWidget(grow_row("mic", "Dictation", "Ctrl + Space", "Speak. Types at cursor."))
        lay.addWidget(grow_row("monitor", "Companion", "Ctrl + /", "Live voice + motion-burst screen. Toggle screen in capsule."))
        lay.addWidget(grow_row("layers", "Purge", "Ctrl + Win", "Clear memory and session (refine deletes since purge)."))
        lay.addWidget(grow_row("sparkles", "Refine", "Say refine", "Refine / Polish / Elaborate session. Triggers + prompts editable in Refine tab."))
        tip = _strip("Capsule (close-only) is hidden until hotkey. Find SPEAK in system tray near the clock.", "info")
        tip.setToolTip("Right-click the tray icon for quick actions")
        lay.addWidget(tip)

        caps, cpl = _card("Capsule")
        for txt in [
            "Hotkeys open the mini pill first. Click it (or the maximize button) to expand the full capsule.",
            "Settings is the main window (min / max / close). Capsule keeps close only.",
            "Dot idle fog, active blueprint, error ember. Bars pulse with mic and voice.",
            "Transcript panel: copy, clear, refine/polish/elaborate + customs. Screen button toggles live vision.",
            "Refine deletes the whole session text, then types the result. Say elaborate (or old expand).",
        ]:
            l = QLabel(txt)
            l.setObjectName("MutedLabel")
            l.setWordWrap(True)
            cpl.addWidget(l)
        lay.addWidget(caps)
        lay.addStretch()

    def _build_prefs_tab(self, w: QWidget):
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        # Top row: Mic | Custom words — side by side to save height
        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        mic_card, ml = _card("Microphone")
        self.combo_audio = QComboBox()
        self.combo_audio.setMinimumHeight(36)
        # Bound the min width to ~14 chars: long device names live in the
        # popup (which auto-sizes), never force the card wider than the page.
        self.combo_audio.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.combo_audio.setMinimumContentsLength(14)
        self.combo_audio.setToolTip("Input device used for dictation and companion")
        self.combo_audio.addItem("Default microphone", userData=None)
        try:
            for idx, name in AudioEngine.get_input_devices():
                self.combo_audio.addItem(f"[{idx}] {name}", userData=idx)
        except Exception:
            pass
        ml.addWidget(self.combo_audio)
        btn_ref = QPushButton("Refresh")
        btn_ref.setIcon(lucide_icon("refresh", size=12, color="#B6D9FC"))
        btn_ref.setMinimumHeight(30)
        btn_ref.setToolTip("Rescan input devices (use after plug / unplug)")
        btn_ref.clicked.connect(self._refresh_audio_devices)
        ml.addWidget(btn_ref)
        self.btn_test_speaker = QPushButton("Test speaker")
        self.btn_test_speaker.setIcon(lucide_icon("volume-2", size=12, color="#B6D9FC"))
        self.btn_test_speaker.setMinimumHeight(30)
        self.btn_test_speaker.setToolTip("Play a test tone through the real reply-audio path (proves speaker wiring + pitch)")
        self.btn_test_speaker.clicked.connect(self._test_speaker)
        ml.addWidget(self.btn_test_speaker)
        self.lbl_speaker_proof = QLabel("")
        self.lbl_speaker_proof.setObjectName("MutedLabel")
        self.lbl_speaker_proof.setWordWrap(True)
        self.lbl_speaker_proof.setToolTip("Result of the last speaker test")
        ml.addWidget(self.lbl_speaker_proof)
        ml.addWidget(_small_muted("Tip: wear headphones — speakers bleed into the mic causes squeal/echo."))
        ml.addStretch()
        top_row.addWidget(mic_card, 1)

        vocab_card, vl = _card("Custom words and mark")
        vm_row = QHBoxLayout()
        vm_row.setSpacing(10)
        left_col = QVBoxLayout()
        left_col.setSpacing(4)
        left_col.addWidget(_small_muted("Words"))
        self.txt_custom_words = QLineEdit()
        self.txt_custom_words.setPlaceholderText("e.g. AcmeCorp, Figma")
        self.txt_custom_words.setClearButtonEnabled(True)
        self.txt_custom_words.setMinimumHeight(32)
        self.txt_custom_words.setToolTip("Vocabulary boosts — comma-separated names SPEAK should transcribe reliably")
        left_col.addWidget(self.txt_custom_words)
        vm_row.addLayout(left_col, 1)
        right_col = QVBoxLayout()
        right_col.setSpacing(4)
        right_col.addWidget(_small_muted("Mark"))
        self.txt_custom_mark = QLineEdit()
        self.txt_custom_mark.setPlaceholderText("e.g. My Studio")
        self.txt_custom_mark.setMaxLength(120)
        self.txt_custom_mark.setClearButtonEnabled(True)
        self.txt_custom_mark.setMinimumHeight(32)
        self.txt_custom_mark.setToolTip("Signature context — who or what this SPEAK install is for")
        right_col.addWidget(self.txt_custom_mark)
        vm_row.addLayout(right_col, 1)
        vl.addLayout(vm_row)
        self.list_words = CompactList(min_h=44, max_h=110)
        self.list_words.setToolTip("Current custom words — attached to every dictation request")
        vl.addWidget(self.list_words)
        roww = QHBoxLayout()
        roww.setSpacing(8)
        btn_add_word = QPushButton("Add")
        btn_add_word.setIcon(lucide_icon("plus", size=12, color="#D1E4FA"))
        btn_add_word.setMinimumHeight(30)
        btn_add_word.setToolTip("Add words (comma-separated) to the boost list")
        btn_add_word.clicked.connect(self._add_custom_words)
        roww.addWidget(btn_add_word)
        btn_clear_words = QPushButton("Clear")
        btn_clear_words.setIcon(lucide_icon("trash-2", size=12, color="#9DA7BA"))
        btn_clear_words.setMinimumHeight(30)
        btn_clear_words.setToolTip("Remove all custom words")
        btn_clear_words.clicked.connect(self._clear_custom_words)
        roww.addWidget(btn_clear_words)
        roww.addStretch()
        vl.addLayout(roww)
        self.txt_custom_words.returnPressed.connect(self._add_custom_words)
        self.txt_custom_mark.returnPressed.connect(self._add_custom_words)
        top_row.addWidget(vocab_card, 1.2)
        lay.addLayout(top_row)

        # System prompt
        prompt_card, pl = _card("System prompt")
        self.txt_prompt = CompactText(min_h=96, max_h=240)
        self.txt_prompt.setPlaceholderText("You are SPEAK, a fast companion...")
        self.txt_prompt.setToolTip("Base instruction the AI follows in every companion session")
        pl.addWidget(self.txt_prompt)
        lay.addWidget(prompt_card)

        # Creativity + screen toggle row
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        temp_card, tl = _card("Creativity")
        t_row = QHBoxLayout()
        precise_lbl = QLabel("Precise")
        precise_lbl.setObjectName("MutedLabel")
        precise_lbl.setToolTip("Low temperature — exact, literal output")
        t_row.addWidget(precise_lbl)
        t_row.addStretch()
        self.lbl_temp = QLabel("0.20")
        self.lbl_temp.setObjectName("StatLabel")
        self.lbl_temp.setToolTip("Current temperature (0.00 precise → 2.00 creative)")
        t_row.addWidget(self.lbl_temp)
        t_row.addStretch()
        creative_lbl = QLabel("Creative")
        creative_lbl.setObjectName("MutedLabel")
        creative_lbl.setToolTip("High temperature — more inventive output")
        t_row.addWidget(creative_lbl)
        tl.addLayout(t_row)
        self.slider_temp = QSlider(Qt.Orientation.Horizontal)
        self.slider_temp.setRange(0, 200)
        self.slider_temp.setValue(20)
        self.slider_temp.setToolTip("Temperature 0.00–2.00 — lower is more exact, higher is more inventive")
        self.slider_temp.valueChanged.connect(lambda v: self.lbl_temp.setText(f"{v/100:.2f}"))
        tl.addWidget(self.slider_temp)
        row2.addWidget(temp_card, 1)

        screen_card, sl = _card("Live Screen")
        self.chk_screen = QCheckBox("Share live screen")
        self.chk_screen.setChecked(True)
        self.chk_screen.setToolTip("Share live screen in companion (motion bursts, ~1 fps when still). When off, companion is voice only.")
        sl.addWidget(self.chk_screen)
        sl.addWidget(_small_muted("Synced with capsule screen button. Takes effect live."))
        detail_row = QHBoxLayout()
        detail_row.setContentsMargins(0, 0, 0, 0)
        detail_row.setSpacing(8)
        detail_lbl = QLabel("Detail")
        detail_lbl.setToolTip("Frame detail: vision clarity per frame vs context burn")
        detail_row.addWidget(detail_lbl)
        self.combo_screen_detail = QComboBox()
        self.combo_screen_detail.setMinimumHeight(32)
        # Bound min width like the mic combo: long names live in the popup.
        self.combo_screen_detail.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.combo_screen_detail.setMinimumContentsLength(10)
        self.combo_screen_detail.addItem("Medium · 560", userData="MEDIUM")
        self.combo_screen_detail.addItem("High · 1120", userData="HIGH")
        self.combo_screen_detail.setToolTip("Frame detail: MEDIUM 560 tokens/frame (default, balanced) · HIGH 1120 tokens/frame (max clarity, ~2x context burn).")
        detail_row.addWidget(self.combo_screen_detail, 1)
        sl.addLayout(detail_row)
        self.btn_test_capture = QPushButton("Test capture")
        self.btn_test_capture.setIcon(lucide_icon("monitor", size=12, color="#B6D9FC"))
        self.btn_test_capture.setMinimumHeight(30)
        self.btn_test_capture.setToolTip("Grab one frame now — proves images actually flow (size shown below)")
        self.btn_test_capture.clicked.connect(self._test_capture)
        sl.addWidget(self.btn_test_capture)
        self.lbl_capture_proof = QLabel("")
        self.lbl_capture_proof.setObjectName("MutedLabel")
        self.lbl_capture_proof.setWordWrap(True)
        self.lbl_capture_proof.setToolTip("Result of the last capture test")
        sl.addWidget(self.lbl_capture_proof)
        row2.addWidget(screen_card, 1)
        lay.addLayout(row2)

        # Message Verification toggle (was _extend_prefs_with_tool_controls)
        ver_card, vcl = _card("Message Verification")
        vcl.addWidget(_small_muted("Controls requireVerification / autoSubmit on every tool call."))
        self.verification_group = QButtonGroup(self)
        # Short labels keep the card narrow; full flags live in tooltips.
        self.radio_verification_active = QRadioButton("Verification Active")
        self.radio_verification_active.setToolTip("Type text, wait for your confirmation before Enter. (requireVerification=True, autoSubmit=False)")
        self.radio_auto_send = QRadioButton("Auto-Send (Default)")
        self.radio_auto_send.setToolTip("Type text and press Enter automatically. (requireVerification=False, autoSubmit=True)")
        for r in (self.radio_verification_active, self.radio_auto_send):
            self.verification_group.addButton(r)
            vcl.addWidget(r)
        try:
            mode = config_vault.get_verification_mode()
            if mode == "auto_send":
                self.radio_auto_send.setChecked(True)
            else:
                self.radio_verification_active.setChecked(True)
        except Exception:
            self.radio_verification_active.setChecked(True)
        lay.addWidget(ver_card)

        # Agent Reasoning — thinking depth is user-selectable now.
        # Only transcription stays locked (SMART).
        reason_card, rl = _card("Agent Reasoning")
        rl.addWidget(_small_muted("Reasoning depth for the AI Engine. Applies on next connect."))
        self.thinking_group = QButtonGroup(self)
        self.radio_think_low = QRadioButton("Low — fastest")
        self.radio_think_low.setToolTip("Lowest latency, light reasoning.")
        self.radio_think_medium = QRadioButton("Medium (Default)")
        self.radio_think_medium.setToolTip("Background reasoning for multi-step tasks (default).")
        self.radio_think_high = QRadioButton("High — deepest")
        self.radio_think_high.setToolTip("Maximum reasoning effort, slower replies.")
        for r in (self.radio_think_low, self.radio_think_medium, self.radio_think_high):
            self.thinking_group.addButton(r)
            rl.addWidget(r)
        try:
            _lv = config_vault.get_live_thinking_level()
            {"LOW": self.radio_think_low, "MEDIUM": self.radio_think_medium, "HIGH": self.radio_think_high}.get(_lv, self.radio_think_medium).setChecked(True)
        except Exception:
            self.radio_think_medium.setChecked(True)
        lay.addWidget(reason_card)

        # Transcription lock (read-only)
        locks_card, ll2 = _card("Live Configuration Locks")
        ll2.addWidget(_small_muted("Enforced on every Live connect — not editable."))
        brow = QHBoxLayout()
        brow.setSpacing(8)
        for txt, tip in (("Transcription: SMART", "High-accuracy context awareness, locked"), ("Tools: type + pc actions", "Type at cursor plus desktop control, with memory. Full authority: acts immediately, no confirmation asks")):
            badge = _chip(txt, "green")
            badge.setToolTip(tip)
            brow.addWidget(badge)
        brow.addStretch()
        ll2.addLayout(brow)
        lay.addWidget(locks_card)

        # Startup
        self.chk_startup = QCheckBox("Launch on Windows startup")
        self.chk_startup.setToolTip("Start SPEAK automatically when Windows starts")
        lay.addWidget(self.chk_startup)
        lay.addStretch()

    def _build_refine_tab(self, w: QWidget):
        # Flat layout — the page already lives inside its own scroll area
        # (no nested scroll-in-scroll so text boxes size naturally).
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)
        lay.addWidget(_eyebrow("Refine prompts"))
        lay.addWidget(_strip("Refine deletes everything typed this session (since purge / dictation start), then types the result. Edit prompts + voice triggers below. Custom actions appear in capsule, tray, and voice.", "info"))
        self._refine_prompt_edits = {}
        self._refine_trigger_edits = {}
        for aid, title, hint in [
            ("refine", "Refine", "Self-correction aware cleanup"),
            ("polish", "Polish", "Publication-ready polish"),
            ("elaborate", "Elaborate", "Expand with detail (voice: elaborate or expand)"),
        ]:
            grp, gl = _card(title)
            gl.addWidget(_small_muted(hint))
            te = CompactText(min_h=88, max_h=170)
            te.setPlaceholderText(f"Prompt for {title}...")
            te.setToolTip(f"Instruction sent to Fast-Lite when you say «{title}». Output replaces the session text.")
            gl.addWidget(te)
            self._refine_prompt_edits[aid] = te
            trow = QHBoxLayout()
            trow.setSpacing(6)
            trig_lbl = _small_muted("Voice triggers (comma-separated):")
            trow.addWidget(trig_lbl)
            le = QLineEdit()
            le.setPlaceholderText("e.g. refine" if aid == "refine" else ("e.g. polish" if aid == "polish" else "e.g. elaborate, expand"))
            le.setClearButtonEnabled(True)
            le.setMinimumHeight(32)
            le.setMaxLength(120)
            le.setToolTip("Say any of these words to trigger. Lowercase letters/numbers/hyphen only.")
            trow.addWidget(le, 1)
            gl.addLayout(trow)
            self._refine_trigger_edits[aid] = le
            lay.addWidget(grp)
        # Custom actions (up to 3)
        cgrp, cl = _card("Custom actions (up to 3)")
        cl.addWidget(_small_muted("Each: display name, single voice trigger, prompt. Shows in capsule + tray + voice when enabled."))
        self._custom_rows = []
        for i in range(3):
            row = QVBoxLayout()
            row.setSpacing(6)
            top = QHBoxLayout()
            top.setSpacing(8)
            en = QCheckBox(f"Custom {i+1}")
            en.setChecked(False)
            en.setToolTip(f"Show Custom {i+1} in the capsule, tray, and voice commands")
            top.addWidget(en)
            nm = QLineEdit()
            nm.setPlaceholderText("Name e.g. Summarize")
            nm.setMaxLength(24)
            nm.setClearButtonEnabled(True)
            nm.setMinimumHeight(32)
            nm.setToolTip("Display name shown in capsule and tray")
            top.addWidget(nm, 1)
            tr = QLineEdit()
            tr.setPlaceholderText("trigger e.g. summarize")
            tr.setMaxLength(24)
            tr.setClearButtonEnabled(True)
            tr.setMinimumHeight(32)
            tr.setToolTip("Single voice word (a-z, 0-9, hyphen, 2-24 chars). Must be unique.")
            top.addWidget(tr, 1)
            row.addLayout(top)
            pr = CompactText(min_h=64, max_h=130)
            pr.setPlaceholderText("Prompt e.g. Summarize the following text in 3 bullets. Output ONLY the summary:")
            pr.setToolTip("Instruction sent to Fast-Lite when you say the trigger word")
            row.addWidget(pr)
            cl.addLayout(row)
            self._custom_rows.append({"enabled": en, "name": nm, "trigger": tr, "prompt": pr})
        lay.addWidget(cgrp)
        reset_row = QHBoxLayout()
        reset_row.addStretch()
        self.btn_refine_reset = QPushButton("Reset refine defaults")
        self.btn_refine_reset.setIcon(lucide_icon("refresh", size=12, color="#B6D9FC"))
        self.btn_refine_reset.setMinimumHeight(32)
        self.btn_refine_reset.setToolTip("Restore default prompts + triggers (clears customs)")
        self.btn_refine_reset.clicked.connect(self._reset_refine_defaults)
        reset_row.addWidget(self.btn_refine_reset)
        lay.addLayout(reset_row)
        lay.addStretch()

    def _build_sessions_tab(self, w: QWidget):
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)
        lay.addWidget(_eyebrow("Multi-Session Engine"))
        lay.addWidget(_strip("Ctrl + Tab immediately spawns and switches to a new live session. Oldest stored sessions evict first (FIFO) when over the limit.", "info"))
        grp, gl = _card("Session Controls")
        row = QHBoxLayout()
        row.setSpacing(10)
        max_lbl = QLabel("Max Stored Sessions")
        max_lbl.setToolTip("How many past sessions SPEAK keeps before FIFO eviction")
        row.addWidget(max_lbl)
        self.slider_max_sessions = QSlider(Qt.Orientation.Horizontal)
        self.slider_max_sessions.setRange(1, 20)
        self.slider_max_sessions.setValue(5)
        self.slider_max_sessions.setToolTip("FIFO eviction threshold (default 5)")
        self.slider_max_sessions.valueChanged.connect(self._on_max_sessions_changed)
        row.addWidget(self.slider_max_sessions, 1)
        self.spin_max_sessions = QSpinBox()
        self.spin_max_sessions.setRange(1, 20)
        self.spin_max_sessions.setValue(5)
        self.spin_max_sessions.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.spin_max_sessions.setMinimumHeight(32)
        self.spin_max_sessions.setToolTip("Exact count — mirrors the slider")
        self.spin_max_sessions.valueChanged.connect(self._on_max_sessions_changed)
        row.addWidget(self.spin_max_sessions)
        gl.addLayout(row)
        self.lbl_session_count = QLabel("Active sessions: 0 · Stored: 0 / 5")
        self.lbl_session_count.setObjectName("StatLabel")
        self.lbl_session_count.setToolTip("Live sessions right now vs kept on disk")
        gl.addWidget(self.lbl_session_count)
        gl.addWidget(_small_muted("Stored session metadata (newest first). Active session marked ●."))
        self.list_sessions = QListWidget()
        self.list_sessions.setMinimumHeight(120)
        self.list_sessions.setMaximumHeight(260)
        self.list_sessions.setToolTip("Stored sessions — FIFO evicts oldest when over Max. Hover any row for details.")
        gl.addWidget(self.list_sessions)
        btn_row = QHBoxLayout()
        self.btn_new_session = QPushButton("New Session (Ctrl+Tab)")
        try:
            self.btn_new_session.setIcon(lucide_icon("plus", size=13, color="#FFFFFF"))
        except Exception:
            pass
        self.btn_new_session.setObjectName("PrimaryButton")
        self.btn_new_session.setMinimumHeight(34)
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
        lay.setSpacing(10)
        lay.addWidget(_eyebrow("Help & Documentation"))
        # Feature Directory
        feat, fl = _card("Feature Directory — step-by-step")
        for title, steps in [
            ("Screen Share", ["1. Enable Preferences > Live Screen or capsule monitor button.", "2. Grant OS screen permission when the banner appears.", "3. Start Companion (Ctrl+/) — live vision bursts on change (~1 fps still).", "4. Toggle screen mid-session; voice never drops."]),
            ("Live Transcription", ["1. Press Ctrl+Space to dictate.", "2. Speak — interim shows live, finals append with SMART accuracy.", "3. Text types at cursor automatically.", "4. Say refine / polish / elaborate or tap capsule buttons."]),
            ("Smart Insertion", ["1. Place cursor in any app input field.", "2. Dictate or trigger typeTextAtCursor via companion.", "3. Auto-Send submits instantly; Verification Active waits for your Enter.", "4. Tone adapts: formal for docs, friendly for chat, concise for code."]),
        ]:
            t = QLabel(title)
            t.setObjectName("CardTitle")
            t.setToolTip(f"How to use {title}")
            fl.addWidget(t)
            for s in steps:
                l = QLabel(s)
                l.setObjectName("MutedLabel")
                l.setWordWrap(True)
                l.setIndent(12)
                fl.addWidget(l)
        lay.addWidget(feat)
        # Shortcut Cheat Sheet table
        cheat, cl = _card("Shortcut Cheat Sheet")
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Keys", "Action"])
        rows = [
            ("Ctrl + Tab", "Spawn + switch to new live session"),
            ("Ctrl + Space", "Dictation on/off (types at cursor)"),
            ("Ctrl + /", "Companion voice + screen"),
            ("Ctrl + Win", "Purge memory + hard reset"),
            ("Esc", "Stop live session only (app keeps running)"),
            ("F11 / Maximize", "Fullscreen settings"),
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
            ki.setToolTip(f"Press {k}")
            ai.setToolTip(f"{k}: {a}")
            table.setItem(i, 0, ki)
            table.setItem(i, 1, ai)
        try:
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            table.verticalHeader().setVisible(False)
            table.verticalHeader().setDefaultSectionSize(32)
        except Exception:
            pass
        table.setMinimumHeight(170)
        table.setMaximumHeight(240)
        table.setToolTip("Every SPEAK shortcut at a glance")
        cl.addWidget(table)
        lay.addWidget(cheat)
        # Troubleshooting
        trouble, tl = _card("Troubleshooting — quick fixes")
        for q, a in [
            ("Cursor not typing?", "Focus the target app input first (not SPEAK). Check Verification mode. Retry dictation; InjectionService skips when SPEAK is focused."),
            ("OS permission banner?", "Click Grant Permission. On Windows open Privacy > Screen recording and allow. On macOS allow in System Settings > Privacy > Screen Recording, then retry."),
            ("Mic silent?", "Settings > Preferences > Microphone — pick device, Refresh, restart dictation. Watch capsule wave bars."),
            ("Live connect failing?", "Check API keys (Setup) and network. Failover rotates keys; 3 fails in 30s stops loudly."),
        ]:
            ql = QLabel(q)
            ql.setObjectName("CardTitle")
            tl.addWidget(ql)
            al = QLabel(a)
            al.setObjectName("MutedLabel")
            al.setWordWrap(True)
            al.setIndent(12)
            tl.addWidget(al)
        lay.addWidget(trouble)
        lay.addStretch()

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

    def _test_capture(self):
        """One-frame proof that screen images actually flow (never silent)."""
        try:
            self.lbl_capture_proof.setText("Capturing...")
        except Exception:
            pass
        # Synchronous: one grab + encode is ~50-150 ms, no thread-marshal bugs.
        try:
            from PySide6.QtWidgets import QApplication as QA
            QA.processEvents()
        except Exception:
            pass
        try:
            from src.screen_engine import ScreenEngine
            eng = ScreenEngine()
            eng.check_permission()
            jpeg = eng.capture_frame_bytes()
            info = getattr(eng, "last_frame_info", "")
            if jpeg:
                try:
                    _ft = {"LOW": 280, "MEDIUM": 560, "HIGH": 1120}.get(config_vault.get_screen_detail(), 560)
                except Exception:
                    _ft = 560
                msg = f"Vision OK — {len(jpeg) // 1024} KB frame ({info}), ~{_ft} tokens. The AI will see this."
                col = "green"
            else:
                try:
                    from src.permission_manager import permission_manager as _pm
                    err = _pm.last_error or eng._perm_error
                except Exception:
                    err = ""
                msg = ("Blank — permission blocked. Click Grant Permission above, approve, "
                       "then Test capture again." + (f" ({err[:80]})" if err else ""))
                col = "red"
            # Color the inline proof via the matching chip-style strip
            try:
                ok = bool(col == "green")
                self.lbl_capture_proof.setText(msg)
                if ok:
                    self.lbl_capture_proof.setStyleSheet("color: #7EE2A8;")
                else:
                    self.lbl_capture_proof.setStyleSheet("color: #F0A08A;")
            except Exception:
                pass
        except Exception as e:
            msg = f"Capture error: {str(e)[:100]}"
            try:
                self.lbl_capture_proof.setText(msg)
                self.lbl_capture_proof.setStyleSheet("color: #F0A08A;")
            except Exception:
                pass

    def _refresh_audio_devices(self):
        self.combo_audio.clear()
        self.combo_audio.addItem("Default microphone", userData=None)
        try:
            for idx, name in AudioEngine.get_input_devices():
                self.combo_audio.addItem(f"[{idx}] {name}", userData=idx)
        except Exception as e:
            self._update_status("Mic scan failed", "red")

    def _test_speaker(self):
        """Two-tone probe through the REAL reply-audio path (24 kHz PCM16).

        If this sounds wrong (chipmunk/harsh), the fault is the speaker
        device/rate chain — not the model. If it sounds right, reply audio
        is proven end-to-end and garble comes from the live session/feedback.
        """
        try:
            self.lbl_speaker_proof.setText("Playing…")
        except Exception:
            pass
        try:
            import numpy as _np
            import sounddevice as _sd
            from src.audio_engine import AudioEngine as _AE
            sr = 24000
            dur = 1.2
            t = _np.arange(int(sr * dur)) / float(sr)
            tone = 0.4 * _np.sin(2 * _np.pi * 440.0 * t) + 0.25 * _np.sin(2 * _np.pi * 660.0 * t)
            raw = (tone * 32767).astype(_np.int16).tobytes()
            try:
                _di = _sd.default.device[1]
                _dev = _sd.query_devices(_di)
                _devname = str(_dev.get("name", _di))[:60]
            except Exception:
                _devname = "default output"
            eng = getattr(self, "_speaker_test_eng", None)
            if eng is None:
                eng = _AE()
                self._speaker_test_eng = eng
            ok = eng.start_playback_stream()
            if not ok:
                raise RuntimeError("output stream would not start")
            eng.play_audio_chunk(raw)
            msg = f"Played 440+660 Hz test tone on {_devname} @24 kHz — a clear two-tone beep means wiring is correct."
        except Exception as e:
            msg = f"Speaker test failed: {str(e)[:120]}"
        try:
            self.lbl_speaker_proof.setText(msg)
        except Exception:
            pass

    def _update_status(self, text: str, color: str):
        self.lbl_api_status.setText(text)
        styles = {
            "green": "background-color: #0E2A1D; color: #7EE2A8; border: 1px solid #1E5B3A; border-radius: 8px; padding: 4px 10px; font-size: 11px; font-weight: 500;",
            "orange": "background-color: #2A1F0E; color: #FFB84D; border: 1px solid #6B4A1E; border-radius: 8px; padding: 4px 10px; font-size: 11px; font-weight: 500;",
            "red": "background-color: #2A1414; color: #F0A08A; border: 1px solid #55E46D4C; border-radius: 8px; padding: 4px 10px; font-size: 11px; font-weight: 500;",
            "muted": "background-color: #1FC7D3EA; color: #C7D3EA; border: 1px solid #1FBAD7F7; border-radius: 8px; padding: 4px 10px; font-size: 11px; font-weight: 500;",
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
        # Format hint only — new key formats vary (AIza classic, plus newer
        # 2026 shapes). Validity is proven by the live probe below, never by
        # prefix. OAuth-style tokens (AQ.Ab…/ya29…) expire in ~1h and will
        # fail with 401 — the probe will say so clearly.
        if not k.startswith("AIza"):
            self.lbl_api_status.setToolTip("Unusual prefix — testing anyway. Classic keys start with AIza; get one at AI Studio if this fails.")
        self._update_status("Testing...", "orange")
        self.repaint()
        from PySide6.QtWidgets import QApplication as QA
        QA.processEvents()
        # Probe current refine models (never retired IDs) + generic fallback.
        try:
            test_models = [m for m in config_vault.get_refine_models() if m] + ["gemini-flash-latest"]
        except Exception:
            test_models = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-flash-latest"]
        try:
            from src.gemini_client import _dictation_sdk_status as _sdk_probe
            _smart_ok, _vocab_ok, _interim_ok = _sdk_probe()
            _sdk_note = "SDK SMART+vocab+interim OK" if (_smart_ok and _vocab_ok and _interim_ok) else (
                "SDK legacy: VERBATIM-only, no interim — pip install -U \"google-genai>=2.22\" for SMART")
        except Exception:
            _sdk_note = "SDK transcription status unknown"
        last_err = None
        for model in test_models:
            try:
                client = genai.Client(api_key=k)
                resp = client.models.generate_content(model=model, contents="Ping - reply with 'pong'")
                if resp and getattr(resp, "text", None):
                    self._update_status("Valid", "green")
                    self.lbl_api_status.setToolTip(f"{resp.text[:80]} | {_sdk_note}")
                    return
                elif resp:
                    self._update_status("Connected", "green")
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
            self._update_status("Service unavailable", "red")
        else:
            self._update_status(f"Error", "red")
            self.lbl_api_status.setToolTip(err[:400])

    def _add_backup(self):
        k = self.txt_new_backup.text().strip()
        if not k:
            return
        if len(k) < 20 or len(k) > 256:
            QMessageBox.warning(self, "Invalid key", "Key length looks wrong (expected 20-256 chars).")
            return
        if not k.startswith("AIza"):
            ret = QMessageBox.question(self, "Unusual key", "Key does not start with AIza (new formats vary). Add anyway? It will be validated on Test/connect.",
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
            self.slider_temp.setValue(int(float(cfg.get("temperature", 0.2)) * 100))
        except Exception:
            self.slider_temp.setValue(20)
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
        # Engine pickers removed — the AI Engine is automatic and
        # internal model values are never shown or edited here.
        # Verification mode + max sessions (redesign defaults)
        try:
            mode = config_vault.get_verification_mode()
            if mode == "auto_send":
                self.radio_auto_send.setChecked(True)
            else:
                self.radio_verification_active.setChecked(True)
        except Exception:
            pass
        # Agent reasoning depth + screen detail
        try:
            _lv = config_vault.get_live_thinking_level()
            {"LOW": self.radio_think_low, "MEDIUM": self.radio_think_medium, "HIGH": self.radio_think_high}.get(_lv, self.radio_think_medium).setChecked(True)
        except Exception:
            pass
        try:
            _sd = config_vault.get_screen_detail()
            for i in range(self.combo_screen_detail.count()):
                if self.combo_screen_detail.itemData(i) == _sd:
                    self.combo_screen_detail.setCurrentIndex(i)
                    break
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
            # Fallback: if old plain-text item (pre-mask builds), migrate if valid length
            try:
                txt = self.list_backups.item(i).text().strip()
                if len(txt) >= 20 and len(txt) <= 256 and "…" not in txt and "***" not in txt:
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
            # Engine model values stay internal — nothing to save from the UI.
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
            # Agent reasoning depth (user-selectable) + transcription lock.
            # Any radio choice counts as an explicit user decision that
            # survives restarts (see config upgrade rule).
            try:
                if hasattr(self, "radio_think_high") and self.radio_think_high.isChecked():
                    config_vault.config["live_thinking_level"] = "HIGH"
                elif hasattr(self, "radio_think_low") and self.radio_think_low.isChecked():
                    config_vault.config["live_thinking_level"] = "LOW"
                else:
                    config_vault.config["live_thinking_level"] = "MEDIUM"
                config_vault.config["_thinking_explicit"] = True
            except Exception:
                config_vault.config["live_thinking_level"] = "MEDIUM"
            config_vault.config["live_transcription_mode"] = "SMART"
            try:
                _sd = str(self.combo_screen_detail.currentData() or "MEDIUM").upper()
                config_vault.config["screen_detail"] = _sd if _sd in ("MEDIUM", "HIGH") else "MEDIUM"
            except Exception:
                config_vault.config["screen_detail"] = "MEDIUM"
            config_vault.set_startup(self.chk_startup.isChecked())
            config_vault.save_config()
            try:
                self.lbl_think.setText(f"Thinking {config_vault.get_live_thinking_level()} · Transcription SMART")
            except Exception:
                pass
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
            def _apply():
                try:
                    enable_rounded_corners(self)
                except Exception:
                    pass
                try:
                    self.update()
                except Exception:
                    pass
            QTimer.singleShot(0, _apply)
            QTimer.singleShot(80, _apply)
        except Exception:
            try:
                enable_rounded_corners(self)
            except Exception:
                pass
