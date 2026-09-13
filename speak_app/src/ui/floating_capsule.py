import time
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QProgressBar, QToolTip, QFrame, QTextEdit, QSizeGrip, QSizePolicy,
    QApplication
)
from PySide6.QtCore import Qt, QTimer, QPoint, Signal, QRectF, QSize
from PySide6.QtGui import (
    QPainter, QColor, QBrush, QPen, QCursor, QFontMetrics, QLinearGradient, QFont
)
from src.ui.icons import icon as lucide_icon
from src.ui.window_effects import enable_rounded_corners

# Authkit — Frosted glass cathedral at midnight
# Void Violet is the SOLE chromatic CTA (Save/Continue). Waves/status stay monochrome.
ACCENT_VIOLET = "#663AF3"
ACCENT_VIOLET_HOVER = "#7550F5"
MUTED = "#9DA7BA"
MUTED_LIGHT = "#C7D3EA"
FROST_GLOW = "#D1E4FA"
ICE_HIGHLIGHT = "#D8ECF8"
BLUEPRINT_BLUE = "#B6D9FC"
BORDER_SUBTLE = "#1FBAD7F7"
SURFACE = "#0B1023"
SURFACE_ALT = "#05060F"


class SoundWavePillWidget(QWidget):
    """Minimal wave — 5 bars, Skywash frost when Gemini, grey-white for mic.
    Authkit: no violet outside CTA — Gemini uses Ice Highlight gradient."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(52, 18)
        self.setMaximumHeight(22)
        self.setFixedWidth(58)
        self._target_amps = [0.14] * 5
        self._current_amps = [0.14] * 5
        self._is_gemini_active = False
        self._timer = QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._animate)
        self._timer.start()

    def set_mic_rms(self, norm_rms: float):
        self._is_gemini_active = False
        spread = [0.7, 1.0, 1.35, 0.9, 0.6]
        for i in range(5):
            self._target_amps[i] = max(0.12, min(1.0, norm_rms * spread[i]))

    def set_gemini_rms(self, norm_rms: float):
        self._is_gemini_active = True
        spread = [0.8, 1.15, 1.45, 1.05, 0.7]
        for i in range(5):
            self._target_amps[i] = max(0.14, min(1.0, norm_rms * spread[i]))

    def _animate(self):
        factor = 0.26
        changed = False
        for i in range(5):
            diff = self._target_amps[i] - self._current_amps[i]
            if abs(diff) > 0.001:
                self._current_amps[i] += diff * factor
                changed = True
        if not changed and max(self._current_amps) < 0.16:
            t = time.time() * 1.9
            for i in range(5):
                self._current_amps[i] = 0.13 + 0.018 * (0.5 + 0.5 * __import__('math').sin(t + i))
            self.update()
        elif changed:
            self.update()
        for i in range(5):
            self._target_amps[i] = max(0.11, self._target_amps[i] * 0.985)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        bar_w = 3.0
        spacing = 3.2
        total_w = 5 * bar_w + 4 * spacing
        start_x = (w - total_w) / 2
        # Authkit: Skywash gradient for Gemini, frost/moon for mic (no violet)
        if self._is_gemini_active:
            c1, c2 = QColor("#D8ECF8"), QColor("#98C0EF")
        else:
            # mic — soft frost / moon mist
            c1, c2 = QColor("#D1E4FA"), QColor("#9DA7BA")
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, c1)
        grad.setColorAt(1.0, c2)
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        for i in range(5):
            x = start_x + i * (bar_w + spacing)
            bar_h = max(3.0, self._current_amps[i] * (h - 3))
            y = (h - bar_h) / 2
            painter.drawRoundedRect(QRectF(x, y, bar_w, bar_h), 1.5, 1.5)


class HoverTokenBar(QProgressBar):
    """Authkit 3px token bar — semantic green/amber/red kept (functional), track midnight."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(3)
        self.setTextVisible(False)
        self.setRange(0, 100)
        self.setValue(0)
        self._tokens = 0
        self._max_tokens = 128000
        self._start_time = time.time()
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style(0)

    def set_tokens(self, current: int, max_tok: int):
        self._tokens = current
        self._max_tokens = max(1, max_tok)
        pct = int(min(100, (self._tokens / self._max_tokens) * 100))
        self.setValue(pct)
        self._apply_style(pct)

    def reset(self):
        self._tokens = 0
        self._start_time = time.time()
        self.setValue(0)
        self._apply_style(0)

    def _apply_style(self, pct: int):
        # Apple muted semantics
        if pct <= 60:
            col = "#30D158"  # Apple green
        elif pct <= 85:
            col = "#FF9F0A"  # Apple orange muted
        else:
            col = "#FF453A"  # Apple red
        self.setStyleSheet(f"""
            QProgressBar {{
                background-color: #0F1428;
                border: 1px solid #0FBAD7F7;
                border-radius: 1.5px;
            }}
            QProgressBar::chunk {{
                background-color: {col};
                border-radius: 1px;
            }}
        """)

    def enterEvent(self, event):
        elapsed = int(time.time() - self._start_time)
        m, s = divmod(elapsed, 60)
        pct = (self._tokens / self._max_tokens) * 100 if self._max_tokens else 0
        tip = (
            f"Context  {self._tokens:,} / {self._max_tokens:,}  ({pct:.1f}%)\n"
            f"Time {m:02d}:{s:02d}  \u00b7  Reset Ctrl+Win"
        )
        QToolTip.showText(QCursor.pos(), tip, self)
        super().enterEvent(event)


class CapsuleIconButton(QPushButton):
    """Minimal icon-only or icon+short label — Lucide, 28px pill."""

    def __init__(self, icon_name: str, label: str, tooltip: str, accent: bool = False, danger: bool = False, parent=None):
        super().__init__(parent)
        self._accent = accent
        self._danger = danger
        # Lucide icon — Authkit monochrome, violet only for primary CTA
        col = "#F0A08A" if danger else ("#FFFFFF" if accent else "#C7D3EA")
        self.setIcon(lucide_icon(icon_name, size=14, color=col))
        self.setIconSize(QSize(14, 14))
        # Short label to keep minimal but clear — single word
        self.setText(label)
        self.setToolTip(tooltip)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(32)
        self.setMinimumWidth(72 if label else 36)
        # Larger hit target for touch / high-DPI friendliness
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setStyleSheet(self._style())

    def _style(self) -> str:
        if self._danger:
            return """
                QPushButton {
                    background-color: #14E46D4C;
                    color: #F0A08A;
                    border: 1px solid #33E46D4C;
                    border-radius: 14px;
                    font-size: 11px;
                    font-weight: 500;
                    padding: 4px 10px;
                }
                QPushButton:hover {
                    background-color: #22E46D4C;
                    color: #FFFFFF;
                    border: 1px solid #55E46D4C;
                }
                QPushButton:pressed { background-color: #33E46D4C; }
            """
        if self._accent:
            return """
                QPushButton {
                    background-color: #663AF3;
                    color: #FFFFFF;
                    border: 1px solid #7A52FF;
                    border-radius: 14px;
                    font-size: 11px;
                    font-weight: 600;
                    padding: 4px 11px;
                }
                QPushButton:hover { background-color: #7550F5; border-color: #8A68FF; }
                QPushButton:pressed { background-color: #552FD1; }
            """
        return """
            QPushButton {
                background-color: #14BAD6F7;
                color: #D1E4FA;
                border: 1px solid #1FBAD7F7;
                border-radius: 14px;
                font-size: 11px;
                font-weight: 500;
                padding: 4px 10px;
            }
            QPushButton:hover {
                background-color: #1FBAD6F7;
                color: #FFFFFF;
                border: 1px solid #33BAD7F7;
            }
            QPushButton:pressed { background-color: #0ABAD6F7; }
        """


class TitleBarButton(QPushButton):
    """Small 28x28 close-only chrome for the frameless capsule.
    Authkit: small windows keep close only (no min/max).
    kind is kept for API compat but only 'close' is used.
    """

    def __init__(self, kind: str = "close", parent=None):
        super().__init__(parent)
        self._kind = "close"
        self.setFixedSize(28, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._icon_name = "x"
        self._icon_color = "#C7D3EA"
        self.setIcon(lucide_icon(self._icon_name, size=13, color=self._icon_color))
        self.setIconSize(QSize(13, 13))
        self.setToolTip("Close \u2014 stop session and hide to tray")
        self.setAccessibleName("Close \u2014 stop session and hide to tray")
        self.setStyleSheet(self._style())

    def set_maximized_state(self, maximized: bool):
        # Close-only: no maximize icon to swap (kept as no-op for compat).
        return

    def _style(self) -> str:
        return """
            QPushButton {
                background: transparent;
                border: 1px solid transparent;
                border-radius: 8px;
                padding: 0px;
            }
            QPushButton:hover {
                background: #22E46D4C;
                border: 1px solid #55E46D4C;
            }
            QPushButton:pressed { background: #33E46D4C; }
        """


class FloatingCapsuleWidget(QWidget):
    """Apple/Stripe minimal capsule — sizable, rounded corners, no emoji, Lucide only."""

    sig_toggle_screen = Signal()
    sig_open_settings = Signal()
    sig_open_tutorial = Signal()
    sig_close_session = Signal()
    sig_refine = Signal(str)
    sig_clear_transcript = Signal()
    sig_copy_transcript = Signal()
    # Emitted after expand/collapse/resize so main.py can keep the
    # capsule fully inside availableGeometry (never under taskbar).
    sig_geometry_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
        # Roomy enough that Ctrl+Space status never elides aggressively.
        # Wider default prevents the "text cut off" report.
        self.setMinimumWidth(680)
        self.setMinimumHeight(112)
        self.setMaximumWidth(860)
        self.resize(720, 118)
        self._drag_pos = QPoint()
        self._drag_active = False
        self._expanded = False
        self._resizing = False
        self._resize_start = QPoint()
        self._resize_size = QSize()
        # Close-only: no maximize state (kept attrs for compat, always False/None)
        self._is_maximized = False
        self._normal_geo = None
        self._last_status = ("Ready", "idle")
        self._init_ui()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(5)

        # ---- Custom title bar: drag handle + close ONLY ----
        # Authkit: small windows keep close only. Frameless Tool has no native
        # chrome, so we provide a single 28px close button (accessible, tooltipped).
        # Drag is titlebar-only (see eventFilter) so buttons/inputs never start a move.
        self.titlebar = QWidget(self)
        self.titlebar.setObjectName("CapsuleTitleBar")
        self.titlebar.setFixedHeight(30)
        self.titlebar.setCursor(Qt.CursorShape.OpenHandCursor)
        tb = QHBoxLayout(self.titlebar)
        tb.setContentsMargins(8, 2, 4, 2)
        tb.setSpacing(6)
        self.title_dot = QLabel("\u25CF", self.titlebar)
        self.title_dot.setStyleSheet("color: #B6D9FC; font-size: 8px; background: transparent;")
        self.title_dot.setFixedWidth(10)
        self.title_dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tb.addWidget(self.title_dot)
        self.title_label = QLabel("SPEAK  \u00b7  Ctrl+Space to dictate", self.titlebar)
        self.title_label.setStyleSheet("color: #9DA7BA; font-size: 11px; font-weight: 500; background: transparent;")
        self.title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        tb.addWidget(self.title_label, 1)
        self.btn_x = TitleBarButton("close", self.titlebar)
        self.btn_x.clicked.connect(self._on_chrome_close)
        tb.addWidget(self.btn_x)
        root.addWidget(self.titlebar)
        # Titlebar drag via event filter (children labels also draggable, button excluded)
        try:
            self.titlebar.installEventFilter(self)
            self.title_label.installEventFilter(self)
            self.title_dot.installEventFilter(self)
        except Exception:
            pass

        # Pill container - tighter to avoid horizontal cutoff
        self.pill = QWidget(self)
        self.pill.setObjectName("CapsulePill")
        lay = QHBoxLayout(self.pill)
        lay.setContentsMargins(12, 6, 10, 6)
        lay.setSpacing(10)

        self.status_dot = QLabel("\u25CF", self.pill)
        self.status_dot.setStyleSheet("color: #9DA7BA; font-size: 9px; background: transparent;")
        self.status_dot.setFixedWidth(10)
        self.status_dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.status_dot)

        self.lbl_status = QLabel("Ready", self.pill)
        self.lbl_status.setStyleSheet("color: #D8ECF8; font-weight: 600; font-size: 12px; letter-spacing: 0.1px; background: transparent;")
        # FIX: never hard-clip — expanding with generous max so long
        # "Dictating (model)" strings elide gracefully instead of cutting.
        self.lbl_status.setMinimumWidth(160)
        self.lbl_status.setMaximumWidth(420)
        self.lbl_status.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.lbl_status.setWordWrap(False)
        lay.addWidget(self.lbl_status, 1)

        self.wave_visualizer = SoundWavePillWidget(self.pill)
        lay.addWidget(self.wave_visualizer)

        self.lbl_hint = QLabel("Listening", self.pill)
        self.lbl_hint.setStyleSheet("color: #9DA7BA; font-size: 10px; background: transparent;")
        self.lbl_hint.setFixedWidth(72)
        self.lbl_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.lbl_hint)

        sep = QFrame(self.pill)
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("background: #1FBAD7F7; border: none;")
        sep.setFixedWidth(1)
        sep.setFixedHeight(20)
        lay.addWidget(sep)

        self.btn_settings = CapsuleIconButton("settings", "Settings", "Open settings (capsule stays)", parent=self.pill)
        self.btn_settings.clicked.connect(self.sig_open_settings.emit)
        lay.addWidget(self.btn_settings)

        self.btn_guide = CapsuleIconButton("book-open", "Guide", "Open shortcut guide", parent=self.pill)
        self.btn_guide.clicked.connect(self.sig_open_tutorial.emit)
        lay.addWidget(self.btn_guide)

        self.btn_close = CapsuleIconButton("x", "Hide", "Stop session and hide to tray", danger=True, parent=self.pill)
        self.btn_close.clicked.connect(self._on_close_clicked)
        lay.addWidget(self.btn_close)

        root.addWidget(self.pill)

        self.token_bar = HoverTokenBar(self)
        root.addWidget(self.token_bar)

        # Inline controls row — compact, transcript toggle next to arrow+screen to save space
        ctrl = QHBoxLayout()
        ctrl.setContentsMargins(4, 0, 4, 0)
        ctrl.setSpacing(6)
        # Group: Transcript arrow + Screen toggle side-by-side to save vertical space
        self.btn_transcript_toggle = QPushButton("Transcript", self)
        self.btn_transcript_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_transcript_toggle.setIcon(lucide_icon("chevron-down", size=13, color="#C7D3EA"))
        self.btn_transcript_toggle.setIconSize(QSize(13,13))
        self.btn_transcript_toggle.setFixedHeight(28)
        self.btn_transcript_toggle.setMinimumWidth(110)
        self.btn_transcript_toggle.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_transcript_toggle.setStyleSheet("""
            QPushButton {
                background: #14BAD6F7;
                color: #D1E4FA;
                border: 1px solid #1FBAD7F7;
                border-radius: 8px;
                font-size: 11px;
                font-weight: 500;
                padding: 0 10px;
                text-align: left;
            }
            QPushButton:hover { background: #1FBAD6F7; color: #FFFFFF; }
        """)
        self.btn_transcript_toggle.setToolTip("Show / hide transcript and refine (no shortcut needed)")
        self.btn_transcript_toggle.setAccessibleName("Toggle transcript panel")
        self.btn_transcript_toggle.clicked.connect(self.toggle_sheet)
        ctrl.addWidget(self.btn_transcript_toggle)

        # Screen toggle (live-screen) — Authkit frost, blueprint icon when ON
        self.btn_screen = QPushButton(self)
        self.btn_screen.setIcon(lucide_icon("monitor", size=13, color="#9DA7BA"))
        self.btn_screen.setIconSize(QSize(13,13))
        self.btn_screen.setFixedSize(32, 28)
        self.btn_screen.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_screen.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_screen.setToolTip("Toggle live screen share for companion (voice-only when off)")
        self.btn_screen.setAccessibleName("Toggle live screen share")
        self.btn_screen.setCheckable(True)
        self.btn_screen.setStyleSheet("""
            QPushButton { background: #14BAD6F7; border: 1px solid #1FBAD7F7; border-radius: 8px; }
            QPushButton:hover { background: #1FBAD6F7; }
            QPushButton:checked { background: #1FBAD6F7; border: 1px solid #33BAD7F7; }
        """)
        self.btn_screen.toggled.connect(self._on_screen_toggled)
        ctrl.addWidget(self.btn_screen)

        self.lbl_interim_inline = QLabel("", self)
        self.lbl_interim_inline.setStyleSheet("color: #9DA7BA; font-size: 11px; background: transparent;")
        self.lbl_interim_inline.setVisible(False)
        self.lbl_interim_inline.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.lbl_interim_inline.setWordWrap(False)
        ctrl.addWidget(self.lbl_interim_inline, 1)

        ctrl.addStretch()

        root.addLayout(ctrl)

        # Sheet — Authkit glass card 16px (transcript panel)
        self.sheet = QFrame(self)
        self.sheet.setObjectName("GlassCard")
        self.sheet.setStyleSheet("QFrame#GlassCard { background-color: #0B1023; border: 1px solid #1FBAD7F7; border-radius: 16px; }")
        sl = QVBoxLayout(self.sheet)
        sl.setContentsMargins(10, 8, 10, 8)
        sl.setSpacing(6)

        head = QHBoxLayout()
        head.setSpacing(8)
        title = QLabel("Transcript", self.sheet)
        title.setStyleSheet("color: #D8ECF8; font-size: 12px; font-weight: 600; background: transparent;")
        head.addWidget(title)
        self.lbl_stats = QLabel("0 words", self.sheet)
        self.lbl_stats.setStyleSheet("color: #9DA7BA; font-size: 11px; background: transparent;")
        head.addWidget(self.lbl_stats)
        head.addStretch()
        self.btn_copy = QPushButton("Copy", self.sheet)
        self.btn_copy.setIcon(lucide_icon("copy", size=12, color="#D1E4FA"))
        self.btn_copy.setFixedHeight(30)
        self.btn_copy.setMinimumWidth(76)
        self.btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_copy.setToolTip("Copy transcript to clipboard")
        self.btn_copy.setStyleSheet("QPushButton { background: #14BAD6F7; color: #D1E4FA; border: 1px solid #1FBAD7F7; border-radius: 8px; padding: 0 10px; font-size: 11px; } QPushButton:hover { background: #1FBAD6F7; color: #FFFFFF; }")
        self.btn_copy.clicked.connect(self._on_copy)
        head.addWidget(self.btn_copy)
        self.btn_clear = QPushButton("Clear", self.sheet)
        self.btn_clear.setIcon(lucide_icon("trash-2", size=12, color="#9DA7BA"))
        self.btn_clear.setFixedHeight(30)
        self.btn_clear.setMinimumWidth(76)
        self.btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_clear.setToolTip("Clear transcript and typed history (Ctrl+Win also purges)")
        self.btn_clear.setStyleSheet("QPushButton { background: transparent; color: #9DA7BA; border: 1px solid #1FBAD7F7; border-radius: 8px; padding: 0 10px; font-size: 11px; } QPushButton:hover { background: #14BAD6F7; color: #D1E4FA; }")
        self.btn_clear.clicked.connect(self.sig_clear_transcript.emit)
        head.addWidget(self.btn_clear)
        sl.addLayout(head)

        self.txt_transcript = QTextEdit(self.sheet)
        self.txt_transcript.setReadOnly(True)
        self.txt_transcript.setPlaceholderText("Transcription appears here. Say refine, polish or elaborate.")
        # FIX: min/max instead of fixed so layout never half-clips on DPI scaling
        self.txt_transcript.setMinimumHeight(90)
        self.txt_transcript.setMaximumHeight(220)
        self.txt_transcript.setFixedHeight(110)
        self.txt_transcript.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.txt_transcript.setStyleSheet("QTextEdit { background: #05060F; border: 1px solid #1FBAD7F7; border-radius: 6px; padding: 8px; color: #D1E4FA; font-size: 12px; } QTextEdit:focus { border: 1px solid #663AF3; }")
        sl.addWidget(self.txt_transcript)

        refine = QHBoxLayout()
        refine.setSpacing(6)
        lb = QLabel("REFINE", self.sheet)
        lb.setObjectName("EyebrowLabel")
        lb.setStyleSheet("color: #C7D3EA; font-size: 10px; font-weight: 600; background: transparent;")
        refine.addWidget(lb)
        refine.addStretch()
        self._refine_layout = refine
        self._refine_buttons: list = []
        self._build_refine_buttons()
        sl.addLayout(refine)

        self.lbl_refine_hint = QLabel("Say refine / polish / elaborate or tap a button.", self.sheet)
        self.lbl_refine_hint.setStyleSheet("color: #9DA7BA; font-size: 11px; background: transparent;")
        self.lbl_refine_hint.setWordWrap(True)
        sl.addWidget(self.lbl_refine_hint)

        root.addWidget(self.sheet)
        self.sheet.setVisible(False)

        # Size grip for sizable behavior (bottom-right)
        grip_row = QHBoxLayout()
        grip_row.addStretch()
        self.size_grip = QSizeGrip(self)
        self.size_grip.setStyleSheet("QSizeGrip { width: 12px; height: 12px; background: transparent; }")
        # Make grip subtle — override paint
        grip_row.addWidget(self.size_grip)
        root.addLayout(grip_row)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Authkit glass plate: midnight fill + frost hairline + cool halo shadow
        # Outer halo (cool blue-grey, not neutral black)
        try:
            shadow_rect = QRectF(6, 8, self.width() - 12, self.height() - 12)
            painter.setBrush(QBrush(QColor(6, 8, 22, 110)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(shadow_rect, 16, 16)
        except Exception:
            pass
        # Subtle top frost highlight (lit-from-above glass)
        try:
            hi = QRectF(5, 4, self.width() - 10, self.height() // 2)
            grad = QLinearGradient(0, 4, 0, 4 + max(1, self.height() // 2))
            grad.setColorAt(0.0, QColor(216, 236, 248, 22))
            grad.setColorAt(1.0, QColor(216, 236, 248, 0))
            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(hi, 16, 16)
        except Exception:
            pass
        rect = QRectF(4, 4, self.width() - 8, self.height() - 8)
        painter.setBrush(QBrush(QColor("#0B1023")))
        painter.setPen(QPen(QColor(186, 215, 247, 31), 1))
        painter.drawRoundedRect(rect, 16, 16)

    def set_status(self, text: str, badge_type: str = "idle"):
        # FIX (cutoff): compute available width from the REAL pill layout
        # instead of a hardcoded 500px guess. Guarantees at least 180px
        # for status so Ctrl+Space messages are never half-clipped, and
        # full text is always in the tooltip.
        self._last_status = (text, badge_type)
        try:
            pill_w = self.pill.width() if self.pill.width() > 100 else self.width() - 12
            # Fixed chrome inside pill: dot + wave + hint + sep + 3 buttons + margins/spacing
            fixed = (
                10 + self.wave_visualizer.width() + self.lbl_hint.width() + 1
                + self.btn_settings.sizeHint().width()
                + self.btn_guide.sizeHint().width()
                + self.btn_close.sizeHint().width()
                + 12 + 10 + 10 * 6
            )
            avail = max(180, min(420, pill_w - fixed))
        except Exception:
            avail = 220
        try:
            metrics = QFontMetrics(self.lbl_status.font())
            elided = metrics.elidedText(text, Qt.TextElideMode.ElideRight, avail)
        except Exception:
            elided = text
        self.lbl_status.setText(elided)
        self.lbl_status.setToolTip(text)
        hint_map = {
            "active": ("Listening", "#B6D9FC"),
            "warn": ("Working", "#FF9F0A"),
            "error": ("Error", "#F0A08A"),
            "refining": ("Refining", "#30D158"),
            "idle": ("Ready", "#9DA7BA"),
        }
        hint, dot = hint_map.get(badge_type, ("Ready", "#9DA7BA"))
        # hint shows fixed short word to keep minimal
        self.lbl_hint.setText(hint)
        self.lbl_hint.setStyleSheet(f"color: {dot if badge_type!='idle' else '#9DA7BA'}; font-size: 10px; font-weight: 500; background: transparent;")
        self.status_dot.setStyleSheet(f"color: {dot}; font-size: 9px; background: transparent;")
        self.title_dot.setStyleSheet(f"color: {dot}; font-size: 8px; background: transparent;")
        self.update()

    def set_transcript(self, text: str):
        self.txt_transcript.setPlainText(text)
        cur = self.txt_transcript.textCursor()
        cur.movePosition(cur.MoveOperation.End)
        self.txt_transcript.setTextCursor(cur)
        words = len(text.strip().split()) if text.strip() else 0
        self.lbl_stats.setText(f"{words} words")
        # Auto expand sheet if there is content and not yet expanded — subtle
        self.update()

    def set_interim(self, text: str):
        if text and text.strip():
            t = text.strip().replace("\n", " ")
            # FIX: elide to actual label width instead of hard 38 chars,
            # so interim never pushes the pill wider / gets half-cut.
            try:
                w = max(160, self.lbl_interim_inline.width() or 240)
                metrics = QFontMetrics(self.lbl_interim_inline.font())
                t = metrics.elidedText(t, Qt.TextElideMode.ElideRight, w)
            except Exception:
                if len(t) > 60:
                    t = t[:60] + "…"
            self.lbl_interim_inline.setText(t)
            self.lbl_interim_inline.setToolTip(text.strip())
            self.lbl_interim_inline.setVisible(True)
        else:
            self.lbl_interim_inline.setVisible(False)
            self.lbl_interim_inline.setText("")
            self.lbl_interim_inline.setToolTip("")

    def _action_meta(self, action_id: str):
        """(label, tip, icon, is_primary) for built-ins + customs."""
        try:
            if action_id == "refine":
                return ("Refine", "Resolve corrections + cohesive", "sparkles", True)
            if action_id == "polish":
                return ("Polish", "Publication ready", "wand", False)
            if action_id in ("elaborate", "expand"):
                return ("Elaborate", "Add detail + fix corrections", "layers", False)
            try:
                from src.config import config_vault as _vault
                for c in _vault.get_custom_actions(enabled_only=False):
                    if c.get("id") == action_id:
                        return (str(c.get("name") or action_id)[:12], f"Custom: {c.get('trigger')}", "zap", False)
            except Exception:
                pass
        except Exception:
            pass
        return (str(action_id)[:12].title(), "Custom refine", "zap", False)

    def _build_refine_buttons(self):
        """Rebuild refine/polish/elaborate + custom buttons from Settings (max 6)."""
        try:
            for b in list(getattr(self, "_refine_buttons", []) or []):
                try:
                    self._refine_layout.removeWidget(b)
                    b.deleteLater()
                except Exception:
                    pass
            self._refine_buttons = []
            # Clear legacy attrs (keep btn_expand alias for compat)
            for legacy in ("btn_refine", "btn_polish", "btn_expand", "btn_elaborate"):
                try:
                    if hasattr(self, legacy):
                        delattr(self, legacy)
                except Exception:
                    pass
            try:
                from src.config import config_vault as _vault
                actions = _vault.get_all_refine_actions()
            except Exception:
                actions = [{"id": "refine", "name": "Refine"}, {"id": "polish", "name": "Polish"}, {"id": "elaborate", "name": "Elaborate"}]
            for item in (actions or [])[:6]:
                try:
                    aid = str(item.get("id", "refine"))
                    label, tip, ico, primary = self._action_meta(aid)
                    # Prefer configured display name for customs
                    try:
                        if item.get("name"):
                            label = str(item["name"])[:12]
                    except Exception:
                        pass
                    b = QPushButton(label, self.sheet)
                    b.setIcon(lucide_icon(ico, size=12, color="#FFFFFF" if primary else "#C7D3EA"))
                    b.setFixedHeight(32)
                    b.setMinimumWidth(84)
                    b.setCursor(Qt.CursorShape.PointingHandCursor)
                    b.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                    b.setToolTip(tip)
                    b.setAccessibleName(f"{label} transcript")
                    if primary:
                        b.setStyleSheet("QPushButton { background: #663AF3; color: #FFFFFF; border: 1px solid #7A52FF; border-radius: 14px; font-size: 11px; font-weight: 600; padding: 0 10px; } QPushButton:hover { background: #7550F5; } QPushButton:disabled { background: #1A2038; color: #9DA7BA; border: 1px solid #1FBAD7F7; }")
                    else:
                        b.setStyleSheet("QPushButton { background: #14BAD6F7; color: #D1E4FA; border: 1px solid #1FBAD7F7; border-radius: 14px; font-size: 11px; } QPushButton:hover { background: #1FBAD6F7; color: #FFFFFF; } QPushButton:disabled { background: #0A0D1D; color: #9DA7BA; }")
                    b.clicked.connect(lambda _, a=aid: self.sig_refine.emit(a))
                    self._refine_layout.addWidget(b)
                    self._refine_buttons.append(b)
                    setattr(self, f"btn_{aid}", b)
                    if aid == "elaborate":
                        setattr(self, "btn_expand", b)  # legacy alias
                except Exception:
                    continue
            self._refresh_refine_hint()
        except Exception:
            pass

    def _refresh_refine_hint(self):
        try:
            words: list[str] = []
            try:
                from src.config import config_vault as _vault
                trig = _vault.get_refine_triggers()
                for aid in ("refine", "polish", "elaborate"):
                    lst = trig.get(aid, [])
                    if lst:
                        words.append(str(lst[0]))
                for c in _vault.get_custom_actions(enabled_only=True):
                    if c.get("trigger"):
                        words.append(str(c["trigger"]))
            except Exception:
                words = ["refine", "polish", "elaborate"]
            words = [w for w in words if w][:6]
            txt = "Say " + " / ".join(words) + " or tap a button." if words else "Tap a button to rewrite the session."
            if hasattr(self, "lbl_refine_hint"):
                self.lbl_refine_hint.setText(txt)
        except Exception:
            pass

    def refresh_refine_actions(self):
        """Public slot: call after Settings save so new prompts/triggers appear immediately."""
        try:
            self._build_refine_buttons()
        except Exception:
            pass

    def set_refining(self, is_refining: bool, action: str = ""):
        for b in list(getattr(self, "_refine_buttons", []) or []):
            try:
                b.setEnabled(not is_refining)
            except Exception:
                pass
        for a in ("refine", "polish", "expand", "elaborate", "custom1", "custom2", "custom3"):
            try:
                b = getattr(self, f"btn_{a}", None)
                if b:
                    b.setEnabled(not is_refining)
            except Exception:
                pass
        if is_refining:
            try:
                from src.config import config_vault as _vault
                _disp = action
                for _item in _vault.get_all_refine_actions():
                    if _item.get("id") == action:
                        _disp = _item.get("name", action)
                        break
                if action in ("elaborate", "expand"):
                    _disp = "Elaborate"
            except Exception:
                _disp = action
            self.set_status(f"{str(_disp).title()}ing", "refining")
            self.btn_copy.setEnabled(False)
            self.btn_clear.setEnabled(False)
        else:
            self.btn_copy.setEnabled(True)
            self.btn_clear.setEnabled(True)

    def toggle_sheet(self):
        self._expanded = not self._expanded
        self.sheet.setVisible(self._expanded)
        # Keep label always "Transcript" — only icon flips, avoids duplicate "Hide" with capsule hide button
        ico_name = "chevron-up" if self._expanded else "chevron-down"
        self.btn_transcript_toggle.setIcon(lucide_icon(ico_name, size=12, color="#C7D3EA"))
        self.btn_transcript_toggle.setText("Transcript")
        # FIX (vertical cutoff): grow/shrink then lift the window so the
        # sheet never extends underneath the taskbar. adjustSize() alone
        # grows downward — we compensate by moving up by the delta.
        try:
            old_h = self.height()
            self.adjustSize()
            self.updateGeometry()
            new_h = self.sizeHint().height() or self.height()
            if new_h != old_h:
                self._clamp_inside_screen()
        except Exception:
            try:
                self.adjustSize()
                self.updateGeometry()
            except Exception:
                pass
        QTimer.singleShot(30, self.update)
        QTimer.singleShot(40, self._refresh_status_elision)
        try:
            self.sig_geometry_changed.emit()
        except Exception:
            pass

    def _refresh_status_elision(self):
        try:
            text, badge = self._last_status
            self.set_status(text, badge)
        except Exception:
            pass

    def _clamp_inside_screen(self):
        """Keep the whole capsule inside availableGeometry (above taskbar)."""
        try:
            app = QApplication.instance()
            if not app:
                return
            screen = app.screenAt(self.geometry().center()) or app.primaryScreen()
            if not screen:
                return
            avail = screen.availableGeometry()
            g = self.geometry()
            # If bottom would go under taskbar, shift up
            if g.bottom() > avail.bottom():
                self.move(g.x(), max(avail.y(), avail.bottom() - g.height() - 6))
            # If expanded made us taller than screen, cap height
            if g.height() > avail.height() - 12:
                self.resize(g.width(), avail.height() - 12)
            # Horizontal clamp
            g2 = self.geometry()
            if g2.right() > avail.right():
                self.move(max(avail.x(), avail.right() - g2.width() - 6), g2.y())
            if g2.x() < avail.x():
                self.move(avail.x() + 6, self.y())
        except Exception:
            pass

    # ---- Window chrome: close-only (no min/max on small windows) ----
    # Compat stubs: old callers expect these; they are intentional no-ops now.
    def show_minimized(self):
        # Close-only capsule: minimize removed — hide to tray instead is via close.
        return

    def toggle_maximize(self):
        # Close-only capsule: maximize removed — no-op (double-click does nothing).
        return

    def _on_chrome_close(self):
        # Same semantics as Hide: stop session, hide to tray (app keeps running).
        try:
            self.sig_close_session.emit()
        except Exception:
            pass
        try:
            self.hide()
        except Exception:
            pass

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Re-elide status on every resize so text never looks half-cut.
        try:
            self._refresh_status_elision()
        except Exception:
            pass

    def set_screen_enabled(self, enabled: bool):
        # Sync live-screen toggle without emitting (Authkit frost/blueprint, no violet)
        self.btn_screen.blockSignals(True)
        self.btn_screen.setChecked(enabled)
        self.btn_screen.setIcon(lucide_icon("monitor" if enabled else "eye-off", size=12, color="#D8ECF8" if enabled else "#9DA7BA"))
        self.btn_screen.setToolTip("Live screen share: ON" if enabled else "Live screen share: OFF — voice only")
        self.btn_screen.blockSignals(False)

    def _on_screen_toggled(self, checked: bool):
        self.btn_screen.setIcon(lucide_icon("monitor" if checked else "eye-off", size=12, color="#D8ECF8" if checked else "#9DA7BA"))
        self.btn_screen.setToolTip("Live screen share: ON" if checked else "Live screen share: OFF — voice only")
        self.sig_toggle_screen.emit()

    def _on_copy(self):
        text = self.txt_transcript.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.sig_copy_transcript.emit()
            orig = self.btn_copy.text()
            self.btn_copy.setText("Copied")
            self.btn_copy.setIcon(lucide_icon("check", size=12, color="#30D158"))
            QTimer.singleShot(1300, lambda: (self.btn_copy.setText(orig), self.btn_copy.setIcon(lucide_icon("copy", size=12, color="#D1E4FA"))))

    def _on_close_clicked(self):
        self._on_chrome_close()

    # ---- Drag: titlebar-only (close-only capsule) + edge resize ----
    # Production rule: NEVER start a drag from buttons, inputs, sheet, or pill.
    # Titlebar drag is handled via eventFilter (covers titlebar + its labels).
    # mousePress/Move here only handles the bottom-right resize zone.
    def _in_resize_zone(self, pos) -> bool:
        try:
            return pos.x() >= self.width() - 16 and pos.y() >= self.height() - 16
        except Exception:
            return False

    def _in_titlebar(self, pos) -> bool:
        try:
            return self.titlebar.geometry().contains(pos.toPoint() if hasattr(pos, "toPoint") else pos)
        except Exception:
            return False

    def eventFilter(self, watched, event):
        # Titlebar drag: press on titlebar/labels starts move; button press does not.
        try:
            from PySide6.QtCore import QEvent
            if watched in (getattr(self, "titlebar", None), getattr(self, "title_label", None), getattr(self, "title_dot", None)):
                et = event.type()
                if et == QEvent.Type.MouseButtonPress:
                    if event.button() == Qt.MouseButton.LeftButton:
                        self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                        self._drag_active = True
                        try:
                            self.titlebar.setCursor(Qt.CursorShape.ClosedHandCursor)
                        except Exception:
                            pass
                        event.accept()
                        return True
                elif et == QEvent.Type.MouseMove:
                    if self._drag_active and (event.buttons() & Qt.MouseButton.LeftButton):
                        self.move(event.globalPosition().toPoint() - self._drag_pos)
                        event.accept()
                        return True
                elif et == QEvent.Type.MouseButtonRelease:
                    if self._drag_active:
                        self._drag_active = False
                        try:
                            self.titlebar.setCursor(Qt.CursorShape.OpenHandCursor)
                        except Exception:
                            pass
                        event.accept()
                        return True
        except Exception:
            pass
        return super().eventFilter(watched, event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Resize zone only — never drag from body (prevents stealing input clicks).
            if self._in_resize_zone(event.position()):
                self._resizing = True
                self._resize_start = event.globalPosition().toPoint()
                self._resize_size = self.size()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        # Close-only: double-click titlebar does nothing (no maximize).
        try:
            if self._in_titlebar(event.position()):
                event.accept()
                return
        except Exception:
            pass
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event):
        if self._resizing and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self._resize_start
            new_w = max(self.minimumWidth(), min(self.maximumWidth(), self._resize_size.width() + delta.x()))
            new_h = max(self.minimumHeight(), self._resize_size.height() + delta.y())
            # Cap max height to avoid huge sheet
            new_h = min(new_h, 620)
            self.resize(int(new_w), int(new_h))
            event.accept()
            return
        # Cursor feedback for resize zone only
        if self._in_resize_zone(event.position()):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_active = False
        self._resizing = False
        try:
            self.titlebar.setCursor(Qt.CursorShape.OpenHandCursor)
        except Exception:
            pass
        super().mouseReleaseEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        # Windows 11 rounded corners + remove 1px border artifact
        try:
            from PySide6.QtCore import QTimer as _QT
            def _apply():
                try:
                    enable_rounded_corners(self)
                    try:
                        from src.ui.window_effects import disable_window_border
                        disable_window_border(self)
                    except Exception:
                        pass
                except Exception:
                    pass
                self.update()
            _QT.singleShot(0, _apply)
            _QT.singleShot(80, _apply)
        except Exception:
            try:
                enable_rounded_corners(self)
            except Exception:
                pass
        self.update()
