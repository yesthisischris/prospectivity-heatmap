"""Data ingestion helpers.

This module contains logic to extract subsets corresponding to the two
rock types defined in the configuration. The input GeoDataFrame is filtered
based on column names specified in the configuration, where values are 0 or 1.
The output is returned as a pair of GeoDataFrames in a consistent CRS.
"""

from __future__ import annotations

from typing import Tuple

import geopandas as gpd

from .config import settings


def load_bedrock(gdf: gpd.GeoDataFrame) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Filter the input GeoDataFrame by rock type columns.

    The column names for the rock types are taken from the configuration.
    Values in these columns are expected to be 0 or 1.

    Parameters
    ----------
    gdf : GeoDataFrame
        Input GeoDataFrame containing the rock type columns.

    Returns
    -------
    (GeoDataFrame, GeoDataFrame)
        Two GeoDataFrames containing polygons for the selected rock types.

    Raises
    ------
    ValueError
        If either of the requested rock type columns cannot be found in the
        dataset or if no rows match the criteria.
    """
    # Ensure the required columns exist in the GeoDataFrame
    if settings.rock_a not in gdf.columns or settings.rock_b not in gdf.columns:
        missing_columns = [
            col for col in [settings.rock_a, settings.rock_b] if col not in gdf.columns
        ]
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    # Filter rows where the rock type columns have a value of 1
    rock_a = gdf[gdf[settings.rock_a] == 1]
    rock_b = gdf[gdf[settings.rock_b] == 1]

    if rock_a.empty or rock_b.empty:
        missing = []
        if rock_a.empty:
            missing.append(settings.rock_a)
        if rock_b.empty:
            missing.append(settings.rock_b)
        raise ValueError(f"No rows found for rock types: {', '.join(missing)}")

    return rock_a, rock_b