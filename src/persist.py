"""Persist prospectivity scores to storage.

This module provides functions for writing the scored hexagon table
to a Parquet file on disk. Parquet is chosen for its efficient
columnar storage and compatibility with cloud analytics engines.
"""

from pathlib import Path
from typing import Optional

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from .config import settings


def write_parquet(df: pd.DataFrame, output_path: Optional[Path] = None) -> Path:
    """Write DataFrame of prospectivity scores to a Parquet file.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with at least columns ``h3_id`` and ``score``.
    output_path : pathlib.Path, optional
        Destination path. If not provided, the path from the config
        (`settings.paths["parquet"]`) is used.

    Returns
    -------
    pathlib.Path
        The resolved path where the Parquet file was written.
    """
    # Determine output path, defaulting to configured location
    path = Path(output_path) if output_path is not None else Path(settings.paths["parquet"])
    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    # Convert to Arrow table and write with compression
    table = pa.Table.from_pandas(df)
    pq.write_table(table, path, compression="zstd")
    return path
