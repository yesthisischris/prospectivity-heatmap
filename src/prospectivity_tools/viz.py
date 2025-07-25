from __future__ import annotations

import contextily as ctx
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt

from .config import settings


def build_static_map(gdf: gpd.GeoDataFrame, output_path: str | None = None) -> plt.Figure:
    """Static prospectivity map with alpha-by-score.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame with 'score' column and geometry.
    output_path : str, optional
        Path to save the map. If None, uses path from config.

    Returns
    -------
    plt.Figure
        The matplotlib figure object
    """
    if not output_path:
        output_path = settings.paths["static_map"]

    if gdf.empty or "score" not in gdf.columns:
        return plt.figure()

    # Convert to Web Mercator for plotting with basemap
    gdf = gdf.to_crs("EPSG:3857")

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 10))

    # Add title
    ax.set_title("Cobalt Prospectivity Map", fontsize=16, fontweight="bold")

    cmap = mpl.colors.LinearSegmentedColormap.from_list("prospectivity", ["green", "yellow", "red"])
    norm = plt.Normalize(vmin=gdf["score"].min(), vmax=gdf["score"].max())
    facecolours = [(*cmap(norm(s))[:3], norm(s)) for s in gdf["score"]]

    gdf.plot(ax=ax, color=facecolours, edgecolor="none", linewidth=0)

    # Set tight bounds to data extent
    ax.set_xlim(gdf.total_bounds[0], gdf.total_bounds[2])
    ax.set_ylim(gdf.total_bounds[1], gdf.total_bounds[3])

    # Add basemap
    ctx.add_basemap(
        ax,
        crs=gdf.crs,
        source=ctx.providers.CartoDB.Positron,
        zoom=10,
    )

    # Color bar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, shrink=0.8, aspect=20)
    cbar.set_label("Prospectivity score", rotation=270, labelpad=20)

    # 50-km scale bar
    xmin, ymin, xmax, ymax = gdf.total_bounds
    scalelen = 50_000
    sx = xmin + 0.05 * (xmax - xmin)
    sy = ymin + 0.05 * (ymax - ymin)
    ax.plot([sx, sx + scalelen], [sy, sy], color="k", linewidth=3)
    ax.text(
        sx + scalelen / 2,
        sy + 0.02 * (ymax - ymin),
        "50 km",
        ha="center",
        va="bottom",
        fontsize=10,
        weight="bold",
    )

    # Add coordinate labels (convert back to lat/lng for display)
    gdf_latlon = gdf.to_crs("EPSG:4326")
    lon_min, lat_min, lon_max, lat_max = gdf_latlon.total_bounds

    # X-axis (longitude) labels - 5 evenly spaced
    lon_ticks = [lon_min + i * (lon_max - lon_min) / 4 for i in range(5)]
    x_ticks = [xmin + i * (xmax - xmin) / 4 for i in range(5)]
    for x_pos, lon_val in zip(x_ticks, lon_ticks, strict=False):
        ax.text(
            x_pos, ymin - 0.02 * (ymax - ymin), f"{lon_val:.1f}°", ha="center", va="top", fontsize=9
        )

    # Y-axis (latitude) labels - 5 evenly spaced
    lat_ticks = [lat_min + i * (lat_max - lat_min) / 4 for i in range(5)]
    y_ticks = [ymin + i * (ymax - ymin) / 4 for i in range(5)]
    for y_pos, lat_val in zip(y_ticks, lat_ticks, strict=False):
        ax.text(
            xmin - 0.02 * (xmax - xmin),
            y_pos,
            f"{lat_val:.1f}°",
            ha="right",
            va="center",
            fontsize=9,
            rotation=90,
        )

    ax.set_axis_off()

    fig.savefig(output_path, dpi=300, bbox_inches="tight")

    return fig
