"""Compute prospectivity score from distances using a Gaussian kernel.

This module defines functions to convert distances to a likelihood score
between 0 and 1. The Gaussian fall‑off is controlled by the
`falloff_km` parameter in the configuration. The score for each cell
is based on the nearest distance to either rock type.
"""

import numpy as np
import pandas as pd

from .config import settings

def gaussian(d: np.ndarray, d0_m: float) -> np.ndarray:
    """Return Gaussian kernel values for distances (in metres) and scale.

    The Gaussian kernel is defined as exp(-(d/d0)^2). At distance zero
    the value is 1 and at distance d0 it is e^-1.

    Parameters
    ----------
    d : numpy.ndarray
        Distances in metres.
    d0_m : float
        Fall-off distance in metres (corresponds to `falloff_km` in config).

    Returns
    -------
    numpy.ndarray
        Array of scores between 0 and 1.
    """
    return np.exp(-((d / d0_m) ** 2))


def compute_likelihood(df: pd.DataFrame) -> pd.DataFrame:
    """Compute prospectivity score for each H3 cell.

    Computes the nearest distance to either rock type and applies the
    Gaussian fall-off to produce a prospectivity score. Returns a
    DataFrame with the H3 ID and score columns.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing columns `h3_id`, `dist_a`, and `dist_b`.

    Returns
    -------
    pandas.DataFrame
        DataFrame with columns `h3_id` and `score`.
    """
    d0_m = settings.falloff_km * 1_000
    # compute nearest distance to either rock type
    nearest = np.minimum(df["dist_a"].to_numpy(), df["dist_b"].to_numpy())
    df = df.copy()
    df["score"] = gaussian(nearest, d0_m)
    return df[["h3_id", "score"]]
