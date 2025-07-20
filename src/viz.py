"""Visualisation of prospectivity scores using Folium.

This module contains helper functions to convert H3 hexagon identifiers
and their associated scores into GeoJSON features and to build an
interactive map using Folium. The resulting map shades each hexagon
according to its prospectivity score and saves an HTML file to the
location specified in the configuration.
"""

from __future__ import annotations

import pandas as pd
import folium
from h3ronpy import h3

from .config import settings


def hex_to_geojson(h3_ids: pd.Series, scores: pd.Series):
    """Yield GeoJSON features for H3 cells with score properties.

    Parameters
    ----------
    h3_ids : pandas.Series
        Series of H3 indexes.
    scores : pandas.Series
        Series of prospectivity scores corresponding to each H3 cell.

    Yields
    ------
    dict
        A GeoJSON feature dictionary for each cell.
    """
    for hid, score in zip(h3_ids, scores):
        # Get boundary coordinates in GeoJSON-friendly format (lon/lat order)
        boundary = h3.h3_to_geo_boundary(hid, geo_json=True)
        yield {
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [boundary]},
            "properties": {"score": float(score)},
        }


def build_map(df: pd.DataFrame) -> folium.Map:
    """Create an interactive Folium map coloured by prospectivity.

    The map uses a continuous Brewer palette to shade hexagons based on
    their score. A tooltip shows the numeric score when hovering over a
    hexagon. The map is saved to the HTML path defined in the config.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with columns ``h3_id`` and ``score``.

    Returns
    -------
    folium.Map
        The constructed map object.
    """
    # Default centre of map can be tuned; here we use the centroid of the
    # dataset if available. As a simple fallback we choose a fixed view.
    m = folium.Map(location=[50.0, -122.0], zoom_start=7, tiles="Stamen Terrain")
    # Build GeoJSON feature collection
    features = list(hex_to_geojson(df["h3_id"], df["score"]))
    folium.GeoJson(
        {"type": "FeatureCollection", "features": features},
        style_function=lambda feat: {
            "fillColor": folium.utilities.color_brewer("YlGnBu", 9, feat["properties"]["score"])[-1],
            "color": "#444",
            "weight": 0.3,
            "fillOpacity": 0.6,
        },
        tooltip=folium.GeoJsonTooltip(fields=["score"], aliases=["Prospectivity"]),
    ).add_to(m)
    # Save interactive HTML
    m.save(settings.paths["interactive_html"])
    return m
