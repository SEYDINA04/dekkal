"""
Dëkkal — Feature Engine v1.3
All geospatial features for a given location
Author : Babacar Ndao
"""
import ee
import datetime
import json
import os

_ee_initialized = False
WATER_THRESHOLD = -20


def _init_ee():
    global _ee_initialized
    if _ee_initialized:
        return
    creds_json = os.getenv("EE_CREDENTIALS")
    if creds_json:
        # Cloud deployment: write credentials file for EE SDK
        creds_dir = os.path.expanduser("~/.config/earthengine")
        os.makedirs(creds_dir, exist_ok=True)
        with open(os.path.join(creds_dir, "credentials"), "w") as f:
            f.write(creds_json)
    ee.Initialize(project="dekkal-04")
    _ee_initialized = True


def get_terrain_features(lat: float, lon: float) -> dict:
    _init_ee()
    dem     = ee.Image('USGS/SRTMGL1_003')
    terrain = ee.Algorithms.Terrain(dem)
    pt      = ee.Geometry.Point([lon, lat])
    buf     = pt.buffer(100)
    stats   = terrain.select(['elevation', 'slope']) \
        .reduceRegion(reducer=ee.Reducer.mean(),
                      geometry=buf, scale=30).getInfo()
    elev  = stats.get('elevation', 10.0) or 10.0
    slope = stats.get('slope', 2.0) or 2.0
    return {
        'elevation_m': round(elev, 2),
        'slope_deg'  : round(slope, 2),
        'hand_proxy' : round(1 / (elev + 0.1), 4),
    }


def get_precipitation_features(lat: float, lon: float) -> dict:
    _init_ee()
    chirps = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY').select('precipitation')
    pt     = ee.Geometry.Point([lon, lat])
    buf    = pt.buffer(5000)
    p      = (chirps
        .filter(ee.Filter.calendarRange(6, 10, 'month'))
        .reduce(ee.Reducer.percentile([95, 99]))
        .reduceRegion(reducer=ee.Reducer.mean(),
                      geometry=buf, scale=5000).getInfo())
    p95 = p.get('precipitation_p95', 17.0) or 17.0
    p99 = p.get('precipitation_p99', 34.0) or 34.0
    return {
        'p95_mm_day': round(p95, 2),
        'p99_mm_day': round(p99, 2),
    }


def get_sar_features(lat: float, lon: float) -> dict:
    _init_ee()
    jrc = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence').gt(80)
    s1  = ee.ImageCollection('COPERNICUS/S1_GRD')
    pt  = ee.Geometry.Point([lon, lat])
    buf = pt.buffer(500)

    def compute_area(start, end):
        col = (s1.filterBounds(buf)
            .filterDate(start, end)
            .filter(ee.Filter.eq('instrumentMode', 'IW'))
            .filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING'))
            .select('VV'))
        if col.size().getInfo() == 0:
            return 0.0
        mask = col.min().lt(WATER_THRESHOLD).where(jrc, 0)
        area = mask.multiply(ee.Image.pixelArea()) \
            .reduceRegion(reducer=ee.Reducer.sum(),
                          geometry=buf, scale=30,
                          maxPixels=1e8, bestEffort=True).getInfo()
        return round(area.get('VV', 0) / 1e6, 4)

    dry = compute_area('2020-01-01', '2020-02-28')
    wet = compute_area('2024-07-01', '2024-10-31')
    return {
        'sar_dry_km2'  : dry,
        'sar_wet_km2'  : wet,
        'sar_delta_km2': round(wet - dry, 4),
    }


def get_soil_features(lat: float, lon: float) -> dict:
    _init_ee()
    clay = ee.Image("projects/soilgrids-isric/clay_mean")
    sand = ee.Image("projects/soilgrids-isric/sand_mean")
    pt   = ee.Geometry.Point([lon, lat])
    buf  = pt.buffer(1000)

    cs = clay.select("clay_0-5cm_mean") \
        .reduceRegion(reducer=ee.Reducer.mean(),
                      geometry=buf, scale=250).getInfo()
    ss = sand.select("sand_0-5cm_mean") \
        .reduceRegion(reducer=ee.Reducer.mean(),
                      geometry=buf, scale=250).getInfo()

    clay_pct = (cs.get('clay_0-5cm_mean') or 205) / 10
    sand_pct = (ss.get('sand_0-5cm_mean') or 647) / 10
    return {
        'clay_pct': round(clay_pct, 1),
        'sand_pct': round(sand_pct, 1),
    }


def get_era5_soil_moisture(lat: float, lon: float) -> dict:
    _init_ee()
    now   = datetime.datetime.utcnow()
    start = (now - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    end   = now.strftime('%Y-%m-%d')
    era5  = (ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR")
        .filterDate(start, end)
        .select('volumetric_soil_water_layer_1'))
    pt  = ee.Geometry.Point([lon, lat])
    buf = pt.buffer(11132)
    stats = era5.mean().reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=buf, scale=11132).getInfo()
    sm = stats.get('volumetric_soil_water_layer_1', 0.13) or 0.13
    return {'soil_moisture_current': round(sm, 4)}


def extract_all_features(lat: float, lon: float) -> dict:
    from api.services.drainage_distance import get_drainage_distance

    terrain  = get_terrain_features(lat, lon)
    precip   = get_precipitation_features(lat, lon)
    sar      = get_sar_features(lat, lon)
    drainage = get_drainage_distance(lat, lon)
    soil     = get_soil_features(lat, lon)
    era5     = get_era5_soil_moisture(lat, lon)

    features = {**terrain, **precip, **sar, **drainage, **soil, **era5}
    features['_lat'] = lat
    features['_lon'] = lon
    features['p99_ensemble'] = features.get('p99_mm_day', 34.0)
    features['p95_ensemble'] = features.get('p95_mm_day', 17.0)
    return features
