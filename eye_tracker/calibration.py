"""Robust calibration from gaze features to screen coordinates."""
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, RBF, WhiteKernel
from sklearn.preprocessing import StandardScaler

from .gaze import (
    FEATURE_A_DX,
    FEATURE_A_DY,
    FEATURE_A_EAR,
    FEATURE_A_IRIS_RADIUS,
    FEATURE_A_LOWER_CLEAR,
    FEATURE_A_UPPER_CLEAR,
    FEATURE_AVG_DX,
    FEATURE_AVG_DY,
    FEATURE_B_DX,
    FEATURE_B_DY,
    FEATURE_B_EAR,
    FEATURE_B_IRIS_RADIUS,
    FEATURE_B_LOWER_CLEAR,
    FEATURE_B_UPPER_CLEAR,
    FEATURE_FACE_CX,
    FEATURE_FACE_CY,
    FEATURE_FACE_SCALE,
    FEATURE_INTEROCULAR,
    FEATURE_PITCH,
    FEATURE_ROLL,
    FEATURE_TX,
    FEATURE_TY,
    FEATURE_TZ,
    FEATURE_VERGENCE_X,
    FEATURE_VERGENCE_Y,
    FEATURE_YAW,
)

_EYE_A_FEAT_IDX_X = [
    FEATURE_A_DX,
    FEATURE_VERGENCE_X,
    FEATURE_YAW,
    FEATURE_ROLL,
    FEATURE_TZ,
    FEATURE_TX,
    FEATURE_A_IRIS_RADIUS,
    FEATURE_FACE_CX,
    FEATURE_FACE_SCALE,
    FEATURE_INTEROCULAR,
]
_EYE_A_FEAT_IDX_Y = [
    FEATURE_A_DY,
    FEATURE_A_EAR,
    FEATURE_A_UPPER_CLEAR,
    FEATURE_A_LOWER_CLEAR,
    FEATURE_PITCH,
    FEATURE_ROLL,
    FEATURE_TZ,
    FEATURE_TY,
    FEATURE_FACE_CY,
    FEATURE_FACE_SCALE,
]
_EYE_B_FEAT_IDX_X = [
    FEATURE_B_DX,
    FEATURE_VERGENCE_X,
    FEATURE_YAW,
    FEATURE_ROLL,
    FEATURE_TZ,
    FEATURE_TX,
    FEATURE_B_IRIS_RADIUS,
    FEATURE_FACE_CX,
    FEATURE_FACE_SCALE,
    FEATURE_INTEROCULAR,
]
_EYE_B_FEAT_IDX_Y = [
    FEATURE_B_DY,
    FEATURE_B_EAR,
    FEATURE_B_UPPER_CLEAR,
    FEATURE_B_LOWER_CLEAR,
    FEATURE_PITCH,
    FEATURE_ROLL,
    FEATURE_TZ,
    FEATURE_TY,
    FEATURE_FACE_CY,
    FEATURE_FACE_SCALE,
]
_BINOCULAR_FEAT_IDX_X = [
    FEATURE_A_DX,
    FEATURE_B_DX,
    FEATURE_AVG_DX,
    FEATURE_VERGENCE_X,
    FEATURE_YAW,
    FEATURE_ROLL,
    FEATURE_TZ,
    FEATURE_TX,
    FEATURE_FACE_CX,
    FEATURE_FACE_SCALE,
    FEATURE_INTEROCULAR,
]
_BINOCULAR_FEAT_IDX_Y = [
    FEATURE_A_DY,
    FEATURE_B_DY,
    FEATURE_AVG_DY,
    FEATURE_A_EAR,
    FEATURE_B_EAR,
    FEATURE_A_UPPER_CLEAR,
    FEATURE_A_LOWER_CLEAR,
    FEATURE_B_UPPER_CLEAR,
    FEATURE_B_LOWER_CLEAR,
    FEATURE_PITCH,
    FEATURE_ROLL,
    FEATURE_TZ,
    FEATURE_TY,
    FEATURE_VERGENCE_Y,
    FEATURE_FACE_CY,
    FEATURE_FACE_SCALE,
]


def _make_gp():
    kernel = (
        ConstantKernel(1.0, (1e-2, 1e3))
        * RBF(length_scale=1.0, length_scale_bounds=(1e-2, 1e2))
        + WhiteKernel(noise_level=5e-3, noise_level_bounds=(1e-6, 1e1))
    )
    return GaussianProcessRegressor(
        kernel=kernel,
        alpha=1e-6,
        normalize_y=True,
        n_restarts_optimizer=4,
    )


class _ScreenRegressor:
    def __init__(self, feat_idx_x, feat_idx_y=None):
        self.feat_idx_x = np.asarray(feat_idx_x, dtype=np.int32)
        self.feat_idx_y = np.asarray(
            feat_idx_x if feat_idx_y is None else feat_idx_y,
            dtype=np.int32,
        )
        self.scaler_x = StandardScaler()
        self.scaler_y = StandardScaler()
        self.gp_x = _make_gp()
        self.gp_y = _make_gp()

    def fit(self, X, Y):
        Xx = X[:, self.feat_idx_x]
        Xy = X[:, self.feat_idx_y]
        self.scaler_x.fit(Xx)
        self.scaler_y.fit(Xy)
        self.gp_x.fit(self.scaler_x.transform(Xx), Y[:, 0])
        self.gp_y.fit(self.scaler_y.transform(Xy), Y[:, 1])

    def predict(self, feat):
        x = self.scaler_x.transform(feat[self.feat_idx_x].reshape(1, -1))
        y = self.scaler_y.transform(feat[self.feat_idx_y].reshape(1, -1))
        mean_x, std_x = self.gp_x.predict(x, return_std=True)
        mean_y, std_y = self.gp_y.predict(y, return_std=True)
        mean = np.array([mean_x[0], mean_y[0]], dtype=np.float64)
        std = np.array([std_x[0], std_y[0]], dtype=np.float64)
        return mean, std


def _quality_weight(feat, ear_idx):
    ear = float(feat[ear_idx])
    return float(np.clip((ear - 0.12) / 0.18, 0.15, 1.0))


class GazeCalibrator:
    """Fuses binocular and per-eye regressors by inverse variance."""

    def __init__(self):
        self.eye_a = _ScreenRegressor(_EYE_A_FEAT_IDX_X, _EYE_A_FEAT_IDX_Y)
        self.eye_b = _ScreenRegressor(_EYE_B_FEAT_IDX_X, _EYE_B_FEAT_IDX_Y)
        self.binocular = _ScreenRegressor(_BINOCULAR_FEAT_IDX_X, _BINOCULAR_FEAT_IDX_Y)
        self._fitted = False

    def fit(self, X, Y):
        X = np.asarray(X, dtype=np.float64)
        Y = np.asarray(Y, dtype=np.float64)
        keep = np.all(np.isfinite(X), axis=1) & np.all(np.isfinite(Y), axis=1)
        X = X[keep]
        Y = Y[keep]
        self.eye_a.fit(X, Y)
        self.eye_b.fit(X, Y)
        self.binocular.fit(X, Y)
        self._fitted = True

    def predict(self, feat):
        pred, _ = self.predict_with_variance(feat)
        return pred

    def predict_with_variance(self, feat):
        if not self._fitted:
            raise RuntimeError("Calibrator has not been trained")
        feat = np.asarray(feat, dtype=np.float64)

        quality_a = _quality_weight(feat, FEATURE_A_EAR)
        quality_b = _quality_weight(feat, FEATURE_B_EAR)
        yaw = abs(float(feat[FEATURE_YAW])) / 0.9
        pitch = abs(float(feat[FEATURE_PITCH])) / 0.65
        pose_quality = float(np.clip(1.0 - 0.5 * (yaw + pitch), 0.25, 1.0))
        weights = [
            quality_a * pose_quality,
            quality_b * pose_quality,
            np.sqrt(quality_a * quality_b) * pose_quality,
        ]

        fused_num = np.zeros(2, dtype=np.float64)
        fused_den = np.zeros(2, dtype=np.float64)
        for model, quality in zip((self.eye_a, self.eye_b, self.binocular), weights):
            mean, std = model.predict(feat)
            var = np.maximum(std * std, 1e-6)
            w = quality / var
            fused_num += mean * w
            fused_den += w

        fused = fused_num / np.maximum(fused_den, 1e-9)
        fused_var = 1.0 / np.maximum(fused_den, 1e-9)
        return fused, fused_var
