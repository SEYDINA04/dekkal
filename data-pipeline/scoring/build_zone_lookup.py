"""
Dëkkal — Zone Risk Lookup Table
Pre-computed zone-level risk scores from XGBoost v1
Used at inference time to contextualize address-level score
Author : Babacar Ndao
"""
import pandas as pd
import numpy as np
import joblib
import json

# Charger modèle v1 (avec SAR)
model    = joblib.load('dekkal_xgboost_v1.pkl')
features = joblib.load('dekkal_xgboost_features.pkl')
df       = pd.read_csv('dekkal_xgboost_training_dataset.csv')

# Score moyen par zone (moyenne des probabilités sur 10 ans)
X = df[features]
df['flood_prob'] = model.predict_proba(X)[:,1]

zone_stats = df.groupby('zone').agg(
    risk_score_mean  = ('flood_prob', lambda x: round(x.mean() * 100, 1)),
    risk_score_max   = ('flood_prob', lambda x: round(x.max() * 100, 1)),
    flood_frequency  = ('flood', 'mean'),
    elevation_mean   = ('elevation_m', 'mean'),
    clay_mean        = ('clay_pct', 'mean'),
).reset_index()

print("Zone Risk Lookup Table :")
print(zone_stats.to_string(index=False))

# Coordonnées centrales par zone
zone_coords = {
    "Dakar_Centre": {"lat_min": 14.72, "lat_max": 14.85,
                     "lon_min": -17.52, "lon_max": -17.38},
    "Pikine"      : {"lat_min": 14.68, "lat_max": 14.78,
                     "lon_min": -17.42, "lon_max": -17.28},
    "Guediawaye"  : {"lat_min": 14.76, "lat_max": 14.85,
                     "lon_min": -17.42, "lon_max": -17.30},
    "Keur_Massar" : {"lat_min": 14.69, "lat_max": 14.76,
                     "lon_min": -17.32, "lon_max": -17.22},
}

# Fusionner stats + coords
lookup = {}
for _, row in zone_stats.iterrows():
    zone = row['zone']
    lookup[zone] = {
        "risk_score_mean" : row['risk_score_mean'],
        "risk_score_max"  : row['risk_score_max'],
        "flood_frequency" : round(row['flood_frequency'], 2),
        "elevation_mean"  : round(row['elevation_mean'], 2),
        "clay_mean"       : round(row['clay_mean'], 2),
        **zone_coords.get(zone, {})
    }

with open('dekkal_zone_lookup.json', 'w') as f:
    json.dump(lookup, f, indent=2)

print("\n✓ Sauvegardé → dekkal_zone_lookup.json")
print(json.dumps(lookup, indent=2))
