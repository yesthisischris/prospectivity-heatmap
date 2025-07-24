"""Compute prospectivity score from distances using a Gaussian kernel.

This module defines functions to convert distances to a likelihood score
between 0 and 1. The Gaussian fall‑off is controlled by the
`falloff_km` parameter in the configuration. The score for each cell
is based on the nearest distance to either rock type.
"""

import numpy as np
import pandas as pd

from .config import settings


def gaussian(d: np.ndarray, d0_m: float, alpha: float = 2.0) -> np.ndarray:
    """Return Gaussian kernel values for distances (in metres) and scale.

    The Gaussian kernel is defined as exp(-(d/d0)^alpha). At distance zero
    the value is 1 and at distance d0 it is e^-1.

    Parameters
    ----------
    d : numpy.ndarray
        Distances in metres.
    d0_m : float
        Fall-off distance in metres (corresponds to `falloff_km` in config).
    alpha : float
        Shape factor controlling the steepness of the fall-off.

    Returns
    -------
    numpy.ndarray
        Array of scores between 0 and 1.
    """
    return np.exp(-((d / d0_m) ** alpha))


def linear(d: np.ndarray, d0_m: float) -> np.ndarray:
    """Return linear decay kernel clipped to 0."""
    return np.clip(1 - (d / d0_m), 0, 1)


def compute_likelihood(df: pd.DataFrame) -> pd.DataFrame:
    """Compute prospectivity score for each H3 cell.

    Computes prospectivity based on proximity to BOTH rock types.
    High scores indicate areas where both serpentinite and granodiorite
    are close (potential contact zones for cobalt mineralization).

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing columns `h3_id`, `dist_a`, `dist_b`, 
        `intersects_a`, and `intersects_b`.

    Returns
    -------
    pandas.DataFrame
        DataFrame with columns `h3_id`, `score`, and `intersects_both`.
    """
    d0_m = settings.falloff_km * 1_000
    
    # Calculate individual proximity scores for each rock type
    score_a = gaussian(df["dist_a"].to_numpy(), d0_m, settings.alpha)
    score_b = gaussian(df["dist_b"].to_numpy(), d0_m, settings.alpha)
    
    # Multiply scores - both rock types must be close for high score
    # This emphasizes contact zones/interfaces
    df = df.copy()
    df["score"] = score_a * score_b
    
    return df[["h3_id", "score", "intersects_a", "intersects_b"]]
