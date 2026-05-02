"""
Dëkkal — Simple Feature Cache
Caches GEE features by (lat, lon) rounded to 3 decimals
In-memory for MVP — Redis in production
Author : Babacar Ndao
"""
import json
import hashlib

_cache = {}


def _key(lat: float, lon: float) -> str:
    lat_r = round(lat, 3)
    lon_r = round(lon, 3)
    return f"{lat_r},{lon_r}"


def get_cached_features(lat: float, lon: float) -> dict | None:
    return _cache.get(_key(lat, lon))


def set_cached_features(lat: float, lon: float, features: dict):
    _cache[_key(lat, lon)] = features
    print(f"  [cache] Stored features for ({lat}, {lon})")


def cache_size() -> int:
    return len(_cache)
