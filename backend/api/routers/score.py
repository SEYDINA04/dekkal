"""
Dëkkal — Score Router v1.1
POST /score — address OR coordinates → risk score
Geocoding : Nominatim (OpenStreetMap)
"""
import time
from fastapi import APIRouter, HTTPException
from api.models.schemas import ScoreRequest, ScoreResponse
from api.services.feature_engine import extract_all_features
from api.services.scoring_engine import score_location
from api.services.geocoder import geocode_address, suggest_alternatives

router = APIRouter(prefix="/api/v1", tags=["scoring"])

DAKAR_BBOX = {
    "lon_min": -17.6, "lon_max": -17.1,
    "lat_min": 14.6,  "lat_max": 14.95
}


def validate_zone(lat: float, lon: float):
    if not (DAKAR_BBOX["lat_min"] <= lat <= DAKAR_BBOX["lat_max"] and
            DAKAR_BBOX["lon_min"] <= lon <= DAKAR_BBOX["lon_max"]):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "zone_not_covered",
                "message": "Location outside Dëkkal coverage area (Dakar, Senegal)",
                "coverage": "Dakar urban zone — lat [14.6, 14.95] lon [-17.6, -17.1]"
            }
        )


@router.post("/score", response_model=ScoreResponse)
async def score_address(request: ScoreRequest):
    start_ms = int(time.time() * 1000)

    # ── VALIDATION INPUT ─────────────────────────────────
    if not request.address and (request.lat is None or request.lon is None):
        raise HTTPException(
            status_code=422,
            detail={"error": "Provide either 'address' or 'lat' + 'lon'"}
        )

    # ── GEOCODING ────────────────────────────────────────
    if request.lat is not None and request.lon is not None:
        lat = request.lat
        lon = request.lon
        address_normalized = f"{lat}, {lon}"

    else:
        try:
            lat, lon, address_normalized = geocode_address(request.address)
        except ValueError as e:
            suggestions = suggest_alternatives(request.address)
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "geocoding_failed",
                    "message": str(e),
                    "suggestions": suggestions
                }
            )

    # ── ZONE VALIDATION ──────────────────────────────────
    validate_zone(lat, lon)

    # ── FEATURE EXTRACTION ───────────────────────────────
    try:
        features = extract_all_features(lat, lon)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "feature_extraction_failed", "detail": str(e)}
        )

    # ── SCORING ──────────────────────────────────────────
    result = score_location(features)

    warning = None
    if result['confidence'] < 0.5:
        warning = "Low confidence — limited data for this location"

    processing_ms = int(time.time() * 1000) - start_ms

    return ScoreResponse(
        location={
            "lat"               : lat,
            "lon"               : lon,
            "address_normalized": address_normalized
        },
        score=result['score'],
        risk_level=result['risk_level'],
        components=result['components'],
        explanations=result['explanations'],
        decision_support=result['decision_support'],
        confidence=result['confidence'],
        warning=warning,
        meta={
            "model_version"    : "v1.0",
            "data_freshness"   : "2026-04",
            "processing_time_ms": processing_ms,
            "data_completeness": result['data_completeness']
        }
    )


@router.get("/health")
async def health():
    return {
        "status" : "ok",
        "service": "Dëkkal Flood Risk API",
        "version": "1.0"
    }
