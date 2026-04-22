"""Gaze feature extraction from face landmarks."""
import math

import numpy as np

from .face_mesh import (
    EYE_A_BOTTOM,
    EYE_A_INNER,
    EYE_A_IRIS,
    EYE_A_OUTER,
    EYE_A_TOP,
    EYE_B_BOTTOM,
    EYE_B_INNER,
    EYE_B_IRIS,
    EYE_B_OUTER,
    EYE_B_TOP,
)

_EYE_A_IRIS_RING = [EYE_A_IRIS, 469, 470, 471, 472]
_EYE_B_IRIS_RING = [EYE_B_IRIS, 474, 475, 476, 477]
_EYE_A_TOP_RING = [159, 160, 161]
_EYE_A_BOTTOM_RING = [144, 145, 153]
_EYE_B_TOP_RING = [386, 387, 388]
_EYE_B_BOTTOM_RING = [373, 374, 380]

FEATURE_A_DX = 0
FEATURE_A_DY = 1
FEATURE_B_DX = 2
FEATURE_B_DY = 3
FEATURE_AVG_DX = 4
FEATURE_AVG_DY = 5
FEATURE_A_EAR = 6
FEATURE_B_EAR = 7
FEATURE_YAW = 8
FEATURE_PITCH = 9
FEATURE_ROLL = 10
FEATURE_TZ = 11
FEATURE_TX = 12
FEATURE_TY = 13
FEATURE_VERGENCE_X = 14
FEATURE_VERGENCE_Y = 15
FEATURE_A_IRIS_RADIUS = 16
FEATURE_B_IRIS_RADIUS = 17
FEATURE_FACE_CX = 18
FEATURE_FACE_CY = 19
FEATURE_FACE_SCALE = 20
FEATURE_INTEROCULAR = 21
FEATURE_COUNT = 22


def _centroid(pts, indices):
    if np.isscalar(indices):
        return pts[int(indices)]
    return np.mean(pts[np.asarray(indices, dtype=np.int32)], axis=0)


def _eye_geometry(pts, outer_idx, inner_idx, top_idx, bottom_idx, iris_ring_idx):
    p_out = _centroid(pts, outer_idx)
    p_in = _centroid(pts, inner_idx)
    p_top = _centroid(pts, top_idx)
    p_bot = _centroid(pts, bottom_idx)
    iris = _centroid(pts, iris_ring_idx)

    eye_vec = p_in - p_out
    eye_w = float(np.linalg.norm(eye_vec)) + 1e-6
    u = eye_vec / eye_w

    # Use an eye-local vertical axis so gaze features stay stable under roll.
    v = np.array([-u[1], u[0]], dtype=np.float64)
    lid_vec = p_bot - p_top
    if np.dot(lid_vec, v) < 0.0:
        v = -v
    eye_h = abs(float(np.dot(lid_vec, v))) + 1e-6

    center = 0.25 * (p_out + p_in + p_top + p_bot)
    iris_offset = iris - center
    dx = float(np.dot(iris_offset, u) / eye_w)
    dy = float(np.dot(iris_offset, v) / eye_h)
    ear = eye_h / eye_w

    iris_ring = pts[np.asarray(iris_ring_idx, dtype=np.int32)]
    iris_radius = float(np.mean(np.linalg.norm(iris_ring - iris, axis=1)) / eye_w)
    return {
        "dx": dx,
        "dy": dy,
        "ear": ear,
        "iris_radius": iris_radius,
        "center": center,
    }


def extract_gaze_features(mesh_result):
    """Return a feature vector describing the current gaze state."""
    pts = mesh_result["pts2d"]
    w, h = mesh_result["size"]

    eye_a = _eye_geometry(
        pts,
        EYE_A_OUTER,
        EYE_A_INNER,
        _EYE_A_TOP_RING,
        _EYE_A_BOTTOM_RING,
        _EYE_A_IRIS_RING,
    )
    eye_b = _eye_geometry(
        pts,
        EYE_B_OUTER,
        EYE_B_INNER,
        _EYE_B_TOP_RING,
        _EYE_B_BOTTOM_RING,
        _EYE_B_IRIS_RING,
    )

    head = mesh_result.get("head_pose")
    if head is None:
        head = np.zeros(6, dtype=np.float64)
    else:
        head = np.asarray(head, dtype=np.float64)

    eye_mid = 0.5 * (eye_a["center"] + eye_b["center"])
    interocular = float(np.linalg.norm(eye_a["center"] - eye_b["center"]))
    face_scale = interocular / (float(w) + 1e-6)
    face_cx = eye_mid[0] / float(w) - 0.5
    face_cy = eye_mid[1] / float(h) - 0.5

    return np.array([
        eye_a["dx"],
        eye_a["dy"],
        eye_b["dx"],
        eye_b["dy"],
        0.5 * (eye_a["dx"] + eye_b["dx"]),
        0.5 * (eye_a["dy"] + eye_b["dy"]),
        eye_a["ear"],
        eye_b["ear"],
        float(head[0]),
        float(head[1]),
        float(head[2]),
        float(head[5]),
        float(head[3]),
        float(head[4]),
        eye_a["dx"] - eye_b["dx"],
        eye_a["dy"] - eye_b["dy"],
        eye_a["iris_radius"],
        eye_b["iris_radius"],
        float(face_cx),
        float(face_cy),
        float(face_scale),
        interocular / (math.sqrt(float(w) * float(h)) + 1e-6),
    ], dtype=np.float64)
