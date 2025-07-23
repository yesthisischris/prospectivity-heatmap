"""Command-line interface for running the prospectivity pipeline."""

from __future__ import annotations

from pathlib import Path

import click

from .config import settings
from .distance import add_distance_columns
from .index_h3 import build_grid
from .ingest import load_bedrock
from .persist import write_parquet
from .score import compute_likelihood
from .viz import build_map


@click.command()
@click.option("--overwrite", is_flag=True, help="Overwrite existing outputs")
@click.option(
    "--skip-existing",
    is_flag=True,
    help="Skip processing if output files already exist",
)
def main(overwrite: bool, skip_existing: bool) -> None:
    """Run the full prospectivity workflow.

    This CLI reads the configured dataset, builds the H3 grid, computes
    distances to rock boundaries, converts those distances into scores,
    writes the results to disk and finally produces an interactive map.
    """
    # Determine output paths and handle existing files
    parquet_path = Path(settings.paths["parquet"])
    html_path = Path(settings.paths["interactive_html"])
    if (parquet_path.exists() or html_path.exists()) and not overwrite:
        if skip_existing:
            click.echo("Outputs already exist, skipping")
            return
        raise click.ClickException("Output files exist. Use --overwrite or --skip-existing.")

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
