"""Entry point: webcam gaze tracker with calibration + on-screen dot overlay."""
import sys
import time
from collections import deque

import numpy as np
from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtWidgets import QApplication

from eye_tracker.calibration import GazeCalibrator
from eye_tracker.gaze import (
    FEATURE_A_EAR,
    FEATURE_B_EAR,
    FEATURE_AVG_DX,
    FEATURE_AVG_DY,
    FEATURE_BLINK_AVG,
    FEATURE_FACE_CX,
    FEATURE_FACE_CY,
    FEATURE_LOOK_H_AVG,
    FEATURE_LOOK_V_AVG,
    FEATURE_PITCH,
    FEATURE_SQUINT_AVG,
    FEATURE_YAW,
)
from eye_tracker.one_euro import OneEuro2D
from eye_tracker.overlay import CalibrationWindow, GazeOverlay
from eye_tracker.tracker import GazeTracker


class AppController(QObject):
    def __init__(self, cam_index=0, n_cal_points=9, samples_per_point=30):
        super().__init__()
        self.tracker = GazeTracker(cam_index=cam_index)
        self.calibrator = GazeCalibrator()
        self.smoother = OneEuro2D(min_cutoff=1.6, beta=0.06)
        self.overlay = None
        self.calib_win = None
        self.n_cal_points = n_cal_points
        self.samples_per_point = samples_per_point
        self._feat_history = deque(maxlen=7)
        self._last_live_feat = None
        self._last_live_t = None

    def start(self):
        self.tracker.start()
        self.calib_win = CalibrationWindow(
            self.tracker,
            n_points=self.n_cal_points,
            samples_per_point=self.samples_per_point,
        )
        self.calib_win.finished.connect(self._on_calib_done)

    @pyqtSlot(object, object)
    def _on_calib_done(self, X, Y):
        if X is None or len(X) < 5:
            print("[calibration] too few points collected — aborting")
            self.tracker.stop()
            QApplication.instance().quit()
            return
        self.calibrator.fit(X, Y)
        self._feat_history.clear()
        self._last_live_feat = None
        self._last_live_t = None
        self.overlay = GazeOverlay()
        self.overlay.show()
        self.tracker.features_ready.connect(self._on_feat)

    def _motion_score(self, feat, now):
        if self._last_live_feat is None or self._last_live_t is None:
            self._last_live_feat = feat.copy()
            self._last_live_t = now
            return 0.0
        dt = max(now - self._last_live_t, 1e-3)
        gaze_delta = np.linalg.norm(
            feat[[FEATURE_AVG_DX, FEATURE_AVG_DY, FEATURE_LOOK_H_AVG, FEATURE_LOOK_V_AVG]]
            - self._last_live_feat[[FEATURE_AVG_DX, FEATURE_AVG_DY, FEATURE_LOOK_H_AVG, FEATURE_LOOK_V_AVG]]
        ) / dt
        head_delta = np.linalg.norm(
            feat[[FEATURE_YAW, FEATURE_PITCH, FEATURE_FACE_CX, FEATURE_FACE_CY]]
            - self._last_live_feat[[FEATURE_YAW, FEATURE_PITCH, FEATURE_FACE_CX, FEATURE_FACE_CY]]
        ) / dt
        lid_delta = abs(float(feat[FEATURE_BLINK_AVG] - self._last_live_feat[FEATURE_BLINK_AVG])) / dt
        self._last_live_feat = feat.copy()
        self._last_live_t = now
        return float(gaze_delta + 0.6 * head_delta + 0.3 * lid_delta)

    @pyqtSlot(object)
    def _on_feat(self, feat):
        if feat is None or self.overlay is None:
            return
        feat = np.asarray(feat, dtype=np.float64)
        blink = feat[FEATURE_BLINK_AVG]
        squint = feat[FEATURE_SQUINT_AVG]
        if (
            feat[FEATURE_A_EAR] < 0.16
            or feat[FEATURE_B_EAR] < 0.16
            or blink > 0.58
            or squint > 0.58
            or abs(feat[FEATURE_YAW]) > 0.70
            or abs(feat[FEATURE_PITCH]) > 0.55
        ):
            return
        now = time.monotonic()
        motion = self._motion_score(feat, now)
        self._feat_history.append(feat)
        if motion > 22.0:
            window = 2
        elif motion > 10.0:
            window = 3
        else:
            window = min(len(self._feat_history), 5)
        feat_for_pred = np.median(np.asarray(list(self._feat_history)[-window:]), axis=0)
        try:
            pred, var = self.calibrator.predict_with_variance(feat_for_pred)
        except Exception as exc:  # predictor rarely but can fail on degenerate input
            print(f"[predict] {exc}")
            return
        if not np.all(np.isfinite(pred)):
            return
        x, y = self.smoother.filter(
            float(pred[0]),
            float(pred[1]),
            variance=var,
            motion=motion,
        )
        self.overlay.update_position(x, y)

    def shutdown(self):
        self.tracker.stop()


def main():
    app = QApplication(sys.argv)
    controller = AppController(cam_index=0, n_cal_points=25, samples_per_point=60)
    app.aboutToQuit.connect(controller.shutdown)
    controller.start()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
