"""PyQt6 windows: click-through gaze dot + calibration collector."""
import sys

import numpy as np
from PyQt6.QtCore import Qt, QTimer, QPointF, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen
from PyQt6.QtWidgets import QApplication, QWidget

_IS_MAC = sys.platform == "darwin"


class GazeOverlay(QWidget):
    """Transparent, always-on-top, click-through dot."""

    def __init__(self):
        super().__init__()
        flags = (
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.WindowTransparentForInput
        )
        # Tool-style windows hide when the owning app loses focus on macOS,
        # which would make the overlay disappear as soon as you click elsewhere.
        if not _IS_MAC:
            flags |= Qt.WindowType.Tool
        else:
            flags |= Qt.WindowType.BypassWindowManagerHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self._x = screen.width() / 2.0
        self._y = screen.height() / 2.0
        self._visible_dot = True

    def update_position(self, x, y):
        self._x = float(x)
        self._y = float(y)
        self.update()

    def set_dot_visible(self, visible: bool):
        self._visible_dot = visible
        self.update()

    def paintEvent(self, _):
        if not self._visible_dot:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor(255, 40, 40, 210)))
        p.setPen(QPen(QColor(255, 255, 255, 230), 2))
        p.drawEllipse(QPointF(self._x, self._y), 14.0, 14.0)


class CalibrationWindow(QWidget):
    """Full-screen dark window that cycles through calibration dots."""

    finished = pyqtSignal(object, object)  # (X feature-matrix, Y target-matrix)

    def __init__(self, tracker, n_points=9, samples_per_point=30,
                 dwell_ms=900):
        super().__init__()
        self.tracker = tracker
        self.samples_per_point = samples_per_point
        self.dwell_ms = dwell_ms
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.points = self._grid(screen.width(), screen.height(), n_points)
        self.idx = 0
        self.collecting = False
        self._buf = []
        self.X, self.Y = [], []

        self._dwell_timer = QTimer(self)
        self._dwell_timer.setSingleShot(True)
        self._dwell_timer.timeout.connect(self._begin_collect)

        self._feat_handler = self._on_feat
        self.tracker.features_ready.connect(self._feat_handler)

        # On macOS, showFullScreen() triggers a native full-screen animation
        # and moves the window to its own Space — we just want a borderless
        # window that covers the display.
        if _IS_MAC:
            self.show()
            self.raise_()
            self.activateWindow()
        else:
            self.showFullScreen()
        self.setFocus()
        QTimer.singleShot(600, self._advance)

    @staticmethod
    def _grid(w, h, n):
        if n <= 9:
            xs = [0.1, 0.5, 0.9]; ys = [0.1, 0.5, 0.9]
        elif n <= 16:
            xs = [0.07, 0.36, 0.64, 0.93]; ys = [0.07, 0.36, 0.64, 0.93]
        else:
            xs = np.linspace(0.07, 0.93, 5); ys = np.linspace(0.07, 0.93, 5)
        return [(int(w * x), int(h * y)) for y in ys for x in xs]

    def _advance(self):
        if self.idx >= len(self.points):
            self._disconnect()
            self.finished.emit(np.array(self.X), np.array(self.Y))
            self.close()
            return
        self.update()
        self._dwell_timer.start(self.dwell_ms)

    def _begin_collect(self):
        self._buf = []
        self.collecting = True
        self.update()

    def _on_feat(self, feat):
        if not self.collecting or feat is None:
            return
        # Reject blinks (EAR below threshold) and off-axis head turns —
        # those frames poison the per-dot average otherwise.
        ear_a, ear_b = feat[6], feat[7]
        yaw = feat[8]
        if ear_a < 0.22 or ear_b < 0.22 or abs(yaw) > 0.25:
            return
        self._buf.append(feat)
        if len(self._buf) >= self.samples_per_point:
            self.collecting = False
            # Median is robust to the few bad frames that slip past the gate.
            feat_repr = np.median(np.asarray(self._buf), axis=0)
            self.X.append(feat_repr)
            self.Y.append(self.points[self.idx])
            self.idx += 1
            QTimer.singleShot(250, self._advance)

    def _disconnect(self):
        try:
            self.tracker.features_ready.disconnect(self._feat_handler)
        except (TypeError, RuntimeError):
            pass

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self._disconnect()
            self.finished.emit(np.array(self.X), np.array(self.Y))
            self.close()

    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(18, 18, 22))
        p.setPen(QPen(QColor(180, 180, 180)))
        p.drawText(
            self.rect().adjusted(0, 24, 0, 0),
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter,
            f"Look at the dot  ({min(self.idx + 1, len(self.points))}/{len(self.points)})"
            "   —   Esc to abort",
        )
        if self.idx >= len(self.points):
            return
        cx, cy = self.points[self.idx]
        # Outer ring
        p.setBrush(QBrush(QColor(50, 50, 60)))
        p.setPen(QPen(QColor(220, 220, 220), 2))
        p.drawEllipse(QPointF(cx, cy), 26, 26)
        # Inner dot — colour indicates "collecting"
        inner = QColor(0, 210, 255) if self.collecting else QColor(255, 170, 40)
        p.setBrush(QBrush(inner))
        p.setPen(QPen(QColor(255, 255, 255), 1))
        p.drawEllipse(QPointF(cx, cy), 10, 10)
