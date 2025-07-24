"""Package initialization for prospectivity heatmap.

This package exposes configuration and pipeline functions for building a
geospatial prospectivity heatmap using H3 indexing. See individual modules
for details.
"""

# Import everything from submodules
from .config import settings
from .distance import add_distance_columns
from .ingest import load_bedrock
from .persist import write_parquet
from .score import compute_likelihood
from .viz import build_map
from .index_h3 import polys_to_h3, build_grid
from .utils import df_more_info

# Define what gets imported when using `from prospectivity_tools import *`
__all__ = [
    'settings',
    'add_distance_columns',
    'load_bedrock',
    'write_parquet',
    'compute_likelihood',
    'build_map',
    'utils'
]