"""
Dëkkal — Final Dataset Builder
Merge all features into one ML-ready dataset
Author : Babacar Ndao
"""
import pandas as pd

# ground_truth contient déjà p99_mm_day et p95_mm_day
df = pd.read_csv('flood_ground_truth_dakar_2015_2024.csv')
df_gpm = pd.read_csv('dekkal_gpm_p99_dakar.csv')

# Fusionner GPM uniquement
df = df.merge(df_gpm[['year','gpm_p95_mm_day','gpm_p99_mm_day']], on='year')

# Ensemble feature
df['p99_ensemble'] = ((df['p99_mm_day'] + df['gpm_p99_mm_day']) / 2).round(1)
df['p95_ensemble'] = ((df['p95_mm_day'] + df['gpm_p95_mm_day']) / 2).round(1)

features = [
    'precip_season_mm',
    'soil_moisture_mean',
    'area_km2',
    'delta_km2',
    'zscore',
    'p99_ensemble',
    'p95_ensemble',
    'extreme_risk_p99',
]

print("Dataset final Dëkkal v1 :")
print("=" * 65)
print(df[features + ['flood_detected']].to_string(index=False))
print(f"\nShape   : {df[features].shape}")
print(f"flood=1 : {df['flood_detected'].sum()}")
print(f"flood=0 : {(df['flood_detected']==0).sum()}")

df.to_csv('dekkal_final_dataset_v1.csv', index=False)
print("\n✓ Sauvegardé → dekkal_final_dataset_v1.csv")
