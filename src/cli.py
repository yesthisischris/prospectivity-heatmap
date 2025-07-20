"""Command-line interface for running the prospectivity pipeline."""

from __future__ import annotations

import click

from .ingest import load_bedrock
from .index_h3 import build_grid
from .distance import add_distance_columns
from .score import compute_likelihood
from .persist import write_parquet
from .viz import build_map
from .config import settings


@click.command()
def main() -> None:
    """Run the full prospectivity workflow.

    This CLI reads the configured dataset, builds the H3 grid, computes
    distances to rock boundaries, converts those distances into scores,
    writes the results to disk and finally produces an interactive map.
    """
    # Load rock polygons
    rock_a, rock_b = load_bedrock()
    # Build the hexagon grid covering both rock types
    grid = build_grid(rock_a, rock_b)
    # Compute distances to each rock type
    grid = add_distance_columns(grid, rock_a, rock_b, crs=settings.crs)
    # Calculate likelihood scores using the Gaussian kernel
    scored = compute_likelihood(grid)
    # Persist results
    out_path = write_parquet(scored)
    click.echo(f"Wrote {len(scored)} H3 cells to {out_path}")
    # Create an interactive map
    html_path = build_map(scored)
    click.echo(f"Saved interactive map to {html_path}")


if __name__ == "__main__":
    main()
