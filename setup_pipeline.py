#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#
#   # ── ORCHESTRATION LAYER ────────────────────────────────────────────
#   "prefect",            # DAG scheduling, retries, logging — pipeline orchestrator
#
#   # ── DATA LAYER — satellite & climate sources ───────────────────────
#   "earthaccess",        # NASA EarthData API — downloads SRTM 30m + GPM IMERG NRT
#   "cdsapi",             # Copernicus Climate Data Store API — downloads ERA5-Land hourly
#   "odc-stac",           # Open Data Cube STAC — accesses Sentinel-1/2 via Digital Earth Africa
#   "pystac-client",      # STAC catalog client — queries satellite collections
#   "earthengine-api",    # Google Earth Engine — downloads CHIRPS daily 1981-present
#   "sentinelsat",        # ESA Copernicus Hub — direct Sentinel-1 SAR download
#   "requests",           # HTTP client — SoilGrids REST API (Ksat, clay, porosity)
#
#   # ── PROCESSING LAYER — raster & vector ops ─────────────────────────
#   "rasterio",           # GeoTIFF read/write, reprojection, resampling to 100m grid
#   "pysheds",            # DEM hydrological analysis — TWI, HAND, flow accumulation
#   "geopandas",          # Vector data ops — shapefiles, spatial joins, PostGIS I/O
#   "osmnx",              # OpenStreetMap extraction — buildings, roads, drainage networks
#   "shapely",            # Geometry engine — polygon ops, spatial predicates
#
#   # ── STORAGE LAYER ──────────────────────────────────────────────────
#   "minio",              # MinIO Python client — raw GeoTIFF rasters + model artifacts
#   "pyarrow",            # Parquet read/write — columnar storage for ML feature tables
#   "psycopg2-binary",    # PostgreSQL driver — connects to PostGIS score grid database
#   "sqlalchemy",         # ORM + connection pooling — database abstraction layer
#   "geoalchemy2",        # PostGIS extension for SQLAlchemy — geospatial queries
#
#   # ── FEATURE ENGINEERING LAYER ─────────────────────────────────────
#   "xarray",             # N-dimensional arrays — handles NetCDF/GRIB (ERA5, CHIRPS)
#   "cfgrib",             # GRIB file decoder — ERA5 native format parser
#   "numpy",              # Array operations — raster math, feature computation
#   "pandas",             # Tabular data — assembles final ML feature dataset
#   "scipy",              # Scientific computing — SPI index, statistical transforms
#
#   # ── MODEL LAYER ────────────────────────────────────────────────────
#   "scikit-learn",       # ML pipeline — preprocessing, cross-validation, metrics
#   "xgboost",            # XGBoost classifier — static flood vulnerability scorer
#   "torch",              # PyTorch — LSTM nowcasting model (3h/6h/12h forecast)
#
#   # ── SERVING LAYER ──────────────────────────────────────────────────
#   "fastapi",            # REST API framework — /score, /forecast, /batch endpoints
#   "uvicorn",            # ASGI server — runs FastAPI in production
#   "redis",              # Redis client — score cache TTL 3h + rate limiting
#
#   # ── STREAM LAYER ───────────────────────────────────────────────────
#   "celery",             # Async task queue — alert workers, SMS/email dispatch (Infobip)
#
#   # ── MODEL MONITORING LAYER ─────────────────────────────────────────
#   "evidently",          # Data drift + model drift — triggers Prefect retrain DAG
#
#   # ── LOGGING LAYER ──────────────────────────────────────────────────
#   "loguru",             # Structured logging — console + file rotation + JSON + async
# ]
# ///

"""
Dekkal - Full Pipeline Setup & Dependency Check
===========================================================
Author  : Babacar Ndao - Tech & AI Lead
Project : Dekkal (MEST Africa EIT 2026)
Stack   : Python 3.11 . uv . Prefect . FastAPI . PostGIS . Redis

Pipeline layers covered:
  1. Orchestration  - Prefect DAGs
  2. Data           - NASA / ESA / GEE / OSM / SoilGrids
  3. Processing     - rasterio / pysheds / geopandas / shapely
  4. Storage        - MinIO / Parquet / PostGIS
  5. Features       - xarray / pandas / scipy
  6. Models         - XGBoost (static) + PyTorch LSTM (nowcasting)
  7. Validation     - scikit-learn metrics + spatial CV
  8. Serving        - FastAPI + Redis cache
  9. Stream         - Redis Streams (MVP) -> Kafka (Phase 2)
 10. Monitoring     - evidently drift detection + retrain trigger
 11. Logging        - loguru structured logging

Run with (no pyproject.toml needed):
    uv run setup_pipeline.py

Tip - disable Prefect telemetry:
    export DO_NOT_TRACK=1
"""

import sys

LAYERS = [
    # (import_name, pkg_name, layer, description)

    # ORCHESTRATION
    ("prefect",       "prefect",         "Orchestration", "DAG scheduling . retries . logging"),

    # DATA LAYER
    ("earthaccess",   "earthaccess",     "Data",          "NASA EarthData - SRTM 30m + GPM IMERG NRT"),
    ("cdsapi",        "cdsapi",          "Data",          "Copernicus CDS - ERA5-Land hourly reanalysis"),
    ("odc",           "odc-stac",        "Data",          "Digital Earth Africa - Sentinel-1/2 pre-processed"),
    ("pystac_client", "pystac-client",   "Data",          "STAC catalog client - satellite collection queries"),
    ("ee",            "earthengine-api", "Data",          "Google Earth Engine - CHIRPS daily 1981-present"),
    ("sentinelsat",   "sentinelsat",     "Data",          "ESA Copernicus Hub - Sentinel-1 SAR direct download"),
    ("requests",      "requests",        "Data",          "HTTP client - SoilGrids REST API (Ksat, clay, porosity)"),

    # PROCESSING LAYER
    ("rasterio",      "rasterio",        "Processing",    "GeoTIFF I/O . reprojection . resample to 100m grid"),
    ("pysheds",       "pysheds",         "Processing",    "DEM hydrology - TWI . HAND . flow accumulation"),
    ("geopandas",     "geopandas",       "Processing",    "Vector ops - shapefiles . spatial joins . PostGIS I/O"),
    ("osmnx",         "osmnx",           "Processing",    "OpenStreetMap - buildings . roads . drainage networks"),
    ("shapely",       "shapely",         "Processing",    "Geometry engine - polygon ops . spatial predicates"),

    # STORAGE LAYER
    ("minio",         "minio",           "Storage",       "MinIO client - raw GeoTIFF rasters + model artifacts"),
    ("pyarrow",       "pyarrow",         "Storage",       "Parquet I/O - columnar ML feature tables"),
    ("psycopg2",      "psycopg2-binary", "Storage",       "PostgreSQL driver - PostGIS score grid connection"),
    ("sqlalchemy",    "sqlalchemy",      "Storage",       "ORM + connection pooling - DB abstraction layer"),
    ("geoalchemy2",   "geoalchemy2",     "Storage",       "PostGIS extension for SQLAlchemy - geospatial queries"),

    # FEATURE ENGINEERING
    ("xarray",        "xarray",          "Features",      "N-D arrays - NetCDF/GRIB handler for ERA5 + CHIRPS"),
    ("cfgrib",        "cfgrib",          "Features",      "GRIB decoder - ERA5 native format parser"),
    ("numpy",         "numpy",           "Features",      "Array ops - raster math . feature computation"),
    ("pandas",        "pandas",          "Features",      "Tabular data - assembles final ML feature dataset"),
    ("scipy",         "scipy",           "Features",      "Scientific computing - SPI index . statistical transforms"),

    # MODEL LAYER
    ("sklearn",       "scikit-learn",    "Model",         "ML pipeline - preprocessing . CV . AUC-ROC . F1"),
    ("xgboost",       "xgboost",         "Model",         "XGBoost classifier - static flood vulnerability score"),
    ("torch",         "torch",           "Model",         "PyTorch - LSTM nowcasting model (3h/6h/12h horizon)"),

    # SERVING LAYER
    ("fastapi",       "fastapi",         "Serving",       "REST API - /score . /forecast . /batch endpoints"),
    ("uvicorn",       "uvicorn",         "Serving",       "ASGI server - runs FastAPI in production"),
    ("redis",         "redis",           "Serving",       "Redis client - score cache TTL 3h . rate limiting"),

    # STREAM LAYER
    ("celery",        "celery",          "Stream",        "Async workers - alert dispatch . SMS . email (Infobip)"),

    # MODEL MONITORING
    ("evidently",     "evidently",       "Monitoring",    "Drift detection - data shift . score distribution . retrain trigger"),

    # LOGGING
    ("loguru",        "loguru",          "Logging",       "Structured logging - console . file rotation . JSON . async"),
]


def colored(text, code):
    return f"\033[{code}m{text}\033[0m"


def print_layer_header(name):
    print(f"\n  {colored(f'── {name}', '2;37')}")


print(colored("\nDekkal - Pipeline Dependency Check", "1;36"))
print(colored("=" * 62, "2;37"))

ok = 0
fail = 0
current_layer = None

for import_name, pkg_name, layer, desc in LAYERS:
    if layer != current_layer:
        print_layer_header(layer)
        current_layer = layer

    try:
        __import__(import_name)
        status = colored("  OK  ", "32")
        ok += 1
    except ImportError:
        status = colored("  FAIL", "31")
        fail += 1

    print(f"{status}  {pkg_name:<22}  {colored(desc, '2;37')}")

print(colored("\n" + "=" * 62, "2;37"))
print(f"\n  {colored(str(ok), '32')} ok  .  {colored(str(fail), '31')} failed  .  {ok + fail} total\n")

if fail == 0:
    print(colored("  All good - Dekkal pipeline ready to run.\n", "1;32"))
else:
    print(colored(f"  {fail} package(s) missing - check errors above.\n", "1;31"))
    sys.exit(1)
