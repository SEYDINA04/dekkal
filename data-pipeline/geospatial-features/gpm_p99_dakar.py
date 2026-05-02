"""
Dëkkal — GPM IMERG P99 Historical Analysis
Optimized : sample annuels au lieu de toute la collection
Author : Babacar Ndao
"""
import ee
import pandas as pd
import sys

ee.Initialize(project='dekkal-04')

dakar_urban = ee.Geometry.Rectangle([-17.52, 14.65, -17.25, 14.85])

gpm = (ee.ImageCollection("NASA/GPM_L3/IMERG_V07")
    .filterBounds(dakar_urban)
    .filter(ee.Filter.calendarRange(6, 10, 'month'))
    .select('precipitation'))

print(f"GPM total : {gpm.size().getInfo()} images")

# ── P99 PAR ANNÉE (plus rapide que global) ───────────────
print("\nP99 GPM par saison 2015-2024 :")
print("=" * 50)

years = list(range(2015, 2025))
rows  = []

for year in years:
    sys.stdout.write(f"  {year}... ")
    sys.stdout.flush()

    p = (gpm
        .filter(ee.Filter.calendarRange(year, year, 'year'))
        .reduce(ee.Reducer.percentile([95, 99]))
        .reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=dakar_urban,
            scale=11132,
            maxPixels=1e8
        ).getInfo())

    # GPM unit: mm/hr → × 0.5hr = mm/image
    # Pour précip journalière max : garder en mm/hr * 0.5
    p95 = round((p.get('precipitation_p95', 0) or 0) * 0.5 * 24, 1)
    p99 = round((p.get('precipitation_p99', 0) or 0) * 0.5 * 24, 1)
    rows.append({'year': year, 'gpm_p95_mm_day': p95, 'gpm_p99_mm_day': p99})
    print(f"P95={p95}mm  P99={p99}mm ✓")

# ── COMPARAISON GPM vs CHIRPS ────────────────────────────
df_gpm    = pd.DataFrame(rows)
df_chirps = pd.read_csv('dekkal_chirps_p99_dakar.csv')
df_comp   = df_gpm.merge(
    df_chirps[['year','p95_mm_day','p99_mm_day']], on='year')

print("\nComparaison GPM vs CHIRPS P99 :")
print(f"{'Year':<6} {'GPM_P99':>10} {'CHIRPS_P99':>12}")
print("=" * 30)
for _, r in df_comp.iterrows():
    print(f"  {int(r.year):<4} {r.gpm_p99_mm_day:>10.1f} {r.p99_mm_day:>12.1f}")

df_gpm.to_csv('dekkal_gpm_p99_dakar.csv', index=False)
print("\n✓ Sauvegardé → dekkal_gpm_p99_dakar.csv")
