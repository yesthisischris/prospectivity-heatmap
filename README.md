# Prospectivity Tools

This repository contains a geospatial prospectivity heatmap generator built using
H3 hexagonal grids, Folium for visualisation, and a configurable pipeline.
It ingests bedrock geology polygons, indexes them with H3, computes
distances to interfaces between two selected rock types, applies a Gaussian
fall‑off scoring function and produces a prospectivity score for each H3 cell.
The resulting scores can be persisted as a Parquet table and visualised as an
interactive web map.

## Structure

- **`config.yaml`** – all adjustable parameters: coordinate reference system,
  rock type names, fall‑off distance, H3 resolution and output paths.
- **`src/`** – modular Python code for ingestion, indexing, distance
  calculation, scoring, persistence, visualisation and a CLI entrypoint.
- **`data/`** – raw input data (e.g. `BedrockP.gpkg`) and processed outputs
  such as Parquet tables and map files.
- **`tests/`** – a simple unit test for the Gaussian scoring kernel.

## Getting Started

1. Install dependencies declared in `pyproject.toml` into a virtual
   environment:

   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -e .
    ```

2. Place your `BedrockP.gpkg` file into `data/raw/` and adjust `config.yaml`
   as needed to select different rock types or H3 resolutions.

3. Run the pipeline via the CLI:

   ```bash
   prospectivity
   ```

    This generates a Parquet file of H3 cell scores and saves an interactive
    HTML map in `data/processed/`.

## Development environment with `uv`

`uv` can be used to create a reproducible environment with all development
dependencies included:

```bash
uv venv
uv pip install -e .[dev]
```

If you are working in Jupyter, ensure the kernel points to this environment so
that notebooks can `import prospectivity_tools` without issues.

## Notes

- The pipeline expects geometry coordinates in the CRS defined in
  `config.yaml` (EPSG:26910 by default).
- Distances are computed to the nearest boundary of each rock type and
  converted to a 0–1 likelihood using a Gaussian fall‑off.
