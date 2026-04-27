import pandas as pd
import numpy as np

df = pd.read_csv('flood_ground_truth_dakar_2015_2024.csv')

# Règle simple basée sur les données observées
# flood=1 quand area_km2 > 8.0 OU delta_km2 > 0.5
df['pred_rule'] = ((df['area_km2'] > 8.0) | (df['delta_km2'] > 0.5)).astype(int)

correct = (df['pred_rule'] == df['flood_detected']).sum()
print(f"Accuracy règle logique : {correct}/10 = {correct*10:.0f}%")
print()
print(df[['year','area_km2','delta_km2','precip_season_mm',
          'flood_detected','pred_rule']].to_string(index=False))
