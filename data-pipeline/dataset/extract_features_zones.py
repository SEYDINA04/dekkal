"""
Dëkkal — Feature Extraction for 40-Zone Dataset
Extracts all 14 geospatial features for each zone/year sample
to build a proper XGBoost training dataset.
Author : Babacar Ndao
"""
import ee
import pandas as pd
import numpy as np
import sys

ee.Initialize(project='dekkal-04')

# ── GEE ASSETS ───────────────────────────────────────────
DEM     = ee.Image('USGS/SRTMGL1_003')
TERRAIN = ee.Algorithms.Terrain(DEM)
JRC     = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence').gt(80)
CHIRPS  = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY').select('precipitation')
S1      = ee.ImageCollection('COPERNICUS/S1_GRD')
CLAY    = ee.Image("projects/soilgrids-isric/clay_mean")
SAND    = ee.Image("projects/soilgrids-isric/sand_mean")
ERA5    = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR")

WATER_THRESHOLD = -20
ORBIT = 'ASCENDING'

# ── ZONE CENTROIDS ───────────────────────────────────────
ZONES = {
    "Dakar_Centre"  : ee.Geometry.Rectangle([-17.52, 14.72, -17.38, 14.85]),
    "Pikine"        : ee.Geometry.Rectangle([-17.42, 14.68, -17.28, 14.78]),
    "Guediawaye"    : ee.Geometry.Rectangle([-17.42, 14.76, -17.30, 14.85]),
    "Keur_Massar"   : ee.Geometry.Rectangle([-17.35, 14.65, -17.18, 14.77]),
}

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
    ss = SAND.select("sand_0-5cm_mean") \
        .reduceRegion(reducer=ee.Reducer.mean(),
                      geometry=geom, scale=250).getInfo()
    return {
        'clay_pct': round((cs.get('clay_0-5cm_mean') or 205) / 10, 1),
        'sand_pct': round((ss.get('sand_0-5cm_mean') or 647) / 10, 1),
    }

def get_p99(geom, start, end):
    p = (CHIRPS
        .filterDate(start, end)
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

# ── MAIN LOOP ────────────────────────────────────────────
df_zones = pd.read_csv('dekkal_dataset_zones.csv')
rows = []
total = len(ZONES) * len(SEASONS)
count = 0

for zone_name, geom in ZONES.items():
    print(f"\n{'='*55}")
    print(f"Zone : {zone_name}")
    print(f"{'='*55}")

    # Static features — computed once per zone
    terrain = get_terrain(geom)
    soil    = get_soil(geom)

    for start, end, year in SEASONS:
        count += 1
        sys.stdout.write(f"  [{count:02d}/{total}] {zone_name} {year}... ")
        sys.stdout.flush()

        try:
            p99  = get_p99(geom, start, end)
            sar  = get_sar(geom, start, end)
            era5 = get_era5(geom, start, end)

            # Get flood label from existing dataset
            match = df_zones[
                (df_zones['zone'] == zone_name) &
                (df_zones['year'] == year)
            ]
            flood = int(match['flood'].values[0]) if len(match) > 0 else -1
            precip = float(match['precip_mm'].values[0]) if len(match) > 0 else 0.0

            row = {
                'zone'         : zone_name,
                'year'         : year,
                **terrain,
                **soil,
                **p99,
                **sar,
                **era5,
                'precip_mm'    : precip,
                'flood'        : flood,
            }
            rows.append(row)
            print(f"elev={terrain['elevation_m']}m clay={soil['clay_pct']}% "
                  f"p99={p99['p99_mm_day']}mm delta={sar['sar_delta_km2']} "
                  f"flood={flood} ✓")

        except Exception as e:
            print(f"ERROR: {e}")

# ── EXPORT ───────────────────────────────────────────────
df = pd.DataFrame(rows)
df = df[df['flood'] != -1]  # Remove unmatched rows

print(f"\n{'='*55}")
print(f"DATASET SUMMARY")
print(f"{'='*55}")
print(f"Total samples : {len(df)}")
print(f"flood=1       : {df['flood'].sum()}")
print(f"flood=0       : {(df['flood']==0).sum()}")
print(f"Features      : {[c for c in df.columns if c not in ['zone','year','flood']]}")
print(f"\n{df.groupby('zone')['flood'].agg(['count','sum']).to_string()}")

df.to_csv('dekkal_xgboost_training_dataset.csv', index=False)
print("\n✓ Sauvegardé → dekkal_xgboost_training_dataset.csv")
