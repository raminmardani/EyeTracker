"""One Euro filter — scale-adaptive smoothing for noisy streams.

Heavy smoothing when the signal is still, low latency when it moves fast.
Reference: Casiez, Roussel & Vogel, CHI 2012.
"""
import math
import time

import numpy as np


def _alpha(cutoff, dt):
    tau = 1.0 / (2.0 * math.pi * cutoff)
    return 1.0 / (1.0 + tau / dt)


class _OneEuro1D:
    def __init__(self, min_cutoff=1.0, beta=0.0, d_cutoff=1.0):
        self.min_cutoff = float(min_cutoff)
        self.beta = float(beta)
        self.d_cutoff = float(d_cutoff)
        self._x = None
        self._dx = 0.0
        self._t = None

    def __call__(self, x, t, cutoff_scale=1.0):
        if self._t is None:
            self._t, self._x = t, x
            return x
        dt = max(t - self._t, 1e-3)
        dx_raw = (x - self._x) / dt
        a_d = _alpha(self.d_cutoff, dt)
        dx_hat = a_d * dx_raw + (1.0 - a_d) * self._dx
        cutoff = (self.min_cutoff + self.beta * abs(dx_hat)) * cutoff_scale
        a = _alpha(max(cutoff, 1e-3), dt)
        x_hat = a * x + (1.0 - a) * self._x
        self._x, self._dx, self._t = x_hat, dx_hat, t
        return x_hat


class OneEuro2D:
    """2-D filter with optional per-sample variance input from the predictor."""

    def __init__(self, min_cutoff=1.0, beta=0.007, d_cutoff=1.0,
                 variance_scale=50.0):
        self._fx = _OneEuro1D(min_cutoff, beta, d_cutoff)
        self._fy = _OneEuro1D(min_cutoff, beta, d_cutoff)
        self._var_scale = float(variance_scale)

    def filter(self, x, y, variance=None, t=None):
        if t is None:
            t = time.monotonic()
        # Higher predictor variance -> smaller cutoff scale -> more smoothing.
        scale = 1.0
        if variance is not None:
            var = float(np.mean(np.maximum(np.asarray(variance, dtype=np.float64), 0.0)))
            if var > 0.0:
                scale = 1.0 / (1.0 + math.sqrt(var) / self._var_scale)
        fx = self._fx(x, t, cutoff_scale=scale)
        fy = self._fy(y, t, cutoff_scale=scale)
        return fx, fy
