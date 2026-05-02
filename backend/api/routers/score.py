"""
Dëkkal — Score Router v2.0
XGBoost ML model replaces rule-based engine
Author : Babacar Ndao
"""
import time
from fastapi import APIRouter, HTTPException
from api.models.schemas import ScoreRequest, ScoreResponse
from api.services.feature_engine import extract_all_features
from api.services.ml_model import predict_flood_risk
from api.services.geocoder import geocode_address, suggest_alternatives

router = APIRouter(prefix="/api/v1", tags=["scoring"])

DAKAR_BBOX = {
    "lon_min": -17.6, "lon_max": -17.1,
    "lat_min": 14.6,  "lat_max": 14.95
}


def validate_zone(lat, lon):
    if not (DAKAR_BBOX["lat_min"] <= lat <= DAKAR_BBOX["lat_max"] and
            DAKAR_BBOX["lon_min"] <= lon <= DAKAR_BBOX["lon_max"]):
        raise HTTPException(status_code=400, detail={
            "error": "zone_not_covered",
            "message": "Location outside Dëkkal coverage (Dakar, Senegal)"
        })


@router.post("/score", response_model=ScoreResponse)
async def score_address(request: ScoreRequest):
    start_ms = int(time.time() * 1000)

    # Input validation
    if not request.address and (
            request.lat is None or request.lon is None):
        raise HTTPException(status_code=422, detail={
            "error": "Provide 'address' or 'lat'+'lon'"
        })

    # Geocoding
    if request.lat is not None and request.lon is not None:
        lat, lon = request.lat, request.lon
        address_normalized = f"{lat}, {lon}"
    else:
        try:
            lat, lon, address_normalized = geocode_address(
                request.address)
        except ValueError as e:
            suggestions = suggest_alternatives(request.address)
            raise HTTPException(status_code=400, detail={
                "error": "geocoding_failed",
                "message": str(e),
                "suggestions": suggestions
            })

    validate_zone(lat, lon)

    # Feature extraction
    try:
        features = extract_all_features(lat, lon)
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "error": "feature_extraction_failed",
            "detail": str(e)
        })

    # ML Scoring — XGBoost
    result = predict_flood_risk(features)

    warning = None
    if result['confidence'] < 0.5:
        warning = "Low confidence — limited data for this location"

    processing_ms = int(time.time() * 1000) - start_ms

    return ScoreResponse(
        location={
            "lat": lat,
            "lon": lon,
            "address_normalized": address_normalized
        },
        score=result['score'],
        risk_level=result['risk_level'],
        components={
            "historical_risk"         : round(features.get('sar_delta_km2', 0) * 100, 1),
            "structural_vulnerability": round((1 - features.get('elevation_m', 10) / 20) * 100, 1),
            "extreme_scenario_risk"   : round(min(100, features.get('p99_mm_day', 34) / 50 * 100), 1),
        },
        explanations=result['explanations'],
        decision_support=result['decision_support'],
        confidence=result['confidence'],
        warning=warning,
        meta={
            "model_version"    : "xgboost_v1.0",
            "data_freshness"   : "2026-04",
            "processing_time_ms": processing_ms,
            "data_completeness": "high" if result['confidence'] >= 0.75 else "medium"
        }
    )


@router.get("/health")
async def health():
    return {
        "status" : "ok",
        "service": "Dëkkal Flood Risk API",
        "version": "2.0",
        "model"  : "xgboost_v1.0"
    }
