"""
Dëkkal — Pikine Aggregated Zones
5 zones regroupant les 16 communes — signal SAR et CHIRPS fiable
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

# ── 5 ZONES AGRÉGÉES ─────────────────────────────────
# Communes regroupées par proximité géographique et profil de risque
PIKINE_ZONES = {
    "Pikine_Nord_Dense": {
        # Guinaw Rail Nord+Sud, Daliford, Pikine Ouest
        "bbox": [-17.424, 14.733, -17.378, 14.767],
        "communes": ["Guinaw Rail Nord","Guinaw Rail Sud","Daliford","Pikine Ouest"],
        "flood_profile": "high"
    },
    "Pikine_Centre": {
        # Pikine Est, Pikine Sud, Diack Sao, Djidah Thiaroye Kao
        "bbox": [-17.410, 14.743, -17.362, 14.777],
        "communes": ["Pikine Est","Pikine Sud","Diack Sao","Djidah Thiaroye Kao"],
        "flood_profile": "medium"
    },
    "Thiaroye_Bas_Fond": {
        # Thiaroye Mer, Thiaroye Gare, Diamaguene/Sicap M'Bao
        "bbox": [-17.400, 14.736, -17.340, 14.765],
        "communes": ["Thiaroye Mer","Thiaroye Gare","Diamaguene/Sicap M'Bao"],
        "flood_profile": "high"
    },
    "Yeumbeul_Malika": {
        # Yeumbeul Nord, Yeumbeul Sud, Malika
        "bbox": [-17.373, 14.762, -17.288, 14.820],
        "communes": ["Yeumbeul Nord","Yeumbeul Sud","Malika"],
        "flood_profile": "medium"
    },
    "Keur_Massar_Mbao": {
        # Keur Massar, Mbao
        "bbox": [-17.355, 14.719, -17.288, 14.824],
        "communes": ["Keur Massar","Mbao"],
        "flood_profile": "high"
    },
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

print(f"Zones  : {len(PIKINE_ZONES)}")
print(f"Saisons: {len(SEASONS)}")
print(f"Total  : {len(PIKINE_ZONES) * len(SEASONS)} samples\n")

def get_geom(bbox):
    return ee.Geometry.Rectangle(bbox)

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
    return {'clay_pct': round((cs.get('clay_0-5cm_mean') or 205) / 10, 1)}

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
total = len(PIKINE_ZONES) * len(SEASONS)
count = 0

for zone_name, zone_info in PIKINE_ZONES.items():
    geom = get_geom(zone_info['bbox'])

    print(f"\n{'='*60}")
    print(f"Zone : {zone_name}")
    print(f"Communes : {', '.join(zone_info['communes'])}")
    print(f"{'='*60}")

    terrain = get_terrain(geom)
    soil    = get_soil(geom)
    print(f"  Terrain: elev={terrain['elevation_m']}m "
          f"slope={terrain['slope_deg']}° clay={soil['clay_pct']}%")

    for start, end, year in SEASONS:
        count += 1
        sys.stdout.write(f"  [{count:02d}/{total}] {year}... ")
        sys.stdout.flush()

        try:
            p99    = get_p99(geom, start, end)
            sar    = get_sar(geom, start, end)
            era5   = get_era5(geom, start, end)
            precip = get_precip(geom, start, end)

            flood = int(sar['sar_delta_km2'] > 0.1)

            row = {
                'zone'         : zone_name,
                'communes'     : '|'.join(zone_info['communes']),
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
            print(f"p99={p99['p99_mm_day']}mm delta={sar['sar_delta_km2']} "
                  f"precip={precip['precip_mm']}mm flood={flood} ✓")

        except Exception as e:
            print(f"ERROR: {e}")

# ── SUMMARY ──────────────────────────────────────────
df = pd.DataFrame(rows)

print(f"\n{'='*60}")
print(f"PIKINE ZONES DATASET SUMMARY")
print(f"{'='*60}")
print(f"Total samples : {len(df)}")
print(f"flood=1       : {df['flood'].sum()}")
print(f"flood=0       : {(df['flood']==0).sum()}")
print(f"Balance       : {df['flood'].mean():.1%} positive rate")
print(f"\nPar zone :")
print(df.groupby('zone')[['flood','elevation_m','p99_mm_day',
                           'sar_delta_km2']].agg(
    flood_1=('flood','sum'),
    n=('flood','count'),
    elev=('elevation_m','first'),
    p99=('p99_mm_day','mean'),
    delta_mean=('sar_delta_km2','mean')
).to_string())

df.to_csv('dekkal_pikine_zones_dataset.csv', index=False)
print(f"\n✓ Sauvegardé → dekkal_pikine_zones_dataset.csv")
