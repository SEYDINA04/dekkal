"""
Dëkkal — Score Router v2.1
XGBoost ML model + Gemini LLM explanations
Author : Babacar Ndao
"""
import time
from fastapi import APIRouter, HTTPException, Query
from api.models.schemas import ScoreRequest, ScoreResponse
from api.services.feature_engine import extract_all_features
from api.services.ml_model import predict_flood_risk
from api.services.geocoder import geocode_address, suggest_alternatives
from api.services.llm_explainer import generate_explanation

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
async def score_address(
    request: ScoreRequest,
    include_llm_explanation: bool = Query(True, description="Generate Gemini-powered explanation"),
    lang: str = Query("auto", description="Response language: 'fr', 'en', or 'auto' (detected from address)")
):
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
    try:
        result = predict_flood_risk(features)
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "error": "prediction_failed",
            "detail": str(e)
        })

    warning = None
    if result['confidence'] < 0.5:
        warning = "Low confidence — limited data for this location"

    components = {
        "historical_risk"         : round(features.get('sar_delta_km2', 0) * 100, 1),
        "structural_vulnerability": round((1 - features.get('elevation_m', 10) / 20) * 100, 1),
        "extreme_scenario_risk"   : round(min(100, features.get('p99_mm_day', 34) / 50 * 100), 1),
    }

    # Generate LLM explanation with Gemini (optional)
    llm_explanation = None
    if include_llm_explanation:
        if lang == "auto":
            lang = "fr" if (request.address and any(
                w in request.address.lower()
                for w in ['dakar', 'pikine', 'sénégal', 'senegal', 'thiès', 'rufisque', 'mbour', 'saint-louis']
            )) else "en"
        try:
            llm_result = generate_explanation(
                score       =result['score'],
                risk_level  =result['risk_level'],
                zone_name   =result.get('zone_name', 'Unknown'),
                components  =components,
                explanations=result['explanations'],
                address     =address_normalized,
                lang        =lang
            )
            llm_explanation = {
                "status"        : llm_result.get("status", "error"),
                "narrative"     : llm_result.get("narrative", ""),
                "breakdown"     : llm_result.get("breakdown"),
                "provider"      : llm_result.get("provider", "gemini"),
                "context_length": llm_result.get("context_length", 0),
                "embedding"     : llm_result.get("embedding")
            }
        except Exception as e:
            print(f"⚠️  LLM explanation failed: {str(e)}")
            llm_explanation = {
                "status"        : "error",
                "narrative"     : f"Explication non disponible: {str(e)}",
                "breakdown"     : None,
                "provider"      : "gemini",
                "context_length": 0
            }

    processing_ms = int(time.time() * 1000) - start_ms

    return ScoreResponse(**{
        "location": {
            "lat": lat,
            "lon": lon,
            "address_normalized": address_normalized
        },
        "score"           : result['score'],
        "risk_level"      : result['risk_level'],
        "components"      : components,
        "explanations"    : result['explanations'],
        "decision_support": result['decision_support'],
        "confidence"      : result['confidence'],
        "warning"         : warning,
        "llm_explanation" : llm_explanation,
        "meta": {
            "model_version"     : "xgboost_v1.0 + Gemini",
            "data_freshness"    : "2026-04",
            "processing_time_ms": processing_ms,
            "data_completeness" : "high" if result['confidence'] >= 0.75 else "medium",
            "llm_enabled"       : include_llm_explanation,
            "llm_provider"      : llm_explanation.get('provider', 'N/A') if llm_explanation else None
        }
    })


@router.get("/health")
async def health():
    return {
        "status" : "ok",
        "service": "Dëkkal Flood Risk API",
        "version": "2.0",
        "model"  : "xgboost_v1.0"
    }
