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
import h3

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

    # Convert to WGS84 if not already in geographic coordinates (h3 requirement)
    if not gdf.crs.is_geographic:
        gdf_wgs84 = gdf.to_crs("EPSG:4326")  # WGS84
    else:
        gdf_wgs84 = gdf

    # Convert polygons to H3 cells using h3.polyfill_geojson
    cell_ids = []
    for geom in gdf_wgs84.geometry:
        if geom.is_valid:
            # Convert shapely geometry to GeoJSON format for h3.polyfill_geojson
            if geom.geom_type == 'Polygon':
                # Extract exterior coordinates as (lng, lat) tuples for GeoJSON format
                coords = [(lng, lat) for lng, lat in geom.exterior.coords]  # Keep all coordinates including the closing one
                geojson_poly = {
                    "type": "Polygon",
                    "coordinates": [coords]
                }
                cell_ids.extend(h3.polyfill_geojson(geojson_poly, res))
            elif geom.geom_type == 'MultiPolygon':
                # Handle MultiPolygon geometries
                for poly in geom.geoms:
                    coords = [(lng, lat) for lng, lat in poly.exterior.coords]  # Keep all coordinates including the closing one
                    geojson_poly = {
                        "type": "Polygon", 
                        "coordinates": [coords]
                    }
                    cell_ids.extend(h3.polyfill_geojson(geojson_poly, res))

    series = pd.Series(pd.unique(cell_ids), name="h3_id")
    series.to_frame().to_feather(cache_file)
    return series


def build_grid(rock_a: gpd.GeoDataFrame, rock_b: gpd.GeoDataFrame, bounds=None) -> pd.DataFrame:
    """Construct a unified H3 grid covering both rock types.

    Parameters
    ----------
    rock_a, rock_b:
        GeoDataFrames containing polygons for each rock type.
    bounds:
        Optional bounds as [west, south, east, north] in WGS84 coordinates.
        If None, uses the combined bounds of both rock types.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with columns ``h3_id``, ``intersects_a``, and ``intersects_b``.
        ``intersects_a`` and ``intersects_b`` are boolean columns indicating
        whether each hexagon intersects ``rock_a`` and ``rock_b``, respectively.
    """
    if bounds is None:
        # Combine both rock types into a single GeoDataFrame
        combined = gpd.GeoDataFrame(pd.concat([rock_a, rock_b], ignore_index=True))
        
        # Convert to WGS84 to get bounds in the right coordinate system
        if not combined.crs.is_geographic:
            combined_wgs84 = combined.to_crs("EPSG:4326")
        else:
            combined_wgs84 = combined
            
        # Get bounds in WGS84 [minx, miny, maxx, maxy]
        bounds = combined_wgs84.total_bounds
    
    # Generate hexagons covering the bounding box
    res = settings.grid["resolution"]
    hexagons = h3.polyfill_geojson(
        {
            "type": "Polygon",
            "coordinates": [
                [
                    [bounds[0], bounds[1]],  # Bottom-left (west, south)
                    [bounds[0], bounds[3]],  # Top-left (west, north)
                    [bounds[2], bounds[3]],  # Top-right (east, north)
                    [bounds[2], bounds[1]],  # Bottom-right (east, south)
                    [bounds[0], bounds[1]],  # Closing the loop
                ]
            ],
        },
        res,
    )

    # Convert hexagons to a DataFrame
    all_cells = pd.Series(list(hexagons), name="h3_id", dtype=str)

    # Determine intersection flags
    a_cells = polys_to_h3(rock_a, "a")
    b_cells = polys_to_h3(rock_b, "b")
    grid = pd.DataFrame({
        "h3_id": all_cells,
        "intersects_a": all_cells.isin(a_cells),
        "intersects_b": all_cells.isin(b_cells),
    })

    return grid