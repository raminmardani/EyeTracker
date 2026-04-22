"""Dual-eye Gaussian-Process calibration from gaze features to screen coords."""
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel
from sklearn.preprocessing import StandardScaler

# Feature layout is defined in gaze.py:
#   0 adx  1 ady  2 bdx  3 bdy  4 avg_dx  5 avg_dy
#   6 aear 7 bear 8 yaw  9 pitch 10 roll 11 tz
# Each eye's regressor sees only that eye's iris ratios + shared head pose.
_EYE_A_FEAT_IDX = [0, 1, 6, 8, 9, 10, 11]
_EYE_B_FEAT_IDX = [2, 3, 7, 8, 9, 10, 11]


def _make_gp():
    kernel = (
        ConstantKernel(1.0, (1e-3, 1e3))
        * RBF(length_scale=1.0, length_scale_bounds=(1e-2, 1e2))
        + WhiteKernel(noise_level=1e-2, noise_level_bounds=(1e-6, 1e1))
    )
    return GaussianProcessRegressor(
        kernel=kernel,
        alpha=1e-6,
        normalize_y=True,
        n_restarts_optimizer=3,
    )


class _EyeRegressor:
    def __init__(self, feat_idx):
        self.feat_idx = feat_idx
        self.scaler = StandardScaler()
        self.gp = _make_gp()

    def fit(self, X, Y):
        Xs = X[:, self.feat_idx]
        self.scaler.fit(Xs)
        self.gp.fit(self.scaler.transform(Xs), Y)

    def predict(self, feat):
        x = self.scaler.transform(feat[self.feat_idx].reshape(1, -1))
        mean, std = self.gp.predict(x, return_std=True)
        mean = np.asarray(mean[0], dtype=np.float64)
        std = np.asarray(std[0], dtype=np.float64)
        if std.ndim == 0:
            std = np.full(mean.shape, float(std), dtype=np.float64)
        return mean, std


class GazeCalibrator:
    """Fits one GP per eye, fuses predictions by inverse-variance weighting."""

    def __init__(self):
        self.eye_a = _EyeRegressor(_EYE_A_FEAT_IDX)
        self.eye_b = _EyeRegressor(_EYE_B_FEAT_IDX)
        self._fitted = False

    def fit(self, X, Y):
        X = np.asarray(X, dtype=np.float64)
        Y = np.asarray(Y, dtype=np.float64)
        self.eye_a.fit(X, Y)
        self.eye_b.fit(X, Y)
        self._fitted = True

    def predict(self, feat):
        pred, _ = self.predict_with_variance(feat)
        return pred

    def predict_with_variance(self, feat):
        if not self._fitted:
            raise RuntimeError("Calibrator has not been trained")
        feat = np.asarray(feat, dtype=np.float64)
        mean_a, std_a = self.eye_a.predict(feat)
        mean_b, std_b = self.eye_b.predict(feat)
        var_a = np.maximum(std_a * std_a, 1e-6)
        var_b = np.maximum(std_b * std_b, 1e-6)
        w_a, w_b = 1.0 / var_a, 1.0 / var_b
        fused = (mean_a * w_a + mean_b * w_b) / (w_a + w_b)
        fused_var = 1.0 / (w_a + w_b)
        return fused, fused_var
