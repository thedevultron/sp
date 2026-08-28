import time
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QProgressBar, QToolTip, QFrame
)
from PySide6.QtCore import Qt, QTimer, QPoint, Signal, QRectF
from PySide6.QtGui import (
    QPainter, QColor, QBrush, QPen, QCursor, QFontMetrics, QLinearGradient
)


class SoundWavePillWidget(QWidget):
    """Modern dynamic sound wave visualization widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(52, 20)
        self.setMaximumHeight(24)
        self._target_amps = [0.15] * 5
        self._current_amps = [0.15] * 5
        self._is_gemini_active = False
        self._timer = QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._animate)
        self._timer.start()

    def set_mic_rms(self, norm_rms: float):
        self._is_gemini_active = False
        spread = [0.7, 1.0, 1.4, 0.9, 0.6]
        for i in range(5):
            self._target_amps[i] = max(0.12, min(1.0, norm_rms * spread[i]))

    def set_gemini_rms(self, norm_rms: float):
        self._is_gemini_active = True
        spread = [0.8, 1.2, 1.5, 1.1, 0.7]
        for i in range(5):
            self._target_amps[i] = max(0.15, min(1.0, norm_rms * spread[i]))

    def _animate(self):
        factor = 0.25
        changed = False
        for i in range(5):
            diff = self._target_amps[i] - self._current_amps[i]
            if abs(diff) > 0.001:
                self._current_amps[i] += diff * factor
                changed = True
        if not changed and max(self._current_amps) < 0.16:
            t = time.time() * 2.0
            for i in range(5):
                self._current_amps[i] = 0.13 + 0.02 * (0.5 + 0.5 * __import__('math').sin(t + i))
            self.update()
        elif changed:
            self.update()
        for i in range(5):
            self._target_amps[i] = max(0.12, self._target_amps[i] * 0.985)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        bar_w = 3.0
        spacing = 3.5
        total_w = 5 * bar_w + 4 * spacing
        start_x = (w - total_w) / 2
        grad = QLinearGradient(0, 0, 0, h)
        if self._is_gemini_active:
            grad.setColorAt(0.0, QColor("#FFA07A"))
            grad.setColorAt(1.0, QColor("#E05A47"))
        else:
            grad.setColorAt(0.0, QColor("#E2886B"))
            grad.setColorAt(1.0, QColor("#C05638"))
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        for i in range(5):
            x = start_x + i * (bar_w + spacing)
            bar_h = max(3.0, self._current_amps[i] * (h - 4))
            y = (h - bar_h) / 2
            painter.drawRoundedRect(QRectF(x, y, bar_w, bar_h), 1.5, 1.5)


class HoverTokenBar(QProgressBar):
    """Context percentage bar with hover telemetry."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(4)
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
        col = "#34C759" if pct <= 60 else ("#F59E0B" if pct <= 85 else "#EF4444")
        self.setStyleSheet(f"""
            QProgressBar {{
                background-color: rgba(255, 255, 255, 0.08);
                border: none;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {col};
                border-radius: 2px;
            }}
        """)

    def enterEvent(self, event):
        elapsed = int(time.time() - self._start_time)
        m, s = divmod(elapsed, 60)
        pct = (self._tokens / self._max_tokens) * 100 if self._max_tokens else 0
        tip = (
            f"🧠 Context Token Usage\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"• Used: {self._tokens:,} / {self._max_tokens:,} ({pct:.1f}%)\n"
            f"• Duration: {m:02d}:{s:02d}\n"
            f"• Reset: Press Ctrl + Win"
        )
        QToolTip.showText(QCursor.pos(), tip, self)
        super().enterEvent(event)


class LabeledCapsuleButton(QPushButton):
    """Obvious labeled pill button with icon + text for friendliness."""

    def __init__(self, icon_text: str, label: str, tooltip: str, is_close: bool = False, parent=None):
        super().__init__(parent)
        # Example: "✏️" + " Draw"
        self.setText(f"{icon_text}  {label}")
        self.setToolTip(tooltip)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        # Auto width but min for consistency
        self.setMinimumHeight(28)
        self.setMinimumWidth(72)
        # Use sizeHint + padding instead of fixed
        self.setStyleSheet(self._style(is_close))

    def _style(self, is_close: bool) -> str:
        if is_close:
            return """
                QPushButton {
                    background-color: rgba(239, 68, 68, 0.15);
                    color: #F87171;
                    border: 1px solid rgba(239, 68, 68, 0.3);
                    border-radius: 14px;
                    font-size: 11px;
                    font-weight: 600;
                    padding: 4px 10px;
                }
                QPushButton:hover {
                    background-color: rgba(239, 68, 68, 0.28);
                    color: #FFFFFF;
                    border: 1px solid rgba(239, 68, 68, 0.5);
                }
                QPushButton:pressed {
                    background-color: rgba(239, 68, 68, 0.35);
                }
            """
        else:
            return """
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.07);
                    color: #E2E8F0;
                    border: 1px solid rgba(255, 255, 255, 0.12);
                    border-radius: 14px;
                    font-size: 11px;
                    font-weight: 500;
                    padding: 4px 10px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.16);
                    color: #FFFFFF;
                    border: 1px solid rgba(255, 255, 255, 0.22);
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 0.04);
                }
            """


class FloatingCapsuleWidget(QWidget):
    """User-friendly floating pill: obvious icons + labels, drag anywhere, hidden until hotkey."""

    sig_toggle_screen = Signal()
    sig_toggle_canvas = Signal()
    sig_open_settings = Signal()
    sig_open_tutorial = Signal()
    sig_close_session = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
        # Larger, more friendly pill
        self.setMinimumWidth(540)
        self.setFixedHeight(58)
        self._drag_pos = QPoint()
        self._drag_active = False
        self._init_ui()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 4, 8, 4)
        root.setSpacing(3)

        self.pill = QWidget(self)
        self.pill.setObjectName("CapsulePill")
        layout = QHBoxLayout(self.pill)
        layout.setContentsMargins(10, 4, 8, 4)
        layout.setSpacing(8)

        # Status Dot
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("color: #E2886B; font-size: 12px;")
        self.status_dot.setToolTip("Status indicator")
        layout.addWidget(self.status_dot)

        # Status Text
        self.lbl_status = QLabel("SPEAK — Ready")
        self.lbl_status.setStyleSheet("color: #F1F5F9; font-weight: 700; font-size: 12px;")
        layout.addWidget(self.lbl_status)

        # Hint label (what to do)
        self.lbl_hint = QLabel("Ctrl+Space to dictate")
        self.lbl_hint.setStyleSheet("color: #94A3B8; font-size: 10px; font-style: italic;")
        layout.addWidget(self.lbl_hint)

        # Waveform Visualizer
        self.wave_visualizer = SoundWavePillWidget(self)
        layout.addWidget(self.wave_visualizer)

        layout.addStretch(1)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("color: rgba(255,255,255,0.12);")
        sep.setFixedWidth(1)
        layout.addWidget(sep)

        # OBVIOUS LABELED BUTTONS - no tiny mystery icons
        self.btn_canvas = LabeledCapsuleButton("✏️", "Draw", "Screen Pen Tool - Draw on screen (Esc to clear, Right-click to wipe)", parent=self)
        self.btn_canvas.clicked.connect(self.sig_toggle_canvas.emit)
        layout.addWidget(self.btn_canvas)

        self.btn_settings = LabeledCapsuleButton("⚙️", "Settings", "Open Settings & API Vault (Keys, Mic, Prompt)", parent=self)
        self.btn_settings.clicked.connect(self.sig_open_settings.emit)
        layout.addWidget(self.btn_settings)

        self.btn_guide = LabeledCapsuleButton("📖", "Guide", "Open Hotkey Guide & Tutorial", parent=self)
        self.btn_guide.clicked.connect(self.sig_open_tutorial.emit)
        layout.addWidget(self.btn_guide)

        self.btn_close = LabeledCapsuleButton("✕", "Hide", "Hide capsule to tray (still running)", is_close=True, parent=self)
        self.btn_close.clicked.connect(self._on_close_clicked)
        layout.addWidget(self.btn_close)

        root.addWidget(self.pill)
        self.token_bar = HoverTokenBar(self)
        root.addWidget(self.token_bar)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(2, 2, self.width() - 4, self.height() - 6)
        bg_grad = QLinearGradient(0, 0, 0, self.height())
        bg_grad.setColorAt(0.0, QColor("#1E1E24"))
        bg_grad.setColorAt(1.0, QColor("#121216"))
        painter.setBrush(QBrush(bg_grad))
        painter.setPen(QPen(QColor(255, 255, 255, 28), 1))
        painter.drawRoundedRect(rect, 20, 20)
        inner = QRectF(3, 3, self.width() - 6, self.height() - 8)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(255, 255, 255, 10), 1))
        painter.drawRoundedRect(inner, 20, 20)

    def set_status(self, text: str, badge_type: str = "idle"):
        metrics = QFontMetrics(self.lbl_status.font())
        elided = metrics.elidedText(text, Qt.TextElideMode.ElideRight, 160)
        self.lbl_status.setText(elided)
        self.lbl_status.setToolTip(text if elided != text else text)
        # Also update hint based on status
        if badge_type == "active":
            self.lbl_hint.setText("Listening...")
            self.lbl_hint.setStyleSheet("color: #E2886B; font-size: 10px; font-weight: 600;")
        elif badge_type == "warn":
            self.lbl_hint.setText("Working...")
            self.lbl_hint.setStyleSheet("color: #F59E0B; font-size: 10px;")
        elif badge_type == "error":
            self.lbl_hint.setText("Error - check tray")
            self.lbl_hint.setStyleSheet("color: #EF4444; font-size: 10px;")
        else:
            self.lbl_hint.setText("Ctrl+Space to dictate")
            self.lbl_hint.setStyleSheet("color: #94A3B8; font-size: 10px; font-style: italic;")

        color_map = {"idle": "#94A3B8", "active": "#E2886B", "warn": "#F59E0B", "error": "#EF4444"}
        self.status_dot.setStyleSheet(f"color: {color_map.get(badge_type, '#94A3B8')}; font-size: 12px;")

    def _on_close_clicked(self):
        self.sig_close_session.emit()
        self.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._drag_active = True
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_active:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_active = False
        super().mouseReleaseEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        self.update()
