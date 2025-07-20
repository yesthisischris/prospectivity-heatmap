"""H3 indexing functions.

Convert vector polygons into H3 cell identifiers and construct the
combined grid used for distance calculations. H3 provides a compact
representation of hexagonal cells that is amenable to fast spatial
operations and efficient storage.
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd
from h3ronpy import arrowvector as h3av

from .config import settings

CACHE_DIR = Path("__cache__")


def polys_to_h3(gdf: gpd.GeoDataFrame, tag: str) -> pd.Series:
    """Return unique H3 cells intersecting the given polygons.

    Results are cached per ``tag`` in ``__cache__/`` so reruns with a
    fixed resolution are instantaneous.
    """
    CACHE_DIR.mkdir(exist_ok=True)
    res = settings.grid["resolution"]
    cache_file = CACHE_DIR / f"{tag}_r{res}.feather"
    if cache_file.exists():
        return pd.read_feather(cache_file)["h3_id"]

    cell_ids = h3av.polygon_to_cells(gdf.geometry.values, res)
    series = pd.Series(cell_ids.unique(), name="h3_id")
    series.to_frame().to_feather(cache_file)
    return series


def build_grid(rock_a: gpd.GeoDataFrame, rock_b: gpd.GeoDataFrame) -> pd.DataFrame:
    """Construct a unified H3 grid covering both rock types.

    Parameters
    ----------
    rock_a, rock_b:
        GeoDataFrames containing polygons for each rock type.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with a single ``h3_id`` column listing all unique
        hexagon IDs that intersect either rock type. Duplicate IDs are
        removed.
    """
    a_cells = polys_to_h3(rock_a, "a")
    b_cells = polys_to_h3(rock_b, "b")
    grid = pd.DataFrame({"h3_id": pd.concat([a_cells, b_cells]).unique()})
    return grid
