"""Visualisation of prospectivity scores using Folium.

This module contains helper functions to convert H3 hexagon identifiers
and their associated scores into GeoJSON features and to build an
interactive map using Folium. The resulting map shades each hexagon
according to its prospectivity score and saves an HTML file to the
location specified in the configuration.
"""

from __future__ import annotations

import folium
import h3
import pandas as pd

from .config import settings

def hex_to_geojson(h3_ids: pd.Series, scores: pd.Series):
    """Yield GeoJSON features for H3 cells with attached scores."""
    for hid, score in zip(h3_ids, scores, strict=False):
        latlng_ring = h3.cell_to_boundary(hid)                   
        boundary = [(lng, lat) for lat, lng in latlng_ring]
        yield {
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [boundary]},
            "properties": {"score": float(score)},
        }

def build_map(df: pd.DataFrame) -> folium.Map:
    """Interactive Folium map coloured by prospectivity score."""
    m = folium.Map(
        location=[50.0, -122.0],             
        zoom_start=7,
        tiles="cartodb positron"          
    )
    features = list(hex_to_geojson(df["h3_id"], df["score"]))
    folium.GeoJson(
        {"type": "FeatureCollection", "features": features},
        style_function=lambda feat: {
            "fillColor": folium.utilities.color_brewer(
                "YlGnBu", 9, feat["properties"]["score"]
            )[-1],
            "color": "#444",
            "weight": 0.3,
            "fillOpacity": 0.6,
        },
        tooltip=folium.GeoJsonTooltip(fields=["score"], aliases=["Prospectivity"]),
    ).add_to(m)

    m.save(settings.paths["interactive_html"])
    return m