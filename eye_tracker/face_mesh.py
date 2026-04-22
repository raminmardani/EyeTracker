"""MediaPipe Face Mesh wrapper with head-pose estimation."""
import cv2
import numpy as np
import mediapipe as mp

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


class FaceMeshWrapper:
    def __init__(self):
        self._mp = mp.solutions.face_mesh
        self.mesh = self._mp.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def process(self, frame_bgr):
        h, w = frame_bgr.shape[:2]
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        result = self.mesh.process(rgb)
        if not result.multi_face_landmarks:
            return None
        lm = result.multi_face_landmarks[0].landmark
        pts2d = np.array([(p.x * w, p.y * h) for p in lm], dtype=np.float64)
        head_pose = self._head_pose(pts2d, w, h)
        return {"pts2d": pts2d, "head_pose": head_pose, "size": (w, h)}

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
        self.mesh.close()
