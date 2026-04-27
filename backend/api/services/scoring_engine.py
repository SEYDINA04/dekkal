"""
Dëkkal — Scoring Engine v1.3
All pipeline features connected to final score
Features : terrain + SAR + P99 ensemble + soil + ERA5
Author   : Babacar Ndao
"""
from typing import Tuple

# ── CALIBRATION ──────────────────────────────────────────
DRAINAGE_CAPACITY  = 25.0   # mm/day
ELEV_MIN           = 5.0    # m
ELEV_MAX           = 20.0   # m
SLOPE_MIN          = 1.0    # °
SLOPE_MAX          = 5.0    # °
SAR_DELTA_HIGH     = 0.3    # km²
CLAY_HIGH          = 25.0   # % — high impermeability
CLAY_LOW           = 15.0   # % — low impermeability
SM_HIGH            = 0.16   # m³/m³ — saturated soil
SM_LOW             = 0.10   # m³/m³ — dry soil


def compute_historical_risk(sar_delta_km2, sar_wet_km2, sar_dry_km2):
    if sar_dry_km2 == 0 and sar_wet_km2 == 0:
        return 15.0
    if sar_delta_km2 <= 0:
        return 5.0
    return round(min(100.0, sar_delta_km2 / SAR_DELTA_HIGH * 100), 1)


def compute_structural_vulnerability(elevation_m, slope_deg,
                                     drain_risk_score=50.0,
                                     clay_pct=20.5,
                                     soil_moisture=0.13):
    """
    4 sub-components :
    - Elevation  : 35%
    - Slope      : 20%
    - Drainage   : 25%
    - Soil       : 20% (clay impermeability + moisture)
    """
    # Elevation — calibré sur plage réelle Dakar 8-13m
    elev_norm  = max(0, min(1, (ELEV_MAX - elevation_m) /
                              (ELEV_MAX - ELEV_MIN)))
    elev_score = elev_norm * 35

    # Slope
    slope_norm  = max(0, min(1, (SLOPE_MAX - slope_deg) /
                               (SLOPE_MAX - SLOPE_MIN)))
    slope_score = slope_norm * 20

    # Drainage distance
    drain_score = (drain_risk_score / 100.0) * 25

    # Soil — clay impermeability + antecedent moisture
    clay_norm = max(0, min(1, (clay_pct - CLAY_LOW) /
                              (CLAY_HIGH - CLAY_LOW)))
    sm_norm   = max(0, min(1, (soil_moisture - SM_LOW) /
                              (SM_HIGH - SM_LOW)))
    soil_score = (clay_norm * 0.6 + sm_norm * 0.4) * 20

    return round(min(100.0,
        elev_score + slope_score + drain_score + soil_score), 1)


def compute_extreme_scenario_risk(p99_ensemble, p95_ensemble):
    """
    Uses ensemble P99 (GPM + CHIRPS average) for robustness.
    """
    if p99_ensemble <= DRAINAGE_CAPACITY:
        return 10.0
    p99_score = min(70.0,
        (p99_ensemble - DRAINAGE_CAPACITY) / DRAINAGE_CAPACITY * 70)
    p95_bonus = 0.0
    if p95_ensemble > DRAINAGE_CAPACITY:
        p95_bonus = min(30.0,
            (p95_ensemble - DRAINAGE_CAPACITY) / DRAINAGE_CAPACITY * 30)
    return round(min(100.0, p99_score + p95_bonus), 1)


def compute_final_score(hist, vuln, extr):
    return int(round(min(100, max(0,
        0.25 * hist +
        0.35 * vuln +
        0.40 * extr
    ))))


def get_risk_level(score):
    if score <= 30: return "Low"
    if score <= 55: return "Moderate"
    if score <= 75: return "High"
    return "Extreme"


def get_decision_action(score):
    if score <= 30:
        return "standard_underwriting", "Standard underwriting"
    if score <= 55:
        return "file_review", "File review recommended"
    if score <= 75:
        return "field_verification_recommended", \
               "Field verification advised"
    return "mandatory_human_decision", \
           "Mandatory human decision required"


def get_confidence(features):
    critical = ['elevation_m', 'slope_deg', 'p99_ensemble',
                'sar_wet_km2', 'clay_pct', 'soil_moisture_current']
    missing  = sum(1 for k in critical if not features.get(k))
    ratio = 1 - missing / len(critical)
    if ratio >= 0.75: return round(ratio, 2), "high"
    if ratio >= 0.50: return round(ratio, 2), "medium"
    return round(ratio, 2), "low"


def get_explanations(elevation_m, slope_deg, p99_ensemble,
                     sar_delta_km2, clay_pct, soil_moisture):
    factors = []

    if elevation_m <= ELEV_MIN:
        factors.append({
            "factor": f"Low elevation ({elevation_m}m)",
            "impact": "High"
        })
    elif elevation_m <= 10:
        factors.append({
            "factor": f"Moderate elevation ({elevation_m}m)",
            "impact": "Medium"
        })

    if slope_deg <= SLOPE_MIN:
        factors.append({
            "factor": f"Flat terrain ({slope_deg}°) — water stagnates",
            "impact": "High"
        })

    if p99_ensemble > DRAINAGE_CAPACITY * 1.5:
        factors.append({
            "factor": (f"P99 rainfall ({p99_ensemble}mm/day) is "
                      f"{round(p99_ensemble/DRAINAGE_CAPACITY,1)}× "
                      f"drainage capacity"),
            "impact": "High"
        })
    elif p99_ensemble > DRAINAGE_CAPACITY:
        factors.append({
            "factor": f"P99 rainfall exceeds drainage capacity",
            "impact": "Medium"
        })

    if clay_pct >= CLAY_HIGH:
        factors.append({
            "factor": f"High clay content ({clay_pct}%) — impermeable soil",
            "impact": "High"
        })
    elif clay_pct >= 20:
        factors.append({
            "factor": f"Moderate clay content ({clay_pct}%)",
            "impact": "Medium"
        })

    if soil_moisture >= SM_HIGH:
        factors.append({
            "factor": f"Saturated soil ({soil_moisture} m³/m³) — reduced infiltration",
            "impact": "High"
        })

    if sar_delta_km2 > SAR_DELTA_HIGH:
        factors.append({
            "factor": f"Satellite flood signal +{sar_delta_km2}km²",
            "impact": "High"
        })

    if not factors:
        factors.append({
            "factor": "No major risk factors detected",
            "impact": "Low"
        })

    return factors[:3]


def score_location(features: dict) -> dict:
    hist = compute_historical_risk(
        features.get('sar_delta_km2', 0),
        features.get('sar_wet_km2', 0),
        features.get('sar_dry_km2', 0)
    )
    vuln = compute_structural_vulnerability(
        features.get('elevation_m', 10.0),
        features.get('slope_deg', 2.0),
        features.get('drain_risk_score', 50.0),
        features.get('clay_pct', 20.5),
        features.get('soil_moisture_current', 0.13)
    )
    extr = compute_extreme_scenario_risk(
        features.get('p99_ensemble', 34.0),
        features.get('p95_ensemble', 17.0)
    )
    score  = compute_final_score(hist, vuln, extr)
    level  = get_risk_level(score)
    action, label = get_decision_action(score)
    confidence, completeness = get_confidence(features)
    explanations = get_explanations(
        features.get('elevation_m', 10.0),
        features.get('slope_deg', 2.0),
        features.get('p99_ensemble', 34.0),
        features.get('sar_delta_km2', 0),
        features.get('clay_pct', 20.5),
        features.get('soil_moisture_current', 0.13)
    )

    return {
        'score': score, 'risk_level': level,
        'components': {
            'historical_risk'         : hist,
            'structural_vulnerability': vuln,
            'extreme_scenario_risk'   : extr,
        },
        'explanations'    : explanations,
        'decision_support': {'action': action, 'label': label},
        'confidence'      : confidence,
        'data_completeness': completeness,
    }
