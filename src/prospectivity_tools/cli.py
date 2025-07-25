"""Command-line interface for prospectivity heatmap generation."""

import sys
from pathlib import Path

import click
import geopandas as gpd

from . import settings
from .geospatial import add_distance_columns, build_grid, h3_to_geodataframe
from .ingest import add_lithology_flags, extract_rock_types
from .score import compute_likelihood
from .viz import build_static_map


@click.command()
@click.option(
    "--generate-map/--no-generate-map",
    default=True,
    help="Generate static map visualization (default: True)",
)
@click.option(
    "--config",
    type=click.Path(exists=True),
    default="config.yaml",
    help="Path to configuration file (default: config.yaml)",
)
def main(generate_map: bool, config: str):
    """Generate a prospectivity heatmap from bedrock geology data.

    This tool processes bedrock geology polygons to create a prospectivity
    score for mineral exploration. It:

    1. Reads bedrock geology from a geopackage
    2. Extracts specified rock types
    3. Builds an H3 hexagonal grid
    4. Computes distances to rock type boundaries
    5. Calculates likelihood scores using a Gaussian kernel
    6. Saves results as a geopackage
    7. Optionally generates a static map visualization
    """
    try:
        # Validate input file exists
        input_path = Path(settings.paths["input_gpkg"])
        if not input_path.exists():
            click.echo(f"Error: Input file not found: {input_path}", err=True)
            sys.exit(1)

        click.echo("Starting prospectivity analysis...")

        # Read in geopackage
        click.echo(f"Reading bedrock data from {input_path}")
        gdf = gpd.read_file(settings.paths["input_gpkg"], engine="pyogrio").to_crs(settings.crs)
        click.echo(f"Loaded {len(gdf)} polygons")

        # Feature engineering: add lithology flags
        click.echo("Adding lithology flags...")
        gdf = add_lithology_flags(gdf)

        # Extract rock polygons
        click.echo(f"Extracting rock types: {settings.rock_a} and {settings.rock_b}")
        rock_a, rock_b = extract_rock_types(gdf)
        click.echo(
            f"Found {len(rock_a)} {settings.rock_a} polygons and "
            f"{len(rock_b)} {settings.rock_b} polygons"
        )

        # Build the hexagon grid covering both rock types
        click.echo(f"Building H3 grid at resolution {settings.grid['resolution']}")
        grid = build_grid(rock_a, rock_b)
        click.echo(f"Created grid with {len(grid)} hexagons")

        # Compute distances to each rock type
        click.echo("Computing distances to rock type boundaries...")
        grid = add_distance_columns(grid)

        # Calculate likelihood scores using the Gaussian kernel
        click.echo("Calculating likelihood scores...")
        scored = compute_likelihood(grid)

        # Convert to GeoDataFrame for saving as geopackage
        click.echo("Converting to GeoDataFrame...")
        scored_gdf = h3_to_geodataframe(scored)

        # Save the scored grid as a geopackage
        output_path = Path(settings.paths["output_gpkg"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        click.echo(f"Saving results to {output_path}")
        scored_gdf.to_file(output_path, driver="GPKG")

        # Create a static map if requested
        if generate_map:
            click.echo("Generating static map...")
            build_static_map(scored_gdf)  # Use the GeoDataFrame for the map
            map_path = Path(settings.paths["static_map"])
            map_path.parent.mkdir(parents=True, exist_ok=True)
            click.echo(f"Map saved to {map_path}")

        click.echo("Prospectivity analysis complete!")

    except Exception as e:
        click.echo(f"Error during analysis: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
