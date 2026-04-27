"""
Dëkkal — Dataset Multi-Zones
Étendre le ground truth de 10 → ~40 samples
Zones : Dakar Centre, Pikine, Guédiawaye, Keur Massar
Author : Babacar Ndao
"""
import ee
import pandas as pd
import numpy as np

ee.Initialize(project='dekkal-04')

# ── ZONES GÉOGRAPHIQUES ──────────────────────────────────
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

# Masque eau permanente
jrc = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence').gt(80)
dem = ee.Image('USGS/SRTMGL1_003')
terrain = ee.Algorithms.Terrain(dem)
chirps_all = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY').select('precipitation')

WATER_THRESHOLD = -20
ORBIT = 'ASCENDING'

rows = []

for zone_name, zone_geom in ZONES.items():
    print(f"\n{'='*55}")
    print(f"Zone : {zone_name}")
    print(f"{'='*55}")

    # Features terrain statiques par zone
    terrain_stats = terrain.select(['elevation','slope']) \
        .reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=zone_geom,
            scale=30
        ).getInfo()

    elev = round(terrain_stats.get('elevation', 0), 2)
    slope = round(terrain_stats.get('slope', 0), 2)

    # Baseline SAR sèche
    s1_dry = (ee.ImageCollection('COPERNICUS/S1_GRD')
        .filterBounds(zone_geom)
        .filterDate('2020-01-01', '2020-02-28')
        .filter(ee.Filter.eq('instrumentMode', 'IW'))
        .filter(ee.Filter.eq('orbitProperties_pass', ORBIT))
        .select('VV'))

    if s1_dry.size().getInfo() == 0:
        print(f"  Pas d'images SAR sèches — skip")
        continue

    dry_mask = s1_dry.min().lt(WATER_THRESHOLD).where(jrc, 0)
    dry_area = dry_mask.multiply(ee.Image.pixelArea()) \
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=zone_geom,
            scale=30, maxPixels=1e8, bestEffort=True
        ).getInfo()
    dry_km2 = round(dry_area.get('VV', 0) / 1e6, 3)

    for start, end, year in SEASONS:
        s1 = (ee.ImageCollection('COPERNICUS/S1_GRD')
            .filterBounds(zone_geom)
            .filterDate(start, end)
            .filter(ee.Filter.eq('instrumentMode', 'IW'))
            .filter(ee.Filter.eq('orbitProperties_pass', ORBIT))
            .select('VV'))

        if s1.size().getInfo() == 0:
            continue

        water_mask = s1.min().lt(WATER_THRESHOLD).where(jrc, 0)
        flood_area = water_mask.multiply(ee.Image.pixelArea()) \
            .reduceRegion(
                reducer=ee.Reducer.sum(),
                geometry=zone_geom,
                scale=30, maxPixels=1e8, bestEffort=True
            ).getInfo()
        area_km2 = round(flood_area.get('VV', 0) / 1e6, 3)
        delta = round(area_km2 - dry_km2, 3)
        flood = int(area_km2 > dry_km2 * 1.1 and delta > 0.05)

        # Précipitations
        precip = chirps_all.filterDate(start, end).sum() \
            .reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=zone_geom,
                scale=5000
            ).getInfo()
        precip_mm = round(precip.get('precipitation', 0), 1)

        row = {
            'zone'       : zone_name,
            'year'       : year,
            'elevation'  : elev,
            'slope'      : slope,
            'area_km2'   : area_km2,
            'delta_km2'  : delta,
            'precip_mm'  : precip_mm,
            'flood'      : flood,
        }
        rows.append(row)
        print(f"  {year} : area={area_km2}km² delta={delta} "
              f"precip={precip_mm}mm flood={flood}")

# ── EXPORT ───────────────────────────────────────────────
df = pd.DataFrame(rows)
df.to_csv('dekkal_dataset_zones.csv', index=False)

print(f"\n{'='*55}")
print(f"RÉSUMÉ DATASET MULTI-ZONES")
print(f"{'='*55}")
print(f"Total samples : {len(df)}")
print(f"flood=1       : {df['flood'].sum()}")
print(f"flood=0       : {(df['flood']==0).sum()}")
print(f"\nPar zone :")
print(df.groupby('zone')['flood'].agg(['count','sum']).rename(
    columns={'count':'total','sum':'flood_1'}
).to_string())

print("\n✓ Sauvegardé → dekkal_dataset_zones.csv")
