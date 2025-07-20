"""Distance calculations between H3 cell centroids and polygons.

Distances are measured from each hexagon centroid to the nearest polygon
boundary for both rock types. Results are expressed in the same units as
the configured CRS (metres for UTM zones). A spatial index (STRtree) is
used for efficient nearest neighbour queries.
"""

from __future__ import annotations

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shapely.strtree import STRtree
from h3ronpy import h3


def _build_tree(geoms) -> STRtree:
    """Build a spatial index over the provided geometries."""
    return STRtree(geoms)


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

    # Build spatial indexes and compute nearest distance for each point
    for tag, geoms in [("a", rock_a.geometry), ("b", rock_b.geometry)]:
        tree = _build_tree(geoms)
        # shapely STRtree returns an index into geoms; nearest() accepts a geometry
        ggrid[f"dist_{tag}"] = ggrid.geometry.apply(
            lambda p: tree.nearest(p).distance(p)
        )

    return ggrid
