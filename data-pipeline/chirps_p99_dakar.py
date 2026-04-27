"""
Dëkkal — CHIRPS Extreme Rainfall Analysis
Feature : P95 / P99 daily precipitation — Extreme Scenario Risk
Source  : UCSB-CHG/CHIRPS/DAILY (GEE) — 1981-present
Author  : Babacar Ndao
"""
import ee
import pandas as pd
import numpy as np

ee.Initialize(project='dekkal-04')

dakar_urban = ee.Geometry.Rectangle([-17.52, 14.65, -17.25, 14.85])

# CHIRPS journalier complet — saison des pluies uniquement (juin-octobre)
chirps = (ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
    .filterBounds(dakar_urban)
    .filter(ee.Filter.calendarRange(6, 10, 'month'))
    .select('precipitation'))

print(f"CHIRPS images (saison pluies 1981-present) : {chirps.size().getInfo()}")

# ── PERCENTILES GLOBAUX ──────────────────────────────────
print("\nCalcul des percentiles globaux 1981-2024...")
percentiles = chirps.reduce(
    ee.Reducer.percentile([50, 75, 90, 95, 99])
).reduceRegion(
    reducer=ee.Reducer.mean(),
    geometry=dakar_urban,
    scale=5000,
    maxPixels=1e8
).getInfo()

print("\nPercentiles précipitations journalières Dakar (saison pluies) :")
print("=" * 55)
for k, v in sorted(percentiles.items()):
    print(f"  {k:<40} : {round(v, 2)} mm/jour")

# ── EXTRACTION P99 PAR ANNÉE ─────────────────────────────
print("\nP99 annuel par saison des pluies :")
print("=" * 55)

years = list(range(2015, 2025))
rows = []

for year in years:
    p99 = (chirps
        .filter(ee.Filter.calendarRange(year, year, 'year'))
        .reduce(ee.Reducer.percentile([95, 99]))
        .reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=dakar_urban,
            scale=5000,
            maxPixels=1e8
        ).getInfo())

    p95_val = round(p99.get('precipitation_p95', 0), 2)
    p99_val = round(p99.get('precipitation_p99', 0), 2)
    rows.append({'year': year, 'p95_mm_day': p95_val, 'p99_mm_day': p99_val})
    print(f"  {year} : P95={p95_val}mm  P99={p99_val}mm")

df = pd.DataFrame(rows)

# ── EXTREME SCENARIO RISK ────────────────────────────────
# Drainage capacity proxy basé sur sol + terrain Dakar
# Sand 65% + Clay 20% + slope ~0° → capacité drainage estimée
DRAINAGE_CAPACITY = 25.0  # mm/jour — proxy conservateur zone urbaine plate

df['drainage_capacity_mm'] = DRAINAGE_CAPACITY
df['extreme_risk_p99'] = (
    ((df['p99_mm_day'] - DRAINAGE_CAPACITY) / DRAINAGE_CAPACITY * 100)
    .clip(lower=0)
    .round(1)
)

print(f"\nDrainage capacity estimée : {DRAINAGE_CAPACITY} mm/jour")
print("\nExtreme Scenario Risk par année :")
print(df[['year','p95_mm_day','p99_mm_day',
          'extreme_risk_p99']].to_string(index=False))

# ── FUSION GROUND TRUTH ──────────────────────────────────
df_gt = pd.read_csv('flood_ground_truth_dakar_2015_2024.csv')
df_merged = df_gt.merge(df[['year','p95_mm_day','p99_mm_day',
                              'extreme_risk_p99']], on='year')

print("\nDataset enrichi flood=1 vs flood=0 :")
print(df_merged[['year','p99_mm_day','extreme_risk_p99',
                 'flood_detected']].to_string(index=False))

df_merged.to_csv('flood_ground_truth_dakar_2015_2024.csv', index=False)
df.to_csv('dekkal_chirps_p99_dakar.csv', index=False)

print("\n✓ Ground truth mis à jour → flood_ground_truth_dakar_2015_2024.csv")
print("✓ CHIRPS P99 sauvegardé  → dekkal_chirps_p99_dakar.csv")
