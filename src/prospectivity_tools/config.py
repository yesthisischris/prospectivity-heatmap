"""Configuration loader and settings model.

All runtime configuration parameters are stored in ``config.yaml``. This
module provides a Pydantic ``Settings`` model along with a ``load_config``
function that reads the YAML file and validates the contents. A module
level ``settings`` object is instantiated for convenience so other
modules can import it directly.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Union

import yaml
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Pydantic model describing the configuration schema.

    Fields map directly to keys in ``config.yaml``. Validation ensures
    required keys are present and sensible (e.g. ``falloff_km`` is
    positive). Additional keys are allowed in the ``grid`` and ``paths``
    dictionaries to accommodate future extensions.
    """

    crs: str
    rock_a: str
    rock_b: str
    falloff_km: float = Field(gt=0, description="Kernel fall‑off distance in km")
    alpha: float = Field(gt=0, description="Gaussian shape factor for fall-off steepness")
    grid: Dict[str, Any]
    paths: Dict[str, str]
    weight_a: float = Field(ge=0, le=1, description="Weight for rock type A in scoring")


def load_config(path: Union[str, Path] = "config.yaml") -> Settings:
    """Load and validate the configuration file.

    Parameters
    ----------
    path:
        Path to the YAML configuration file. Defaults to ``config.yaml``
        in the project root.

    Returns
    -------
    Settings
        A validated configuration object.
    """
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return Settings(**cfg)


# Expose a singleton settings object that other modules can import.
settings: Settings = load_config()
