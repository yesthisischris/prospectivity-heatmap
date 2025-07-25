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


def weighted_and(mu_a: np.ndarray, mu_b: np.ndarray, w_a: float) -> np.ndarray:
    """
    Weighted geometric AND.

    Parameters
    ----------
    mu_a, mu_b : np.ndarray
        Membership values (0–1) for rock types A and B.
    w_a : float
        Relative importance of rock type A.

    Returns
    -------
    np.ndarray
        Combined membership (0–1).
    """
    w_a = float(np.clip(w_a, 0.0, 1.0))
    w_b = 1.0 - w_a
    return (mu_a ** w_a) * (mu_b ** w_b)


def compute_likelihood(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute prospectivity score for each H3 cell using a weighted fuzzy‑AND.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing columns `h3_id`, `dist_a`, `dist_b`, 
        `intersects_a`, and `intersects_b`.

    Returns
    -------
    pandas.DataFrame
        DataFrame with columns `h3_id`, `score`, `intersects_a`, and `intersects_b`.
    """
    d0_m = settings.falloff_km * 1_000

    # Convert distances to fuzzy memberships
    mu_a = gaussian(df["dist_a"].to_numpy(), d0_m, settings.alpha)
    mu_b = gaussian(df["dist_b"].to_numpy(), d0_m, settings.alpha)

    # Combine with weighted AND
    score = weighted_and(mu_a, mu_b, settings.weight_a)

    # Package result
    out = df[["h3_id", "intersects_a", "intersects_b"]].copy()
    out["score"] = score
    return out
