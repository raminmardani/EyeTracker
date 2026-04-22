"""MediaPipe face landmark wrapper with head-pose estimation."""
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np

# Landmark indices (MediaPipe Face Mesh with refine_landmarks=True)
# Eye A (image-right / user's left eye)
EYE_A_OUTER = 33
EYE_A_INNER = 133
EYE_A_TOP = 159
EYE_A_BOTTOM = 145
EYE_A_IRIS = 468
# Eye B (image-left / user's right eye)
EYE_B_INNER = 362
EYE_B_OUTER = 263
EYE_B_TOP = 386
EYE_B_BOTTOM = 374
EYE_B_IRIS = 473

# Canonical 3D points (mm) for solvePnP head-pose
_MODEL_POINTS = np.array([
    (0.0, 0.0, 0.0),            # nose tip        (landmark 1)
    (0.0, -63.6, -12.5),        # chin            (landmark 152)
    (-43.3, 32.7, -26.0),       # eye A outer     (landmark 33)
    (43.3, 32.7, -26.0),        # eye B outer     (landmark 263)
    (-28.9, -28.9, -24.1),      # mouth A corner  (landmark 61)
    (28.9, -28.9, -24.1),       # mouth B corner  (landmark 291)
], dtype=np.float64)
_POSE_LM_IDX = [1, 152, 33, 263, 61, 291]
_TASKS_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
    "face_landmarker/float16/1/face_landmarker.task"
)


def _cache_dir():
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Caches" / "Eyee"
    return Path.home() / ".cache" / "eyee"


def _ensure_tasks_model():
    model_dir = _cache_dir()
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "face_landmarker.task"
    if model_path.exists():
        return model_path

    tmp_path = model_dir / f"{model_path.name}.{os.getpid()}.tmp"
    try:
        with urllib.request.urlopen(_TASKS_MODEL_URL, timeout=30) as src:
            with tmp_path.open("wb") as dst:
                dst.write(src.read())
        tmp_path.replace(model_path)
    except (OSError, urllib.error.URLError) as exc:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise RuntimeError(
            "Failed to download the MediaPipe face landmarker model. "
            f"Check network access or place it at {model_path}."
        ) from exc
    return model_path


class FaceMeshWrapper:
    def __init__(self):
        self._mode = None
        self.mesh = None
        self._last_timestamp_ms = 0

        if hasattr(mp, "solutions"):
            self._mode = "solutions"
            self._mp = mp.solutions.face_mesh
            self.mesh = self._mp.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
            return

        if not hasattr(mp, "tasks") or not hasattr(mp.tasks, "vision"):
            raise RuntimeError(
                "Installed mediapipe package exposes neither `solutions` nor "
                "`tasks.vision`."
            )

        model_path = _ensure_tasks_model()
        options = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_faces=1,
            min_face_detection_confidence=0.3,
            min_face_presence_confidence=0.3,
            min_tracking_confidence=0.3,
        )
        self._mode = "tasks"
        self.mesh = mp.tasks.vision.FaceLandmarker.create_from_options(options)

    def process(self, frame_bgr):
        h, w = frame_bgr.shape[:2]
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        lm = self._detect_landmarks(rgb)
        if lm is None:
            return None
        pts2d = np.array([(p.x * w, p.y * h) for p in lm], dtype=np.float64)
        head_pose = self._head_pose(pts2d, w, h)
        return {"pts2d": pts2d, "head_pose": head_pose, "size": (w, h)}

    def _detect_landmarks(self, frame_rgb):
        if self._mode == "solutions":
            frame_rgb.flags.writeable = False
            result = self.mesh.process(frame_rgb)
            if not result.multi_face_landmarks:
                return None
            return result.multi_face_landmarks[0].landmark

        timestamp_ms = max(self._last_timestamp_ms + 1, int(time.monotonic() * 1000))
        self._last_timestamp_ms = timestamp_ms
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        result = self.mesh.detect_for_video(image, timestamp_ms)
        if not result.face_landmarks:
            return None
        return result.face_landmarks[0]

    def _head_pose(self, pts2d, w, h):
        image_points = pts2d[_POSE_LM_IDX]
        focal = float(w)
        cam = np.array([[focal, 0.0, w / 2.0],
                        [0.0, focal, h / 2.0],
                        [0.0, 0.0, 1.0]], dtype=np.float64)
        dist = np.zeros((4, 1))
        ok, rvec, tvec = cv2.solvePnP(
            _MODEL_POINTS, image_points, cam, dist,
            flags=cv2.SOLVEPNP_ITERATIVE,
        )
        if not ok:
            return None
        rmat, _ = cv2.Rodrigues(rvec)
        sy = np.sqrt(rmat[0, 0] ** 2 + rmat[1, 0] ** 2)
        pitch = float(np.arctan2(-rmat[2, 0], sy))
        yaw = float(np.arctan2(rmat[1, 0], rmat[0, 0]))
        roll = float(np.arctan2(rmat[2, 1], rmat[2, 2]))
        return np.array([yaw, pitch, roll,
                         float(tvec[0, 0]), float(tvec[1, 0]), float(tvec[2, 0])])

    def close(self):
        if self.mesh is not None:
            self.mesh.close()
