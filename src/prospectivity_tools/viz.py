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
    """Generate GeoJSON features for H3 cells with attached scores."""
    features = []
    for hid, score in zip(h3_ids, scores):
        try:
            latlng_ring = h3.h3_to_geo_boundary(hid)
            boundary = [(lng, lat) for lat, lng in latlng_ring]
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
    # Initialize the map
    m = folium.Map(location=[50.0, -122.0], zoom_start=7, tiles="cartodb positron")

    # Validate input DataFrame
    if df.empty:
        print("Warning: DataFrame is empty, returning empty map")
        return m

    if not {"h3_id", "score"}.issubset(df.columns):
        print(f"Warning: Required columns missing. Found: {df.columns.tolist()}")
        return m

    # Generate GeoJSON features
    features = hex_to_geojson(df["h3_id"], df["score"])
    if not features:
        print("Warning: No features generated from H3 data")
        return m

    print(f"Generated {len(features)} features for visualization")

    # Define color mapping
    min_score = df["score"].min()
    max_score = df["score"].max()

    def get_color(score: float) -> str:
        """Map score to a color gradient from blue to yellow."""
        norm_score = (score - min_score) / (max_score - min_score) if max_score > min_score else 0.5
        r = int(255 * norm_score)
        g = int(255 * (1 - abs(norm_score - 0.5) * 2))
        b = int(255 * (1 - norm_score))
        return f"#{r:02x}{g:02x}{b:02x}"

    # Add GeoJSON layer to the map
    try:
        folium.GeoJson(
            {"type": "FeatureCollection", "features": features},
            style_function=lambda feat: {
                "fillColor": get_color(feat["properties"]["score"]),
                "color": "#444",
                "weight": 0.3,
                "fillOpacity": 0.6,
            },
            tooltip=folium.GeoJsonTooltip(fields=["score"], aliases=["Prospectivity"]),
        ).add_to(m)
    except Exception as e:
        print(f"Error creating GeoJson layer: {e}")
        return m

    # Save the map to an HTML file
    try:
        m.save(settings.paths["interactive_html"])
    except Exception as e:
        print(f"Error saving map: {e}")

    return m