import pandas as pd

# Charger les labels SAR déjà calculés
df = pd.read_csv('flood_ground_truth_dakar_2015_2024.csv')

# Ajouter les features terrain (constantes pour cette zone)
df['elevation_m']  = 5.45
df['slope_deg']    = 0.66
df['aspect_deg']   = 67.68

# Feature enginering — HAND proxy (plus l'élévation est basse, plus c'est à risque)
df['hand_proxy']   = 1 / (df['elevation_m'] + 0.1)

# Features finales pour XGBoost
features = ['precip_season_mm', 'elevation_m', 'slope_deg', 'hand_proxy']
target   = 'flood_detected'

print("Dataset ML final :")
print(df[features + [target]].to_string(index=False))
print(f"\nShape : {df.shape}")
print(f"Features : {features}")

import ee
import pandas as pd

ee.Initialize(project='dekkal-04')

dakar_urban = ee.Geometry.Rectangle([-17.52, 14.65, -17.25, 14.85])

dem     = ee.Image('USGS/SRTMGL1_003')
terrain = ee.Algorithms.Terrain(dem)

# Extraire par cellule 500m — pas une moyenne globale
grid_stats = terrain.select(['elevation', 'slope']) \
    .reduceRegion(
        reducer=ee.Reducer.percentile([10, 25, 50, 75, 90]),
        geometry=dakar_urban,
        scale=100
    ).getInfo()

print("Distribution élévation Dakar :")
for k, v in sorted(grid_stats.items()):
    print(f"  {k:<30} : {round(v, 2)}")
    
# Créer une grille de points sur Dakar
grid = ee.FeatureCollection.randomPoints(
    region=dakar_urban,
    points=200,
    seed=42
)

# Extraire élévation + pente pour chaque point
terrain_points = terrain.select(['elevation', 'slope']) \
    .sampleRegions(
        collection=grid,
        scale=30,
        geometries=True
    )

# Convertir en DataFrame
features_list = terrain_points.getInfo()['features']
rows = []
for f in features_list:
    coords = f['geometry']['coordinates']
    props  = f['properties']
    rows.append({
        'lon'       : round(coords[0], 4),
        'lat'       : round(coords[1], 4),
        'elevation' : props.get('elevation', None),
        'slope'     : props.get('slope', None),
    })

df_grid = pd.DataFrame(rows)

# Score de risque terrain simple (0-100)
df_grid['terrain_risk'] = (
    (1 - df_grid['elevation'].clip(0, 20) / 20) * 70 +
    (1 - df_grid['slope'].clip(0, 5) / 5) * 30
).round(1)

print(df_grid.sort_values('terrain_risk', ascending=False).head(10).to_string(index=False))
df_grid.to_csv('dekkal_terrain_grid_200pts.csv', index=False)
print(f"\n✓ Grille 200 points sauvegardée")

print("Distribution des scores terrain (200 points) :")
print(df_grid['terrain_risk'].describe().round(2))
print()

# Répartition par catégorie de risque
bins   = [0, 25, 50, 75, 90, 100]
labels = ['Faible', 'Modéré', 'Élevé', 'Très élevé', 'Extrême']
df_grid['risk_class'] = pd.cut(df_grid['terrain_risk'], bins=bins, labels=labels)

print("Répartition par classe de risque :")
print(df_grid['risk_class'].value_counts().sort_index().to_string())
print()

# Combien de points à risque extrême (100/100) ?
extreme = (df_grid['terrain_risk'] == 100).sum()
print(f"Points à risque extrême (100/100) : {extreme}/200 = {extreme/2:.0f}% de la zone")

# Sauvegarder la grille avec classes
df_grid.to_csv('dekkal_terrain_grid_200pts.csv', index=False)

# Résumé pour le pitch
summary = {
    'zone'              : 'Dakar urbain',
    'points_analysés'   : 200,
    'pct_risque_extreme': 59,
    'elevation_mediane' : df_grid['elevation'].median(),
    'slope_mediane'     : df_grid['slope'].median(),
    'source'            : 'SRTM 30m / GEE',
    'date_extraction'   : '2026-04-22'
}

import json
with open('dekkal_terrain_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print(json.dumps(summary, indent=2))


import pandas as pd
import numpy as np

# Charger les deux sources
df_labels  = pd.read_csv('flood_ground_truth_dakar_2015_2024.csv')
df_terrain = pd.read_csv('dekkal_terrain_grid_200pts.csv')

# Stats terrain globales pour enrichir les labels annuels
terrain_stats = {
    'elevation_median' : df_terrain['elevation'].median(),
    'elevation_mean'   : df_terrain['elevation'].mean().round(2),
    'slope_median'     : df_terrain['slope'].median(),
    'pct_extreme_risk' : (df_terrain['terrain_risk'] == 100).mean().round(3),
    'pct_low_elevation': (df_terrain['elevation'] <= 2).mean().round(3),
}

# Enrichir chaque année avec les features terrain
for k, v in terrain_stats.items():
    df_labels[k] = v

# Feature engineering
df_labels['precip_x_risk']    = df_labels['precip_season_mm'] * df_labels['pct_extreme_risk']
df_labels['precip_x_lowelev'] = df_labels['precip_season_mm'] * df_labels['pct_low_elevation']

# Dataset final
features = [
    'precip_season_mm',
    'elevation_mean',
    'slope_median',
    'pct_extreme_risk',
    'pct_low_elevation',
    'precip_x_risk',
    'precip_x_lowelev'
]
target = 'flood_detected'

X = df_labels[features]
y = df_labels[target]

print("Dataset XGBoost v1 — Dëkkal")
print("=" * 55)
print(df_labels[features + [target]].to_string(index=False))
print(f"\nShape    : {X.shape}")
print(f"Flood=1  : {y.sum()} années")
print(f"Flood=0  : {(y==0).sum()} années")

# Sauvegarder
df_labels.to_csv('dekkal_xgboost_dataset_v1.csv', index=False)
print("\n✓ Sauvegardé → dekkal_xgboost_dataset_v1.csv")
