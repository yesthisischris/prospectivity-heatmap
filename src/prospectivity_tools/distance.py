"""Distance calculations between H3 cell centroids and polygons.

Distances are measured from each hexagon centroid to the nearest polygon
boundary for both rock types. Results are expressed in metres using H3's
native distance calculations. This approach scales to millions of cells
without external geospatial libraries.
"""

from __future__ import annotations

import math
from collections import deque

import h3
import pandas as pd


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