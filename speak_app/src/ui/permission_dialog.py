"""Startup permission-ask modal — mic + screen, impossible to miss.

The banner alone was too easy to overlook (users reported blank vision that
never asked). This modal appears on launch whenever microphone or screen
capture is not granted, with one-click Grant buttons that open the native
Windows privacy pages and re-check. Never raises, never blocks the app:
Continue/Later always closes it.
"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt


class PermissionAskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SPEAK needs permission")
        self.setModal(True)
        self.setMinimumWidth(460)
        self._mic_status = "unknown"
        self._screen_status = "unknown"
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(10)

        title = QLabel("Allow microphone + screen sharing")
        title.setStyleSheet("color: #D8ECF8; font-size: 15px; font-weight: 700;")
        lay.addWidget(title)
        sub = QLabel("Without these, dictation hears nothing and the AI sees a blank screen. "
                     "Windows requires you to approve in Settings — one click opens the right page.")
        sub.setWordWrap(True)
        sub.setStyleSheet("color: #9DA7BA; font-size: 12px;")
        lay.addWidget(sub)

        self.lbl_mic = QLabel()
        self.lbl_mic.setWordWrap(True)
        lay.addWidget(self.lbl_mic)
        mic_row = QHBoxLayout()
        mic_row.addStretch()
        self.btn_mic = QPushButton("Grant Microphone")
        self.btn_mic.setFixedHeight(32)
        self.btn_mic.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mic.setStyleSheet("QPushButton { background-color: #663AF3; color: #FFFFFF; border: 1px solid #7A52FF; border-radius: 8px; padding: 4px 14px; font-weight: 600; } QPushButton:hover { background-color: #7550F5; }")
        self.btn_mic.clicked.connect(self._grant_mic)
        mic_row.addWidget(self.btn_mic)
        lay.addLayout(mic_row)

        self.lbl_screen = QLabel()
        self.lbl_screen.setWordWrap(True)
        lay.addWidget(self.lbl_screen)
        scr_row = QHBoxLayout()
        scr_row.addStretch()
        self.btn_screen = QPushButton("Grant Screen")
        self.btn_screen.setFixedHeight(32)
        self.btn_screen.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_screen.setStyleSheet("QPushButton { background-color: #663AF3; color: #FFFFFF; border: 1px solid #7A52FF; border-radius: 8px; padding: 4px 14px; font-weight: 600; } QPushButton:hover { background-color: #7550F5; }")
        self.btn_screen.clicked.connect(self._grant_screen)
        scr_row.addWidget(self.btn_screen)
        lay.addLayout(scr_row)

        bot = QHBoxLayout()
        bot.addStretch()
        self.btn_later = QPushButton("Later")
        self.btn_later.setFixedHeight(32)
        self.btn_later.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_later.setStyleSheet("QPushButton { background: transparent; color: #9DA7BA; border: 1px solid #1FBAD7F7; border-radius: 8px; padding: 4px 14px; } QPushButton:hover { color: #FFFFFF; }")
        self.btn_later.clicked.connect(self.reject)
        bot.addWidget(self.btn_later)
        self.btn_continue = QPushButton("Continue")
        self.btn_continue.setFixedHeight(32)
        self.btn_continue.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_continue.setStyleSheet("QPushButton { background: #14BAD6F7; color: #D1E4FA; border: 1px solid #1FBAD7F7; border-radius: 8px; padding: 4px 18px; font-weight: 600; } QPushButton:hover { color: #FFFFFF; }")
        self.btn_continue.clicked.connect(self.accept)
        bot.addWidget(self.btn_continue)
        lay.addLayout(bot)
        self.refresh()

    def _fmt(self, ok: bool, label: str, detail: str = "") -> str:
        dot = "#30D158" if ok else "#FF9F0A"
        word = "Ready" if ok else "Blocked"
        extra = f" — {detail[:100]}" if detail and not ok else ""
        return f"<span style='color:{dot};'>\u25cf</span> <b>{label}:</b> {word}{extra}"

    def refresh(self):
        try:
            from src.permission_manager import mic_permission_manager, permission_manager
            try:
                self._mic_status = mic_permission_manager.check_permission()
                merr = mic_permission_manager.last_error
            except Exception:
                self._mic_status, merr = "pending", ""
            try:
                self._screen_status = permission_manager.check_permission()
                serr = permission_manager.last_error
            except Exception:
                self._screen_status, serr = "pending", ""
            self.lbl_mic.setText(self._fmt(self._mic_status == "granted", "Microphone", merr))
            self.lbl_screen.setText(self._fmt(self._screen_status == "granted", "Screen", serr))
            self.btn_mic.setEnabled(self._mic_status != "granted")
            self.btn_screen.setEnabled(self._screen_status != "granted")
            if self._mic_status == "granted" and self._screen_status == "granted":
                self.accept()
        except Exception:
            pass

    def _grant_mic(self):
        try:
            from src.permission_manager import mic_permission_manager
            mic_permission_manager.request_permission()
        except Exception:
            pass
        self.refresh()

    def _grant_screen(self):
        try:
            from src.permission_manager import permission_manager
            permission_manager.request_permission()
        except Exception:
            pass
        self.refresh()

    def all_granted(self) -> bool:
        return self._mic_status == "granted" and self._screen_status == "granted"
