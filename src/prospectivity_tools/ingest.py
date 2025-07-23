"""Data ingestion helpers.

This module contains logic to read the input GeoPackage and extract
subsets corresponding to the two rock types defined in the configuration.
The output is returned as a pair of GeoDataFrames in a consistent CRS.
"""

from __future__ import annotations

import geopandas as gpd

from .config import settings


def load_bedrock() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Load the bedrock GeoPackage and filter by rock type.

    The path to the GeoPackage and the CRS are taken from the
    configuration. Rock type names are matched case‑insensitively.

    Returns
    -------
    (GeoDataFrame, GeoDataFrame)
        Two GeoDataFrames containing polygons for the selected rock types.

    Raises
    ------
    ValueError
        If either of the requested rock types cannot be found in the
        dataset.
    """
    # Read the dataset with Pyogrio for faster I/O and reproject to the configured CRS
    gdf = gpd.read_file(settings.paths["input_gpkg"], engine="pyogrio").to_crs(settings.crs)

    # Filter by rock type names (case‑insensitive). Some datasets may use
    # different casing; ``na=False`` avoids matching NaN values.
    rock_a = gdf[gdf["ROCKTYPE"].str.contains(settings.rock_a, case=False, na=False)]
    rock_b = gdf[gdf["ROCKTYPE"].str.contains(settings.rock_b, case=False, na=False)]

    if rock_a.empty or rock_b.empty:
        missing = []
        if rock_a.empty:
            missing.append(settings.rock_a)
        if rock_b.empty:
            missing.append(settings.rock_b)
        raise ValueError(f"Requested rock types not found: {', '.join(missing)}")

    return rock_a, rock_b
