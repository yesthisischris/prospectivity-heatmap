"""Basic unit tests for the scoring functions."""

import numpy as np
import pandas as pd

from prospectivity_tools.score import compute_likelihood, gaussian, weighted_and


def test_gaussian_at_zero_distance():
    """Test that gaussian returns 1.0 at distance 0."""
    d = np.array([0.0])
    d0_m = 1000.0
    result = gaussian(d, d0_m)
    assert np.isclose(result[0], 1.0)


def test_weighted_and_equal_weights():
    """Test weighted_and with equal weights."""
    mu_a = np.array([0.8])
    mu_b = np.array([0.6])
    w_a = 0.5
    result = weighted_and(mu_a, mu_b, w_a)
    expected = (0.8**0.5) * (0.6**0.5)
    assert np.isclose(result[0], expected)


def test_compute_likelihood_structure():
    """Test that compute_likelihood returns the correct structure."""
    df = pd.DataFrame(
        {
            "h3_id": ["test_cell"],
            "dist_a": [0.0],
            "dist_b": [0.0],
            "intersects_a": [True],
            "intersects_b": [True],
        }
    )
    result = compute_likelihood(df)
    expected_columns = ["h3_id", "intersects_a", "intersects_b", "score"]
    assert list(result.columns) == expected_columns
