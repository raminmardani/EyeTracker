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

    def __init__(self, cam_index=0, width=1920, height=1080, fps=30):
        super().__init__()
        self.cam_index = cam_index
        self.width = width
        self.height = height
        self.fps = fps
        self._stop = False
        self._thread = None
        self._no_face_streak = 0

    def start(self):
        self._stop = False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop = True
        if self._thread is not None:
            self._thread.join(timeout=1.5)

    def _configure_capture(self, cap):
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        cap.set(cv2.CAP_PROP_FPS, self.fps)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def _candidate_indices(self):
        if self.cam_index is None or self.cam_index < 0:
            return [0, 1, 2, 3]
        return [self.cam_index] + [idx for idx in range(4) if idx != self.cam_index]

    def _probe_capture(self, cap, probe_mesh=None, warmup_frames=8):
        last_frame = None
        valid_frames = 0
        detected = 0
        for _ in range(warmup_frames):
            ok, frame = cap.read()
            if ok and frame is not None:
                last_frame = frame
                valid_frames += 1
                if probe_mesh is not None and probe_mesh.process(self._prepare_frame(frame)) is not None:
                    detected += 1
            time.sleep(0.04)
        if last_frame is None:
            return None
        gray = cv2.cvtColor(last_frame, cv2.COLOR_BGR2GRAY)
        mean = float(gray.mean())
        std = float(gray.std())
        score = mean + 1.5 * std
        viable = mean >= 25.0 or std >= 10.0
        return {
            "mean": mean,
            "std": std,
            "score": score,
            "viable": viable,
            "valid_frames": valid_frames,
            "detected_frames": detected,
        }

    def _open_capture(self, probe_mesh=None):
        best = None
        fallback = None
        for idx in self._candidate_indices():
            for backend in _preferred_backends():
                cap = cv2.VideoCapture(idx, backend)
                if not cap.isOpened():
                    cap.release()
                    continue
                self._configure_capture(cap)
                probe = self._probe_capture(cap, probe_mesh=probe_mesh)
                cap.release()
                if probe is None:
                    continue
                candidate = {"idx": idx, "backend": backend, **probe}
                if fallback is None or candidate["score"] > fallback["score"]:
                    fallback = candidate
                if candidate["detected_frames"] > 0 and (
                    best is None
                    or candidate["detected_frames"] > best["detected_frames"]
                    or (
                        candidate["detected_frames"] == best["detected_frames"]
                        and candidate["score"] > best["score"]
                    )
                ):
                    best = candidate

        chosen = best or fallback
        if chosen is None:
            return cv2.VideoCapture(self.cam_index if self.cam_index is not None else 0)

        cap = cv2.VideoCapture(chosen["idx"], chosen["backend"])
        if not cap.isOpened():
            cap.release()
            return cv2.VideoCapture(chosen["idx"])
        self._configure_capture(cap)
        if self.cam_index is not None and self.cam_index >= 0 and chosen["idx"] != self.cam_index:
            print(
                f"[tracker] camera index {self.cam_index} looked unusable; "
                f"using camera index {chosen['idx']} instead"
            )
        print(
            f"[tracker] selected camera index {chosen['idx']} "
            f"(backend {chosen['backend']}, faces={chosen['detected_frames']}/"
            f"{chosen['valid_frames']}, mean={chosen['mean']:.1f}, std={chosen['std']:.1f})"
        )
        return cap

    def _prepare_frame(self, frame):
        # Mirror so the user's iris moves in the same direction as their gaze
        return cv2.flip(frame, 1)

    def _run(self):
        try:
            mesh = FaceMeshWrapper()
        except Exception as exc:
            print(f"[tracker] failed to initialize face landmarks: {exc}")
            return
        cap = self._open_capture(probe_mesh=mesh)
        if not cap.isOpened():
            print("[tracker] failed to open webcam")
            mesh.close()
            return
        try:
            while not self._stop:
                ok, frame = cap.read()
                if not ok:
                    time.sleep(0.01)
                    continue
                frame = self._prepare_frame(frame)
                result = mesh.process(frame)
                if result is None:
                    self._no_face_streak += 1
                    if self._no_face_streak % 90 == 0:
                        print(
                            "[tracker] no face landmarks detected "
                            f"for {self._no_face_streak} frames"
                        )
                    self.features_ready.emit(None)
                    continue
                self._no_face_streak = 0
                feat = extract_gaze_features(result)
                self.features_ready.emit(feat)
        finally:
            cap.release()
            mesh.close()
