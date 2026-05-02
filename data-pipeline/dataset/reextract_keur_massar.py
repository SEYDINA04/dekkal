"""
Dëkkal — Re-extraction Keur Massar
Corrected bbox — residential flood zone only
Author : Babacar Ndao
"""
import ee
import pandas as pd
import sys

ee.Initialize(project='dekkal-04')

DEM     = ee.Image('USGS/SRTMGL1_003')
TERRAIN = ee.Algorithms.Terrain(DEM)
JRC     = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence').gt(80)
CHIRPS  = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY').select('precipitation')
S1      = ee.ImageCollection('COPERNICUS/S1_GRD')
CLAY    = ee.Image("projects/soilgrids-isric/clay_mean")
ERA5    = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR")

WATER_THRESHOLD = -20
ORBIT = 'ASCENDING'

# Bbox corrigée — zone résidentielle inondable uniquement
KM = ee.Geometry.Rectangle([-17.32, 14.69, -17.22, 14.76])

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

# Static features
terrain_stats = TERRAIN.select(['elevation','slope']) \
    .reduceRegion(reducer=ee.Reducer.mean(),
                  geometry=KM, scale=30).getInfo()
clay_stats = CLAY.select("clay_0-5cm_mean") \
    .reduceRegion(reducer=ee.Reducer.mean(),
                  geometry=KM, scale=250).getInfo()

elev  = round(terrain_stats.get('elevation', 10.0) or 10.0, 2)
slope = round(terrain_stats.get('slope', 2.0) or 2.0, 2)
clay  = round((clay_stats.get('clay_0-5cm_mean') or 205) / 10, 1)

print(f"Keur Massar corrigé — elev={elev}m slope={slope}° clay={clay}%")
print("=" * 55)

rows = []

for start, end, year in SEASONS:
    sys.stdout.write(f"  {year}... ")
    sys.stdout.flush()

    # P99
    p = (CHIRPS.filterDate(start, end)
        .filter(ee.Filter.calendarRange(6, 10, 'month'))
        .reduce(ee.Reducer.percentile([95, 99]))
        .reduceRegion(reducer=ee.Reducer.mean(),
                      geometry=KM, scale=5000).getInfo())
    p95 = round(p.get('precipitation_p95', 17.0) or 17.0, 2)
    p99 = round(p.get('precipitation_p99', 34.0) or 34.0, 2)

    # SAR
    def area(s, e):
        col = (S1.filterBounds(KM)
            .filterDate(s, e)
            .filter(ee.Filter.eq('instrumentMode', 'IW'))
            .filter(ee.Filter.eq('orbitProperties_pass', ORBIT))
            .select('VV'))
        if col.size().getInfo() == 0:
            return 0.0
        mask = col.min().lt(WATER_THRESHOLD).where(JRC, 0)
        r = mask.multiply(ee.Image.pixelArea()) \
            .reduceRegion(reducer=ee.Reducer.sum(),
                          geometry=KM, scale=30,
                          maxPixels=1e8, bestEffort=True).getInfo()
        return round(r.get('VV', 0) / 1e6, 4)

    dry   = area('2020-01-01', '2020-02-28')
    wet   = area(start, end)
    delta = round(wet - dry, 4)

    # ERA5
    sm_stats = (ERA5.filterDate(start, end)
        .select('volumetric_soil_water_layer_1')
        .mean()
        .reduceRegion(reducer=ee.Reducer.mean(),
                      geometry=KM, scale=11132).getInfo())
    sm = round(sm_stats.get('volumetric_soil_water_layer_1', 0.13) or 0.13, 4)

    # CHIRPS seasonal
    precip_stats = (CHIRPS.filterDate(start, end)
        .sum()
        .reduceRegion(reducer=ee.Reducer.mean(),
                      geometry=KM, scale=5000).getInfo())
    precip = round(precip_stats.get('precipitation', 0) or 0, 1)

    # Flood label — basé sur delta SAR (seuil corrigé pour KM)
    flood = int(delta > 0.1)

    rows.append({
        'zone': 'Keur_Massar', 'year': year,
        'elevation_m': elev, 'slope_deg': slope,
        'clay_pct': clay, 'sand_pct': 64.7,
        'p95_mm_day': p95, 'p99_mm_day': p99,
        'sar_dry_km2': dry, 'sar_wet_km2': wet,
        'sar_delta_km2': delta,
        'soil_moisture': sm, 'precip_mm': precip,
        'flood': flood,
    })
    print(f"elev={elev}m p99={p99}mm delta={delta} flood={flood} ✓")

df_km = pd.DataFrame(rows)
print(f"\nKeur Massar flood=1 : {df_km['flood'].sum()}/10")
print(df_km[['year','sar_delta_km2','precip_mm','flood']].to_string(index=False))

# Mettre à jour le dataset principal
df_main = pd.read_csv('dekkal_xgboost_training_dataset.csv')
df_main = df_main[df_main['zone'] != 'Keur_Massar']
df_main = pd.concat([df_main, df_km], ignore_index=True)
df_main.to_csv('dekkal_xgboost_training_dataset.csv', index=False)
print(f"\n✓ Dataset mis à jour → dekkal_xgboost_training_dataset.csv")
print(f"Total : {len(df_main)} samples | flood=1: {df_main['flood'].sum()}")
