"""Unit tests for the scoring functions."""

import numpy as np

from src.score import gaussian


def test_gaussian_kernel() -> None:
    """Verify the Gaussian kernel returns expected values at key points."""
    # At zero distance the score should be exactly one
    assert gaussian(0, 1000) == 1
    # At the decay distance d0 the score should be exp(-1)
    assert np.isclose(gaussian(1000, 1000), np.exp(-1))
