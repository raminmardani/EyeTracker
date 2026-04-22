"""PyQt6 windows: click-through gaze dot + calibration collector."""
import sys

import numpy as np
from PyQt6.QtCore import Qt, QTimer, QPointF, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen
from PyQt6.QtWidgets import QApplication, QWidget

from .gaze import FEATURE_A_EAR, FEATURE_B_EAR, FEATURE_YAW

_IS_MAC = sys.platform == "darwin"


def _representative_feature(samples):
    arr = np.asarray(samples, dtype=np.float64)
    if len(arr) <= 4:
        return np.median(arr, axis=0)

    center = np.median(arr, axis=0)
    mad = np.median(np.abs(arr - center), axis=0)
    scale = np.where(mad > 1e-6, mad, 1.0)
    dist = np.sqrt(np.mean(((arr - center) / scale) ** 2, axis=1))
    keep = max(8, int(round(len(arr) * 0.7)))
    keep = min(keep, len(arr))
    chosen = arr[np.argsort(dist)[:keep]]
    return np.median(chosen, axis=0)


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
        self._x = float(np.clip(x, 0.0, max(0.0, self.width() - 1.0)))
        self._y = float(np.clip(y, 0.0, max(0.0, self.height() - 1.0)))
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
                 dwell_ms=900, collect_timeout_ms=4500):
        super().__init__()
        self.tracker = tracker
        self.samples_per_point = samples_per_point
        self.min_samples_per_point = max(10, samples_per_point // 3)
        self.dwell_ms = dwell_ms
        self.collect_timeout_ms = collect_timeout_ms
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.points = self._grid(screen.width(), screen.height(), n_points)
        self.idx = 0
        self._started = False
        self.collecting = False
        self._buf = []
        self._fallback_buf = []
        self.X, self.Y = [], []

        self._dwell_timer = QTimer(self)
        self._dwell_timer.setSingleShot(True)
        self._dwell_timer.timeout.connect(self._begin_collect)

        self._collect_timer = QTimer(self)
        self._collect_timer.setSingleShot(True)
        self._collect_timer.timeout.connect(self._finish_collect)

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
        self._fallback_buf = []
        self.collecting = True
        self._collect_timer.start(self.collect_timeout_ms)
        self.update()

    def _on_feat(self, feat):
        if feat is None:
            return
        feat = np.asarray(feat, dtype=np.float64)
        if not np.all(np.isfinite(feat)):
            return
        if not self._started:
            self._started = True
            self.update()
            QTimer.singleShot(250, self._advance)
            return
        if not self.collecting:
            return
        self._fallback_buf.append(feat)
        # Prefer frames with both eyes open and a roughly centered head pose,
        # but do not deadlock calibration if the thresholds are too strict on
        # a given machine/camera combination.
        ear_a, ear_b = feat[FEATURE_A_EAR], feat[FEATURE_B_EAR]
        yaw = feat[FEATURE_YAW]
        if ear_a < 0.16 or ear_b < 0.16 or abs(yaw) > 0.60:
            return
        self._buf.append(feat)
        if len(self._buf) >= self.samples_per_point:
            self._finish_collect()

    def _finish_collect(self):
        if not self.collecting:
            return
        self.collecting = False
        self._collect_timer.stop()

        chosen = None
        point_no = self.idx + 1
        if len(self._buf) >= self.min_samples_per_point:
            chosen = self._buf
        elif len(self._fallback_buf) >= self.min_samples_per_point:
            chosen = self._fallback_buf
            print(
                f"[calibration] point {point_no}: using relaxed fallback "
                f"({len(self._buf)} strict / {len(self._fallback_buf)} total)"
            )
        elif self._fallback_buf:
            chosen = self._fallback_buf
            print(
                f"[calibration] point {point_no}: low sample count "
                f"({len(self._fallback_buf)}/{self.min_samples_per_point})"
            )
        else:
            print(f"[calibration] point {point_no}: no usable samples, skipping")

        if chosen is not None:
            feat_repr = _representative_feature(chosen)
            self.X.append(feat_repr)
            self.Y.append(self.points[self.idx])
        self.idx += 1
        self.update()
        QTimer.singleShot(250, self._advance)

    def _disconnect(self):
        try:
            self.tracker.features_ready.disconnect(self._feat_handler)
        except (TypeError, RuntimeError):
            pass
        self._dwell_timer.stop()
        self._collect_timer.stop()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self._disconnect()
            self.finished.emit(np.array(self.X), np.array(self.Y))
            self.close()

    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(18, 18, 22))
        p.setPen(QPen(QColor(180, 180, 180)))
        message = (
            f"Look at the dot  ({min(self.idx + 1, len(self.points))}/{len(self.points)})"
            "   —   Esc to abort"
        )
        if not self._started:
            message = "Center your face in the camera to start calibration   —   Esc to abort"
        p.drawText(
            self.rect().adjusted(0, 24, 0, 0),
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter,
            message,
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
