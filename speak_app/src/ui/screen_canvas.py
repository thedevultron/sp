from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath


class ScreenCanvasOverlay(QWidget):
    """Transparent drawing layer for marking screens with Claude terracotta ink.
    Fixed for multi-monitor / HighDPI / virtualGeometry edge cases.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        # Allow keyboard focus for Esc handling
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._strokes = []
        self._current_path = None
        self._pen_color = QColor("#DA7756")
        self._pen_width = 4
        self._is_drawing = False

    def show_canvas(self):
        # Fix: Use QApplication virtualGeometry (not self.screen() which may be None)
        try:
            geo = QApplication.primaryScreen().virtualGeometry() if QApplication.primaryScreen() else None
            if geo is None or geo.isEmpty():
                # Fallback: union of all screens
                geo = QApplication.primaryScreen().geometry() if QApplication.primaryScreen() else self.geometry()
                for scr in QApplication.screens():
                    geo = geo.united(scr.geometry())
            self.setGeometry(geo)
        except Exception as e:
            print(f"[Canvas] Geometry error: {e}")
            # Fallback to primary screen
            try:
                self.setGeometry(QApplication.primaryScreen().geometry())
            except Exception:
                pass
        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus()
        # Ensure we are on top
        self.update()

    def clear_all(self):
        self._strokes.clear()
        self._current_path = None
        self.update()

    def hideEvent(self, event):
        # Clear focus issues
        super().hideEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.clear_all()
            self.hide()
            event.accept()
            return
        elif event.key() == Qt.Key.Key_1:
            self._pen_color = QColor("#DA7756")  # Terracotta
            event.accept()
            return
        elif event.key() == Qt.Key.Key_2:
            self._pen_color = QColor("#D97706")  # Amber
            event.accept()
            return
        elif event.key() == Qt.Key.Key_3:
            self._pen_color = QColor("#F3F3EE")  # Clean White
            event.accept()
            return
        elif event.key() == Qt.Key.Key_C and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.clear_all()
            event.accept()
            return
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_drawing = True
            self._current_path = QPainterPath()
            self._current_path.moveTo(event.position())
            self._strokes.append((self._current_path, QColor(self._pen_color), self._pen_width))
            self.update()
            event.accept()
            return
        elif event.button() == Qt.MouseButton.RightButton:
            # Right-click to clear
            self.clear_all()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_drawing and self._current_path:
            self._current_path.lineTo(event.position())
            self.update()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_drawing = False
            self.update()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        # Dim background slightly to indicate drawing mode
        painter.fillRect(self.rect(), QColor(0, 0, 0, 18))

        for path, col, w in self._strokes:
            pen = QPen(col, w, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawPath(path)

        # Hint text when empty
        if not self._strokes:
            painter.setPen(QColor(255, 255, 255, 90))
            painter.drawText(self.rect().adjusted(20, 20, -20, -20),
                             Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter,
                             "Drawing Mode  •  Draw with mouse  •  Esc to clear & exit  •  1/2/3 colors  •  Right-click to clear")
