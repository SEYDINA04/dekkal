"""
Dëkkal — Ground Truth Labels Pipeline
GEE Flood Detection — Dakar Urban Zone
Author  : Babacar Ndao (CTO)
Project : dekkal-04
"""

import ee
import datetime
import pandas as pd

# ─────────────────────────────────────────────
# 0. INITIALISATION
# ─────────────────────────────────────────────
ee.Initialize(project='dekkal-04')

# Zones géographiques
dakar        = ee.Geometry.Rectangle([-17.6,  14.6,  -17.1, 14.95])
dakar_urban  = ee.Geometry.Rectangle([-17.52, 14.65, -17.25, 14.85])

# Paramètres SAR
WATER_THRESHOLD = -20        # dB — en dessous = eau
ORBIT           = 'ASCENDING'
S1_MODE         = 'IW'

# Masque eau permanente (océan, lacs)
jrc            = ee.Image('JRC/GSW1_4/GlobalSurfaceWater')
permanent_water = jrc.select('occurrence').gt(80)

print("✓ GEE initialisé")
print(f"  Projet     : dekkal-04")
print(f"  Zone       : Dakar urbain [-17.52, 14.65, -17.25, 14.85]")
print(f"  Seuil SAR  : {WATER_THRESHOLD} dB")
print(f"  Orbite     : {ORBIT}\n")


# ─────────────────────────────────────────────
# 1. FONCTION DÉTECTION INONDATION
# ─────────────────────────────────────────────
def detect_flood(start, end, label, method='min'):
    """
    Détecte les zones inondées via Sentinel-1 SAR.
    
    method='mean' : surface moyenne sur la période
    method='min'  : pic d'inondation (recommandé pour labels)
    """
    collection = (ee.ImageCollection('COPERNICUS/S1_GRD')
        .filterBounds(dakar_urban)
        .filterDate(start, end)
        .filter(ee.Filter.eq('instrumentMode', S1_MODE))
        .filter(ee.Filter.eq('orbitProperties_pass', ORBIT))
        .select('VV'))

    n = collection.size().getInfo()

    if n == 0:
        print(f"⚠️  {label} : aucune image disponible")
        return 0.0

    # Agrégation temporelle
    img = collection.min() if method == 'min' else collection.mean()

    # Masque eau
    water_mask = img.lt(WATER_THRESHOLD).where(permanent_water, 0)

    # Surface en km²
    area = water_mask.multiply(ee.Image.pixelArea()) \
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=dakar_urban,
            scale=30,
            maxPixels=1e8,
            bestEffort=True
        ).getInfo()

    km2 = round(area.get('VV', 0) / 1e6, 2)
    print(f"  {label:<45} {km2:>8.2f} km²  ({n} images, method={method})")
    return km2


# ─────────────────────────────────────────────
# 2. RÉFÉRENCE SÈCHE (baseline)
# ─────────────────────────────────────────────
print("=" * 65)
print("RÉFÉRENCE — PÉRIODE SÈCHE")
print("=" * 65)

dry_mean = detect_flood('2020-01-01', '2020-02-28', 'Sèche jan-fév 2020 (mean)', method='mean')
dry_min  = detect_flood('2020-01-01', '2020-02-28', 'Sèche jan-fév 2020 (min)',  method='min')


# ─────────────────────────────────────────────
# 3. DÉTECTION PAR SAISON DES PLUIES
# ─────────────────────────────────────────────
print("\n" + "=" * 65)
print("DÉTECTION INONDATIONS — SAISONS DES PLUIES")
print("=" * 65)

seasons = [
    ('2015-07-01', '2015-10-31', '2015'),
    ('2016-07-01', '2016-10-31', '2016'),
    ('2017-07-01', '2017-10-31', '2017'),
    ('2018-07-01', '2018-10-31', '2018'),
    ('2019-07-01', '2019-10-31', '2019'),
    ('2020-07-01', '2020-10-31', '2020'),
    ('2021-07-01', '2021-10-31', '2021'),
    ('2022-07-01', '2022-10-31', '2022'),
    ('2023-07-01', '2023-10-31', '2023'),
    ('2024-07-01', '2024-10-31', '2024'),
]

results = []
for start, end, year in seasons:
    area = detect_flood(start, end, f'Saison pluies {year} (min)', method='min')
    delta = round(area - dry_min, 2)
    flood_detected = delta > 0.1  # seuil minimum significatif
    results.append({
        'year'          : int(year),
        'start'         : start,
        'end'           : end,
        'area_km2'      : area,
        'delta_km2'     : delta,
        'flood_detected': int(flood_detected)
    })


# ─────────────────────────────────────────────
# 4. LABELS CHIRPS — PRÉCIPITATIONS ASSOCIÉES
# ─────────────────────────────────────────────
print("\n" + "=" * 65)
print("PRÉCIPITATIONS CHIRPS — SAISON DES PLUIES")
print("=" * 65)

chirps_all = (ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
    .filterBounds(dakar_urban)
    .select('precipitation'))

for r in results:
    flood_date = ee.Date(r['end'])
    cumul = (chirps_all
        .filterDate(
            ee.Date(r['start']),
            ee.Date(r['end'])
        )
        .sum()
        .reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=dakar_urban,
            scale=5000
        ).getInfo())

    r['precip_season_mm'] = round(cumul.get('precipitation', 0), 1)
    print(f"  {r['year']} : {r['precip_season_mm']} mm/saison | "
          f"delta={r['delta_km2']} km² | flood={r['flood_detected']}")


# ─────────────────────────────────────────────
# 5. DATASET FINAL
# ─────────────────────────────────────────────
print("\n" + "=" * 65)
print("DATASET GROUND TRUTH — RÉSUMÉ")
print("=" * 65)

df = pd.DataFrame(results)
df['source_sar']   = 'Sentinel-1_GRD'
df['source_precip'] = 'CHIRPS_DAILY'
df['zone']         = 'Dakar_urban'
df['threshold_db'] = WATER_THRESHOLD

print(df[['year','area_km2','delta_km2','precip_season_mm','flood_detected']].to_string(index=False))

# Export CSV
df.to_csv('flood_ground_truth_dakar_2015_2024.csv', index=False)
print("\n✓ Sauvegardé → flood_ground_truth_dakar_2015_2024.csv")

# Statistiques
n_flood    = df['flood_detected'].sum()
n_no_flood = len(df) - n_flood
print(f"\n  Années avec inondation détectée : {n_flood}")
print(f"  Années sans inondation          : {n_no_flood}")
print(f"  Précipitation moyenne (flood=1) : "
      f"{df[df.flood_detected==1]['precip_season_mm'].mean():.1f} mm")
print(f"  Précipitation moyenne (flood=0) : "
      f"{df[df.flood_detected==0]['precip_season_mm'].mean():.1f} mm")
      
# ─────────────────────────────────────────────
# 6. NORMALISATION Z-SCORE
# ─────────────────────────────────────────────
import numpy as np

areas     = df['area_km2'].values
df['zscore']       = (areas - areas.mean()) / areas.std()
df['flood_zscore'] = (df['zscore'] > 0.5).astype(int)

print("\n" + "=" * 65)
print("LABELS NORMALISÉS — Z-SCORE")
print("=" * 65)
print(df[['year','area_km2','zscore','precip_season_mm','flood_zscore']].to_string(index=False))

# Sauvegarder version finale
df.to_csv('flood_ground_truth_dakar_2015_2024.csv', index=False)
print("\n✓ Dataset final sauvegardé avec z-score")
