"""H3 indexing functions.

Convert vector polygons into H3 cell identifiers and construct the
combined grid used for distance calculations. H3 provides a compact
representation of hexagonal cells that is amenable to fast spatial
operations and efficient storage.
"""

from __future__ import annotations

import geopandas as gpd
import pandas as pd
from h3ronpy import arrowvector as h3av

from .config import settings


def polys_to_h3(gdf: gpd.GeoDataFrame) -> pd.Series:
    """Return unique H3 cells intersecting the given polygons.

    Uses the resolution defined in the configuration. The return value
    is a pandas Series of 64 bit integers (H3 IDs) with the name
    ``h3_id``.
    """
    res = settings.grid["resolution"]
    # h3ronpy returns a 1D numpy array of cell IDs for each polygon.
    cell_ids = h3av.polygon_to_cells(gdf.geometry.values, res)
    return pd.Series(cell_ids.unique(), name="h3_id")


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
    a_cells = polys_to_h3(rock_a)
    b_cells = polys_to_h3(rock_b)
    grid = pd.DataFrame({"h3_id": pd.concat([a_cells, b_cells]).unique()})
    return grid
