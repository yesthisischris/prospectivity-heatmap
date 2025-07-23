"""Package initialisation for prospectivity heatmap.

This package exposes configuration and pipeline functions for building a
geospatial prospectivity heatmap using H3 indexing. See individual modules
for details.
"""

from . import cli, config, distance, ingest, persist, score, viz

# ``index_h3`` requires optional binary dependencies from ``h3ronpy``. To
# avoid import errors when those are not available (e.g. during basic unit
# tests) it is imported lazily when needed by the CLI.

__all__ = ['config', 'score', 'viz', 'distance', 'ingest', 'persist', 'cli']
