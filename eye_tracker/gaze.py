"""Gaze feature extraction from a Face Mesh result."""
import numpy as np
from .face_mesh import (
    EYE_A_OUTER, EYE_A_INNER, EYE_A_TOP, EYE_A_BOTTOM, EYE_A_IRIS,
    EYE_B_OUTER, EYE_B_INNER, EYE_B_TOP, EYE_B_BOTTOM, EYE_B_IRIS,
)


def _eye_ratio(pts, iris_idx, outer, inner, top, bottom):
    iris = pts[iris_idx]
    p_out = pts[outer]; p_in = pts[inner]
    p_top = pts[top]; p_bot = pts[bottom]
    eye_w = float(np.linalg.norm(p_out - p_in)) + 1e-6
    eye_h = float(np.linalg.norm(p_top - p_bot)) + 1e-6
    center = (p_out + p_in) / 2.0
    dx = (iris[0] - center[0]) / eye_w
    dy = (iris[1] - center[1]) / eye_h
    # Eye-aspect ratio (blink indicator)
    ear = eye_h / eye_w
    return dx, dy, ear


def extract_gaze_features(mesh_result):
    """Return a 12-D feature vector describing the current gaze state."""
    pts = mesh_result["pts2d"]
    adx, ady, aear = _eye_ratio(pts, EYE_A_IRIS,
                                EYE_A_OUTER, EYE_A_INNER,
                                EYE_A_TOP, EYE_A_BOTTOM)
    bdx, bdy, bear = _eye_ratio(pts, EYE_B_IRIS,
                                EYE_B_OUTER, EYE_B_INNER,
                                EYE_B_TOP, EYE_B_BOTTOM)
    head = mesh_result.get("head_pose")
    if head is None:
        head = np.zeros(6, dtype=np.float64)
    feat = np.array([
        adx, ady, bdx, bdy,
        (adx + bdx) * 0.5, (ady + bdy) * 0.5,   # averaged gaze
        aear, bear,                              # eye openness
        head[0], head[1], head[2], head[5],      # yaw, pitch, roll, tz
    ], dtype=np.float64)
    return feat
