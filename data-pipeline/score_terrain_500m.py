# Créer une grille de points sur Dakar
import ee
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
