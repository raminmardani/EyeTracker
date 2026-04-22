"""Entry point: webcam gaze tracker with calibration + on-screen dot overlay."""
import sys
from collections import deque

import numpy as np
from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtWidgets import QApplication

from eye_tracker.calibration import GazeCalibrator
from eye_tracker.gaze import FEATURE_A_EAR, FEATURE_B_EAR, FEATURE_YAW
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
        self._feat_history = deque(maxlen=5)

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
        self.overlay = GazeOverlay()
        self.overlay.show()
        self.tracker.features_ready.connect(self._on_feat)

    @pyqtSlot(object)
    def _on_feat(self, feat):
        if feat is None or self.overlay is None:
            return
        feat = np.asarray(feat, dtype=np.float64)
        if (
            feat[FEATURE_A_EAR] < 0.16
            or feat[FEATURE_B_EAR] < 0.16
            or abs(feat[FEATURE_YAW]) > 0.70
        ):
            return
        self._feat_history.append(feat)
        feat_for_pred = np.median(np.asarray(self._feat_history), axis=0)
        try:
            pred, var = self.calibrator.predict_with_variance(feat_for_pred)
        except Exception as exc:  # predictor rarely but can fail on degenerate input
            print(f"[predict] {exc}")
            return
        if not np.all(np.isfinite(pred)):
            return
        x, y = self.smoother.filter(float(pred[0]), float(pred[1]), variance=var)
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
