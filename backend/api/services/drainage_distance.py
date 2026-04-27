"""
Dëkkal — OSM Drainage Distance Feature
Computes distance (meters) from a point to nearest drain/canal
Source : OpenStreetMap via osmnx
Author : Babacar Ndao
"""
import osmnx as ox
import geopandas as gpd
from shapely.geometry import Point
import numpy as np

# Cache global — chargé une seule fois au démarrage
_drainage_gdf = None

DRAINAGE_TAGS = {
    "waterway": ["canal", "drain", "ditch", "stream", "river"]
}


def load_drainage_network() -> gpd.GeoDataFrame:
    """Charge le réseau de drainage OSM pour Dakar — mis en cache."""
    global _drainage_gdf
    if _drainage_gdf is None:
        print("Loading OSM drainage network for Dakar...")
        gdf = ox.features_from_place("Dakar, Senegal", tags=DRAINAGE_TAGS)
        # Garder uniquement les LineStrings
        _drainage_gdf = gdf[gdf.geom_type == 'LineString'].copy()
        # Projeter en UTM zone 28N pour calculs en mètres
        _drainage_gdf = _drainage_gdf.to_crs("EPSG:32628")
        print(f"Drainage network loaded: {len(_drainage_gdf)} features")
    return _drainage_gdf


def get_drainage_distance(lat: float, lon: float) -> dict:
    """
    Returns distance in meters to nearest drain.
    Also returns drainage density score (0-100).
    """
    gdf = load_drainage_network()

    # Point en UTM 28N
    pt_wgs84 = Point(lon, lat)
    pt_gdf = gpd.GeoDataFrame(
        geometry=[pt_wgs84], crs="EPSG:4326"
    ).to_crs("EPSG:32628")
    pt_utm = pt_gdf.geometry.iloc[0]

    # Distance au drain le plus proche
    distances = gdf.geometry.distance(pt_utm)
    min_dist  = round(float(distances.min()), 1)

    # Compter les drains dans un rayon de 500m
    drains_500m = int((distances <= 500).sum())

    # Score drainage (0-100)
    # Proche drain = eau s'écoule = risque plus faible
    # Mais aussi : drain débordé = risque plus élevé
    # On utilise la distance comme proxy de connectivité au réseau
    if min_dist <= 50:
        # Très proche : drain peut déborder → risque élevé
        drain_risk_score = 80.0
    elif min_dist <= 200:
        # Zone de drainage directe → risque modéré
        drain_risk_score = 50.0
    elif min_dist <= 500:
        # Drainage accessible → risque modéré-faible
        drain_risk_score = 30.0
    else:
        # Loin de tout drain → eau stagne → risque élevé
        drain_risk_score = 70.0

    return {
        "drain_distance_m"  : min_dist,
        "drains_500m"       : drains_500m,
        "drain_risk_score"  : drain_risk_score,
    }
