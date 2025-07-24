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


def hex_to_geojson(h3_ids: pd.Series, scores: pd.Series) -> list:
    """Generate GeoJSON features for H3 cells with scores above 0.05."""
    features = []
    for hid, score in zip(h3_ids, scores):
        if score < 0.05:
            continue
        try:
            boundary = [(lng, lat) for lat, lng in h3.h3_to_geo_boundary(hid)]
            features.append({
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [boundary]},
                "properties": {"score": float(score)},
            })
        except Exception as e:
            print(f"Error processing H3 ID {hid}: {e}")
    return features


def build_map(df: pd.DataFrame) -> folium.Map:
    """Create an interactive Folium map colored by prospectivity score."""
    m = folium.Map(location=[50.0, -122.0], zoom_start=7, tiles="cartodb positron")
    
    if df.empty or not {"h3_id", "score"}.issubset(df.columns):
        return m

    features = hex_to_geojson(df["h3_id"], df["score"])
    if not features:
        return m

    min_score, max_score = df["score"].min(), df["score"].max()

    def get_color(score: float) -> str:
        """Red-yellow-green gradient with opacity based on score."""
        norm = (score - min_score) / (max_score - min_score) if max_score > min_score else 0.5
        
        if norm < 0.5:
            # Green to Yellow (low to mid scores)
            r, g, b = int(255 * norm * 2), 255, 0
        else:
            # Yellow to Red (mid to high scores)
            r, g, b = 255, int(255 * (2 - norm * 2)), 0
        
        return f"rgba({r}, {g}, {b}, {norm})"

    folium.GeoJson(
        {"type": "FeatureCollection", "features": features},
        style_function=lambda feat: {
            "fillColor": get_color(feat["properties"]["score"]),
            "weight": 0,
            "fillOpacity": 1.0,
        },
        tooltip=folium.GeoJsonTooltip(fields=["score"], aliases=["Score"]),
    ).add_to(m)

    m.save(settings.paths["interactive_html"])
    return m