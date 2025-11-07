"""
Overlay_dx: Visual and quantitative metric for time series forecasting evaluation.

This package provides the overlay_dx metric for evaluating time series forecasts.
The metric combines visual interpretability with quantitative assessment by measuring
the alignment between predictions and actual values across different tolerance thresholds.

Example:
    >>> from overlay_dx import overlay_dx_score
    >>> import numpy as np
    >>> y_true = np.array([1, 2, 3, 4, 5])
    >>> y_pred = np.array([1.1, 2.1, 2.9, 4.1, 5.1])
    >>> score = overlay_dx_score(y_true, y_pred)
    >>> print(f"Overlay_dx score: {score:.3f}")

For more examples, see: https://github.com/Smile-SA/overlay_dx
"""

from ._version import __version__
from .metrics import (
    overlay_dx_score,
    make_overlay_dx_scorer,
    OVERLAY_DX_SCORER,
    OVERLAY_DX_SCORER_FINE,
    OVERLAY_DX_SCORER_COARSE,
    Evaluate,
)

__all__ = [
    "__version__",
    "overlay_dx_score",
    "make_overlay_dx_scorer",
    "OVERLAY_DX_SCORER",
    "OVERLAY_DX_SCORER_FINE",
    "OVERLAY_DX_SCORER_COARSE",
    "Evaluate",
]
