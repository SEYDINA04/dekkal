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
        "lat_min": 14.68, "lat_max": 14.76,
        "lon_min": -17.42, "lon_max": -17.30,
        "risk_score_mean": 62.4,
        "risk_score_max" : 95.2,
        "flood_frequency": 0.7,
        "elevation_mean" : 4.97,
    },
    "Guediawaye": {
        "lat_min": 14.80, "lat_max": 14.87,
        "lon_min": -17.47, "lon_max": -17.32,
        "risk_score_mean": 78.3,
        "risk_score_max" : 94.1,
        "flood_frequency": 0.8,
        "elevation_mean" : 4.02,
    },
    "Yeumbeul": {
        "lat_min": 14.76, "lat_max": 14.80,
        "lon_min": -17.40, "lon_max": -17.27,
        "risk_score_mean": 62.0,
        "risk_score_max" : 90.0,
        "flood_frequency": 0.65,
        "elevation_mean" : 6.5,
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
        "lat_min": 14.69, "lat_max": 14.84,
        "lon_min": -17.30, "lon_max": -17.20,
        "risk_score_mean": 38.0,
        "risk_score_max" : 72.0,
        "flood_frequency": 0.35,
        "elevation_mean" : 11.5,
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
