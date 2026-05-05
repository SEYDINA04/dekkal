"""
Dëkkal — ML Model Service v3.1
Zone-based XGBoost score + address-level terrain adjustment
Author : Babacar Ndao
"""
import joblib
import numpy as np
import json
import os

BASE = os.path.dirname(__file__)

model    = joblib.load(os.path.join(BASE, '../../dekkal_xgboost_v3.pkl'))
FEATURES = joblib.load(os.path.join(BASE, '../../dekkal_xgboost_features_v3.pkl'))

from api.services.zone_config import get_zone, ZONES

# Pre-computed zone SAR features from training dataset
ZONE_SAR = {
    "Yeumbeul_Malika"  : {"sar_delta_km2": 0.54, "sar_wet_km2": 0.62, "sar_dry_km2": 0.08},
    "Keur_Massar_Mbao" : {"sar_delta_km2": 0.60, "sar_wet_km2": 0.68, "sar_dry_km2": 0.08},
    "Pikine_Nord_Dense": {"sar_delta_km2": 0.13, "sar_wet_km2": 0.20, "sar_dry_km2": 0.07},
    "Pikine"            : {"sar_delta_km2": 0.13, "sar_wet_km2": 0.20, "sar_dry_km2": 0.07},
    "Dakar_Centre"     : {"sar_delta_km2": 0.22, "sar_wet_km2": 0.30, "sar_dry_km2": 0.08},
    "Guediawaye"       : {"sar_delta_km2": 0.45, "sar_wet_km2": 0.52, "sar_dry_km2": 0.07},
    "Yeumbeul"         : {"sar_delta_km2": 0.35, "sar_wet_km2": 0.42, "sar_dry_km2": 0.07},
    "Almadies_Ngor"    : {"sar_delta_km2": 0.02, "sar_wet_km2": 0.05, "sar_dry_km2": 0.03},
    "Plateau_Dakar"    : {"sar_delta_km2": 0.01, "sar_wet_km2": 0.03, "sar_dry_km2": 0.02},
    "Keur_Massar"      : {"sar_delta_km2": 0.08, "sar_wet_km2": 0.12, "sar_dry_km2": 0.04},
}
DEFAULT_SAR = {"sar_delta_km2": 0.10, "sar_wet_km2": 0.15, "sar_dry_km2": 0.05}

# Structural vulnerability multiplier by property type
PROPERTY_VULNERABILITY = {
    "residential": 1.0,
    "commercial" : 1.1,
    "hotel"      : 1.15,
    "school"     : 1.25,
    "hospital"   : 1.4,
    "warehouse"  : 0.85,
}

print(f"✓ XGBoost v3.1 loaded | Recall=95.8% | Zone SAR lookup active")


def predict_flood_risk(features: dict, property_type: str = "residential") -> dict:
    lat = features.get('_lat', 14.75)
    lon = features.get('_lon', -17.39)

    # Get zone
    zone_name, zone_data = get_zone(lat, lon)

    # Use pre-computed zone SAR features
    sar = ZONE_SAR.get(zone_name, DEFAULT_SAR)

    # Build feature vector with zone SAR
    feature_values = {
        'elevation_m'  : features.get('elevation_m', 8.0),
        'slope_deg'    : features.get('slope_deg', 2.0),
        'clay_pct'     : features.get('clay_pct', 22.0),
        'p95_mm_day'   : features.get('p95_mm_day', 17.0),
        'p99_mm_day'   : features.get('p99_mm_day', 34.0),
        'sar_dry_km2'  : sar['sar_dry_km2'],
        'sar_wet_km2'  : sar['sar_wet_km2'],
        'sar_delta_km2': sar['sar_delta_km2'],
        'soil_moisture': features.get('soil_moisture_current', 0.13),
        'precip_mm'    : features.get('precip_season_mm', 490.0),
    }

    X     = np.array([[feature_values[f] for f in FEATURES]])
    prob  = float(model.predict_proba(X)[0][1])
    score = int(round(prob * 100))

    # Elevation adjustment — address-level
    elevation = features.get('elevation_m', 8.0)
    zone_elev = zone_data.get('elevation_mean', 8.0) if zone_data else 8.0
    elev_adj  = int((zone_elev - elevation) * 2)
    score     = min(100, max(0, score + elev_adj))

    # Risk level
    if score <= 30:   risk_level = "Low"
    elif score <= 55: risk_level = "Moderate"
    elif score <= 75: risk_level = "High"
    else:             risk_level = "Extreme"

    # Decision support
    if score <= 30:
        action = "standard_underwriting"
        label  = "Standard underwriting"
    elif score <= 55:
        action = "file_review"
        label  = "File review recommended"
    elif score <= 75:
        action = "field_verification_recommended"
        label  = "Field verification advised"
    else:
        action = "mandatory_human_decision"
        label  = "Mandatory human decision required"

    # Explanations
    explanations = []
    if zone_data:
        freq = int(zone_data.get('flood_frequency', 0) * 100)
        zname = zone_name.replace('_', ' ')
        explanations.append({
            "factor": f"{zname} — {freq}% historical flood frequency",
            "impact": "High" if freq >= 70 else "Medium"
        })
    if sar['sar_delta_km2'] > 0.3:
        explanations.append({
            "factor": f"Strong satellite flood signal (SAR delta {sar['sar_delta_km2']}km²)",
            "impact": "High"
        })
    elif sar['sar_delta_km2'] > 0.1:
        explanations.append({
            "factor": f"Moderate satellite flood signal detected",
            "impact": "Medium"
        })
    if elevation < 5:
        explanations.append({
            "factor": f"Low elevation ({elevation}m)",
            "impact": "High"
        })
    if not explanations:
        explanations.append({
            "factor": "No major risk factors detected",
            "impact": "Low"
        })

    # Confidence
    has_zone = 1 if zone_data else 0
    has_elev = 1 if features.get('elevation_m') else 0
    has_precip = 1 if features.get('p99_mm_day') else 0
    confidence = round((has_zone + has_elev + has_precip) / 3, 2)

    # Property-type vulnerability adjustment
    vuln_mult = PROPERTY_VULNERABILITY.get(property_type, 1.0)
    raw_vuln  = max(0, (1 - elevation / 20)) * 100
    adj_vuln  = round(min(100, raw_vuln * vuln_mult), 1)

    if vuln_mult > 1.0 and property_type not in ("residential",):
        ptype_label = property_type.replace("_", " ").capitalize()
        explanations.append({
            "factor": f"{ptype_label} — higher structural exposure to flood damage",
            "impact": "High" if vuln_mult >= 1.3 else "Medium"
        })

    return {
        'score'           : score,
        'risk_level'      : risk_level,
        'zone_name'       : zone_name or "Unknown",
        'property_type'   : property_type,
        'components'      : {
            'historical_risk'         : round(sar['sar_delta_km2'] * 100, 1),
            'structural_vulnerability': adj_vuln,
            'extreme_scenario_risk'   : round(min(100, features.get('p99_mm_day', 34) / 50 * 100), 1),
        },
        'explanations'    : explanations[:4],
        'decision_support': {'action': action, 'label': label},
        'confidence'      : confidence,
        'model_type'      : 'xgboost_v3_pikine',
    }
