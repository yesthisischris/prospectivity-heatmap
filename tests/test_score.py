"""Unit tests for the scoring functions."""

import numpy as np
import pytest

from prospectivity_tools.score import gaussian, linear


@pytest.mark.parametrize("kernel", [gaussian, linear])
def test_kernels(kernel) -> None:
    """Verify kernels return expected values at key points."""
    # At zero distance the score should be exactly one
    assert kernel(0, 1000) == 1
    # At the decay distance d0 the score should be exp(-1) for Gaussian and 0 for linear
    expected = np.exp(-1) if kernel is gaussian else 0
    assert np.isclose(kernel(1000, 1000), expected)
