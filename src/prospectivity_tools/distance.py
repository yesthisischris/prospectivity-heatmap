"""Distance calculations between H3 cell centroids and polygons.

Distances are measured from each hexagon centroid to the nearest polygon
boundary for both rock types. Results are expressed in the same units as
the configured CRS (metres for UTM zones). Shapely's vectorised distance
operations provide fast SIMD implementations.
"""

from __future__ import annotations

import geopandas as gpd

# `h3ronpy` no longer exposes the basic H3 API. Use the standalone `h3`
# package for geo conversions.
import h3
import pandas as pd
from shapely.geometry import Point


def _centroid_to_point(h3_id: int) -> Point:
    """Convert an H3 cell ID to a Shapely point (WGS84)."""
    lat, lon = h3.h3_to_geo(h3_id)
    return Point(lon, lat)


def add_distance_columns(
    grid: pd.DataFrame,
    rock_a: gpd.GeoDataFrame,
    rock_b: gpd.GeoDataFrame,
    crs: str,
) -> gpd.GeoDataFrame:
    """Attach distance-to-rock columns to the grid.

    Parameters
    ----------
    grid:
        DataFrame with a column ``h3_id``.
    rock_a, rock_b:
        GeoDataFrames containing polygons for each rock type.
    crs:
        Target coordinate reference system for distance measurements.

    Returns
    -------
    GeoDataFrame
        A copy of the input grid with new columns ``dist_a`` and
        ``dist_b`` containing distances (in the CRS units) to the
        nearest polygon of each rock type.
    """
    # Copy to avoid mutating caller state
    grid = grid.copy()
    # Convert hexagon centroids to WGS84 points and then to target CRS
    grid["geometry"] = grid["h3_id"].apply(_centroid_to_point)
    ggrid = gpd.GeoDataFrame(grid, geometry="geometry", crs="EPSG:4326").to_crs(crs)

    # Vectorised distance from each point to the nearest polygon of each type
    ggrid["dist_a"] = ggrid.geometry.distance(rock_a.unary_union)
    ggrid["dist_b"] = ggrid.geometry.distance(rock_b.unary_union)

    return ggrid
