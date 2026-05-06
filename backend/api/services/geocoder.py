"""
Dëkkal — Geocoder Service
Provider : Nominatim (OpenStreetMap) — free, no API key
Fallback : coordinates pass-through
Author   : Babacar Ndao
"""
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from typing import Tuple, Optional
import time

geolocator = Nominatim(
    user_agent="dekkal-flood-risk-api-v1",
    timeout=10
)

# Dakar bounding box pour restreindre les résultats
DAKAR_VIEWBOX = [
    (-17.6, 14.95),  # top-left
    (-17.1, 14.6),   # bottom-right
]

DAKAR_BBOX = {
    "lon_min": -17.6, "lon_max": -17.1,
    "lat_min": 14.6,  "lat_max": 14.95
}


def geocode_address(address: str) -> Tuple[float, float, str]:
    """
    Geocode an address to (lat, lon, normalized_address).
    Raises ValueError if address cannot be resolved within Dakar.
    """
    # Ajouter "Dakar, Senegal" si non précisé
    query = address
    if "dakar" not in address.lower() and "sénégal" not in address.lower() \
       and "senegal" not in address.lower():
        query = f"{address}, Dakar, Senegal"

    try:
        location = geolocator.geocode(
            query,
            viewbox=DAKAR_VIEWBOX,
            bounded=True,
            language="en",
            exactly_one=True,
        )

        # Si pas de résultat dans le viewbox, essai sans bounded
        if location is None:
            location = geolocator.geocode(
                query,
                language="en",
                exactly_one=True,
            )

        if location is None:
            raise ValueError(
                f"Address not found: '{address}'. "
                "Try adding more context e.g. 'Pikine, Dakar' or use lat/lon."
            )

        lat = location.latitude
        lon = location.longitude

        # Vérifier que le résultat est dans la zone Dakar
        if not (DAKAR_BBOX["lat_min"] <= lat <= DAKAR_BBOX["lat_max"] and
                DAKAR_BBOX["lon_min"] <= lon <= DAKAR_BBOX["lon_max"]):
            raise ValueError(
                f"Resolved location ({lat}, {lon}) is outside Dëkkal "
                f"coverage area (Dakar urban zone)."
            )

        normalized = location.address
        return lat, lon, normalized

    except GeocoderTimedOut:
        raise ValueError("Geocoding service timed out — please retry")
    except GeocoderServiceError as e:
        raise ValueError(f"Geocoding service error: {str(e)}")


def reverse_geocode(lat: float, lon: float) -> str:
    """Reverse geocode lat/lon to a readable address string."""
    try:
        location = geolocator.reverse(
            (lat, lon),
            language="en",
            exactly_one=True,
            zoom=16,
        )
        if location and location.address:
            return location.address
    except Exception:
        pass
    return f"{lat:.5f}, {lon:.5f}"


def suggest_alternatives(address: str) -> list:
    """Retourne jusqu'à 3 suggestions pour une adresse ambiguë."""
    query = address
    if "dakar" not in address.lower():
        query = f"{address}, Dakar, Senegal"

    try:
        time.sleep(1)  # respecter rate limit Nominatim
        results = geolocator.geocode(
            query,
            exactly_one=False,
            limit=3,
            language="en",
        )
        if not results:
            return []
        return [r.address for r in results]
    except Exception:
        return []
