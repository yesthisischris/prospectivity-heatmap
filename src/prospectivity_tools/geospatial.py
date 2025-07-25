from __future__ import annotations

import math
from collections import deque
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


def hex_step_distances(sources, allowed_cells=None):
    """
    Multi-source breadth-first search on the H3 grid.
    
    Parameters
    ----------
    sources : iterable
        H3 indices where distance = 0
    allowed_cells : set, optional
        Set that limits expansion to your grid (useful if clipped beforehand)
        
    Returns
    -------
    dict
        Mapping {cell: steps_from_nearest_source}
    """
    allowed = set(allowed_cells) if allowed_cells is not None else None
    dist = {h: 0 for h in sources}
    q = deque(sources)

    while q:
        h = q.popleft()
        d = dist[h]
        for nb in h3.k_ring(h, 1):            # neighbours share an edge
            if allowed and nb not in allowed:  # skip cells outside your grid
                continue
            if nb not in dist:                 # first time we visit -> shortest
                dist[nb] = d + 1
                q.append(nb)
    return dist


def add_distance_columns(
    grid: pd.DataFrame,
) -> pd.DataFrame:
    """Attach distance-to-rock columns to the grid using H3-native calculations.

    Parameters
    ----------
    grid:
        DataFrame with columns ``h3_id``, ``intersects_a``, and ``intersects_b``.

    Returns
    -------
    DataFrame
        A copy of the input grid with new columns ``dist_a`` and
        ``dist_b`` containing distances in metres to the nearest
        polygon of each rock type.
    """
    # Copy to avoid mutating caller state
    df = grid.copy()
    
    # Check if grid is empty
    if df.empty:
        print("Warning: Grid is empty, returning empty DataFrame")
        return df
    
    # Set H3 index for efficient lookups
    df = df.set_index("h3_id", drop=False)
    
    # Get sources for each rock type
    sources_a = df.index[df["intersects_a"]].tolist()
    sources_b = df.index[df["intersects_b"]].tolist()
    grid_cells = set(df.index)
    
    # Compute hex step distances using multi-source BFS
    steps_a = hex_step_distances(sources_a, allowed_cells=grid_cells)
    steps_b = hex_step_distances(sources_b, allowed_cells=grid_cells)
    
    # Convert hex steps to metres
    res = h3.h3_get_resolution(df.index[0])
    edge_m = h3.edge_length(res, "m")
    step_m = edge_m * math.sqrt(3)  # centre-to-centre distance
    
    # Attach distances to the DataFrame
    df["dist_a"] = df.index.map(lambda h: steps_a.get(h, math.nan) * step_m)
    df["dist_b"] = df.index.map(lambda h: steps_b.get(h, math.nan) * step_m)
    
    # Reset index to match original structure
    df = df.reset_index(drop=True)
    
    return df


def h3_to_geodataframe(df: pd.DataFrame, h3_column: str = "h3_id", 
                      target_crs: str | None = None) -> gpd.GeoDataFrame:
    """Convert DataFrame with H3 IDs to GeoDataFrame with polygon geometries.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing H3 cell IDs
    h3_column : str
        Name of column containing H3 cell IDs (default: "h3_id")
    target_crs : str, optional
        Target CRS to transform to. If None, uses settings.crs
        
    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame with H3 polygons as geometry column
    """
    from shapely.geometry import Polygon
    
    if target_crs is None:
        target_crs = settings.crs
    
    # Create geometries from H3 IDs
    geometries = []
    for h3_id in df[h3_column]:
        try:
            boundary = h3.h3_to_geo_boundary(h3_id, geo_json=True)
            poly = Polygon(boundary)
            geometries.append(poly)
        except Exception:
            geometries.append(None)
    
    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry=geometries, crs="EPSG:4326")
    
    # Convert to target CRS
    if target_crs != "EPSG:4326":
        gdf = gdf.to_crs(target_crs)
    
    return gdf
