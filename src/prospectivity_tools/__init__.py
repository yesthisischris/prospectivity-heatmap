"""Package initialization for prospectivity heatmap.

This package exposes configuration and pipeline functions for building a
geospatial prospectivity heatmap using H3 indexing. See individual modules
for details.
"""

# Import everything from submodules
from .config import settings
from .geospatial import add_distance_columns, build_grid, h3_to_geodataframe, polys_to_h3
from .ingest import add_lithology_flags, extract_rock_types
from .score import compute_likelihood
from .utils import df_more_info
from .viz import build_static_map

# Define what gets imported when using `from prospectivity_tools import *`
__all__ = [
    "settings",
    "add_distance_columns",
    "polys_to_h3",
    "build_grid",
    "h3_to_geodataframe",
    "extract_rock_types",
    "add_lithology_flags",
    "compute_likelihood",
    "build_static_map",
    "df_more_info",
]
