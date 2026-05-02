"""
Dëkkal — Feature Extraction for 16 Pikine Communes
Source bboxes : mapSenegal R package (official GADM data)
Author : Babacar Ndao
"""
import ee
import pandas as pd
import numpy as np
import sys

ee.Initialize(project='dekkal-04')

# ── GEE ASSETS ───────────────────────────────────────
DEM     = ee.Image('USGS/SRTMGL1_003')
TERRAIN = ee.Algorithms.Terrain(DEM)
JRC     = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence').gt(80)
CHIRPS  = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY').select('precipitation')
S1      = ee.ImageCollection('COPERNICUS/S1_GRD')
CLAY    = ee.Image("projects/soilgrids-isric/clay_mean")
ERA5    = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR")

WATER_THRESHOLD = -20
ORBIT = 'ASCENDING'

SEASONS = [
    ('2015-07-01', '2015-10-31', 2015),
    ('2016-07-01', '2016-10-31', 2016),
    ('2017-07-01', '2017-10-31', 2017),
    ('2018-07-01', '2018-10-31', 2018),
    ('2019-07-01', '2019-10-31', 2019),
    ('2020-07-01', '2020-10-31', 2020),
    ('2021-07-01', '2021-10-31', 2021),
    ('2022-07-01', '2022-10-31', 2022),
    ('2023-07-01', '2023-10-31', 2023),
    ('2024-07-01', '2024-10-31', 2024),
]

# Charger les bboxes officielles
df_bbox = pd.read_csv('pikine_communes_bbox.csv')
print(f"Communes chargées : {len(df_bbox)}")
print(f"Saisons           : {len(SEASONS)}")
print(f"Total samples     : {len(df_bbox) * len(SEASONS)}\n")

def make_geom(row):
    return ee.Geometry.Rectangle([
        row['lon_min'], row['lat_min'],
        row['lon_max'], row['lat_max']
    ])

def get_terrain(geom):
    s = TERRAIN.select(['elevation','slope']) \
        .reduceRegion(reducer=ee.Reducer.mean(),
                      geometry=geom, scale=30).getInfo()
    return {
        'elevation_m': round(s.get('elevation', 10.0) or 10.0, 2),
        'slope_deg'  : round(s.get('slope', 2.0) or 2.0, 2),
    }

def get_soil(geom):
    cs = CLAY.select("clay_0-5cm_mean") \
        .reduceRegion(reducer=ee.Reducer.mean(),
                      geometry=geom, scale=250).getInfo()
    clay = (cs.get('clay_0-5cm_mean') or 205) / 10
    return {'clay_pct': round(clay, 1)}

def get_p99(geom, start, end):
    p = (CHIRPS.filterDate(start, end)
        .filter(ee.Filter.calendarRange(6, 10, 'month'))
        .reduce(ee.Reducer.percentile([95, 99]))
        .reduceRegion(reducer=ee.Reducer.mean(),
                      geometry=geom, scale=5000).getInfo())
    return {
        'p95_mm_day': round(p.get('precipitation_p95', 17.0) or 17.0, 2),
        'p99_mm_day': round(p.get('precipitation_p99', 34.0) or 34.0, 2),
    }

def get_sar(geom, start, end):
    def area(s, e):
        col = (S1.filterBounds(geom)
            .filterDate(s, e)
            .filter(ee.Filter.eq('instrumentMode', 'IW'))
            .filter(ee.Filter.eq('orbitProperties_pass', ORBIT))
            .select('VV'))
        if col.size().getInfo() == 0:
            return 0.0
        mask = col.min().lt(WATER_THRESHOLD).where(JRC, 0)
        r = mask.multiply(ee.Image.pixelArea()) \
            .reduceRegion(reducer=ee.Reducer.sum(),
                          geometry=geom, scale=30,
                          maxPixels=1e8, bestEffort=True).getInfo()
        return round(r.get('VV', 0) / 1e6, 4)

    dry = area('2020-01-01', '2020-02-28')
    wet = area(start, end)
    return {
        'sar_dry_km2'  : dry,
        'sar_wet_km2'  : wet,
        'sar_delta_km2': round(wet - dry, 4),
    }

def get_era5(geom, start, end):
    s = (ERA5.filterDate(start, end)
        .select('volumetric_soil_water_layer_1')
        .mean()
        .reduceRegion(reducer=ee.Reducer.mean(),
                      geometry=geom, scale=11132).getInfo())
    sm = s.get('volumetric_soil_water_layer_1', 0.13) or 0.13
    return {'soil_moisture': round(sm, 4)}

def get_precip(geom, start, end):
    r = (CHIRPS.filterDate(start, end).sum()
        .reduceRegion(reducer=ee.Reducer.mean(),
                      geometry=geom, scale=5000).getInfo())
    return {'precip_mm': round(r.get('precipitation', 0) or 0, 1)}

# ── MAIN LOOP ────────────────────────────────────────
rows = []
total = len(df_bbox) * len(SEASONS)
count = 0

for _, commune in df_bbox.iterrows():
    name = commune['NAME']
    geom = make_geom(commune)

    print(f"\n{'='*60}")
    print(f"Commune : {name}")
    print(f"{'='*60}")

    # Static features — once per commune
    terrain = get_terrain(geom)
    soil    = get_soil(geom)
    print(f"  Terrain: elev={terrain['elevation_m']}m slope={terrain['slope_deg']}° clay={soil['clay_pct']}%")

    for start, end, year in SEASONS:
        count += 1
        sys.stdout.write(f"  [{count:03d}/{total}] {year}... ")
        sys.stdout.flush()

        try:
            p99   = get_p99(geom, start, end)
            sar   = get_sar(geom, start, end)
            era5  = get_era5(geom, start, end)
            precip = get_precip(geom, start, end)

            # Flood label from SAR delta
            flood = int(sar['sar_delta_km2'] > 0.05)

            row = {
                'commune'      : name,
                'year'         : year,
                **terrain,
                **soil,
                **p99,
                **sar,
                **era5,
                **precip,
                'flood'        : flood,
            }
            rows.append(row)
            print(f"elev={terrain['elevation_m']}m p99={p99['p99_mm_day']}mm "
                  f"delta={sar['sar_delta_km2']} flood={flood} ✓")

        except Exception as e:
            print(f"ERROR: {e}")

# ── EXPORT ───────────────────────────────────────────
df = pd.DataFrame(rows)

print(f"\n{'='*60}")
print(f"PIKINE DATASET SUMMARY")
print(f"{'='*60}")
print(f"Total samples : {len(df)}")
print(f"flood=1       : {df['flood'].sum()}")
print(f"flood=0       : {(df['flood']==0).sum()}")
print(f"Balance       : {df['flood'].mean():.1%} positive rate")
print(f"\nPar commune :")
print(df.groupby('commune')['flood'].agg(['count','sum']).rename(
    columns={'count':'années','sum':'flood_1'}
).to_string())

df.to_csv('dekkal_pikine_dataset.csv', index=False)
print(f"\n✓ Sauvegardé → dekkal_pikine_dataset.csv")
print(f"  Shape : {df.shape}")
