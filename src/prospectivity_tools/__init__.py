"""Package initialization for prospectivity heatmap.

This package exposes configuration and pipeline functions for building a
geospatial prospectivity heatmap using H3 indexing. See individual modules
for details.
"""

# Import everything from submodules
from .config import settings
from .geospatial import add_distance_columns, polys_to_h3, build_grid, h3_to_geodataframe
from .ingest import extract_rock_types, add_lithology_flags
from .score import compute_likelihood
from .viz import build_static_map
from .utils import df_more_info

# Define what gets imported when using `from prospectivity_tools import *`
__all__ = [
    'settings',
    'add_distance_columns',
    'polys_to_h3',
    'build_grid',
    'h3_to_geodataframe',
    'extract_rock_types',
    'add_lithology_flags',
    'compute_likelihood',
    'build_static_map',
    'df_more_info'
]