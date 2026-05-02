"""
Dëkkal — Zone Configuration v1.1
Non-overlapping bboxes — refined boundaries
Author : Babacar Ndao
"""

ZONES = {
    "Almadies_Ngor": {
        "lat_min": 14.72, "lat_max": 14.85,
        "lon_min": -17.56, "lon_max": -17.46,
        "risk_score_mean": 45.0,
        "risk_score_max" : 70.0,
        "flood_frequency": 0.3,
        "elevation_mean" : 8.5,
    },
    "Dakar_Centre": {
        "lat_min": 14.72, "lat_max": 14.85,
        "lon_min": -17.46, "lon_max": -17.42,
        "risk_score_mean": 70.7,
        "risk_score_max" : 95.0,
        "flood_frequency": 0.8,
        "elevation_mean" : 5.51,
    },
    "Pikine": {
        "lat_min": 14.68, "lat_max": 14.78,
        "lon_min": -17.42, "lon_max": -17.28,
        "risk_score_mean": 62.4,
        "risk_score_max" : 95.2,
        "flood_frequency": 0.7,
        "elevation_mean" : 4.97,
    },
    "Guediawaye": {
        "lat_min": 14.76, "lat_max": 14.85,
        "lon_min": -17.42, "lon_max": -17.30,
        "risk_score_mean": 78.3,
        "risk_score_max" : 94.1,
        "flood_frequency": 0.8,
        "elevation_mean" : 4.02,
    },
    "Plateau_Dakar": {
        "lat_min": 14.66, "lat_max": 14.72,
        "lon_min": -17.47, "lon_max": -17.42,
        "risk_score_mean": 28.0,
        "risk_score_max" : 45.0,
        "flood_frequency": 0.2,
        "elevation_mean" : 12.5,
    },
    "Keur_Massar": {
        "lat_min": 14.69, "lat_max": 14.76,
        "lon_min": -17.32, "lon_max": -17.22,
        "risk_score_mean": 44.1,
        "risk_score_max" : 90.6,
        "flood_frequency": 0.7,
        "elevation_mean" : 10.32,
    },
}


def get_zone(lat: float, lon: float) -> tuple:
    matches = []
    for zone_name, z in ZONES.items():
        if (z['lat_min'] <= lat <= z['lat_max'] and
                z['lon_min'] <= lon <= z['lon_max']):
            area = ((z['lat_max'] - z['lat_min']) *
                    (z['lon_max'] - z['lon_min']))
            matches.append((area, zone_name, z))
    if not matches:
        return None, None
    matches.sort(key=lambda x: x[0])
    _, zone_name, zone_data = matches[0]
    return zone_name, zone_data
