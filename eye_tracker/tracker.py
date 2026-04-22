"""Background worker: webcam capture + Face Mesh + gaze-feature emission."""
import sys
import threading
import time

import cv2
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal

from .face_mesh import FaceMeshWrapper
from .gaze import extract_gaze_features


def _preferred_backends():
    """Platform-appropriate OpenCV capture backends, tried in order."""
    if sys.platform == "darwin":
        return [cv2.CAP_AVFOUNDATION, cv2.CAP_ANY]
    if sys.platform.startswith("win"):
        return [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
    return [cv2.CAP_V4L2, cv2.CAP_ANY]


class GazeTracker(QObject):
    # emits a feature vector (np.ndarray) or None when no face is visible
    features_ready = pyqtSignal(object)

    def __init__(self, cam_index=0, width=1280, height=720, fps=30):
        super().__init__()
        self.cam_index = cam_index
        self.width = width
        self.height = height
        self.fps = fps
        self._stop = False
        self._thread = None
        self._clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    def start(self):
        self._stop = False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop = True
        if self._thread is not None:
            self._thread.join(timeout=1.5)

    def _open_capture(self):
        for backend in _preferred_backends():
            cap = cv2.VideoCapture(self.cam_index, backend)
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                cap.set(cv2.CAP_PROP_FPS, self.fps)
                return cap
            cap.release()
        return cv2.VideoCapture(self.cam_index)

    def _preprocess(self, frame):
        # Mirror so the user's iris moves in the same direction as their gaze
        frame = cv2.flip(frame, 1)
        # CLAHE on luminance for robustness under uneven lighting
        yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
        yuv[:, :, 0] = self._clahe.apply(yuv[:, :, 0])
        return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)

    def _run(self):
        cap = self._open_capture()
        if not cap.isOpened():
            print("[tracker] failed to open webcam")
            return
        mesh = FaceMeshWrapper()
        try:
            while not self._stop:
                ok, frame = cap.read()
                if not ok:
                    time.sleep(0.01)
                    continue
                frame = self._preprocess(frame)
                result = mesh.process(frame)
                if result is None:
                    self.features_ready.emit(None)
                    continue
                feat = extract_gaze_features(result)
                self.features_ready.emit(feat)
        finally:
            cap.release()
            mesh.close()
