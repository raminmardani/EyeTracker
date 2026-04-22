"""Entry point: webcam gaze tracker with calibration + on-screen dot overlay."""
import sys

import numpy as np
from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtWidgets import QApplication

from eye_tracker.calibration import GazeCalibrator
from eye_tracker.one_euro import OneEuro2D
from eye_tracker.overlay import CalibrationWindow, GazeOverlay
from eye_tracker.tracker import GazeTracker


class AppController(QObject):
    def __init__(self, cam_index=0, n_cal_points=9, samples_per_point=30):
        super().__init__()
        self.tracker = GazeTracker(cam_index=cam_index)
        self.calibrator = GazeCalibrator()
        self.smoother = OneEuro2D(min_cutoff=1.0, beta=0.007)
        self.overlay = None
        self.calib_win = None
        self.n_cal_points = n_cal_points
        self.samples_per_point = samples_per_point

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
        self.overlay = GazeOverlay()
        self.overlay.show()
        self.tracker.features_ready.connect(self._on_feat)

    @pyqtSlot(object)
    def _on_feat(self, feat):
        if feat is None or self.overlay is None:
            return
        try:
            pred, var = self.calibrator.predict_with_variance(feat)
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
    controller = AppController(cam_index=0, n_cal_points=16, samples_per_point=45)
    app.aboutToQuit.connect(controller.shutdown)
    controller.start()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
