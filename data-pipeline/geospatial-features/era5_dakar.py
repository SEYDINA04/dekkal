"""
Dëkkal — ERA5-Land Antecedent Soil Moisture
Feature : soil moisture before flood events
Source  : ECMWF/ERA5_LAND/DAILY_AGGR (GEE)
Author  : Babacar Ndao
"""
import ee
import pandas as pd

ee.Initialize(project='dekkal-04')

dakar_urban = ee.Geometry.Rectangle([-17.52, 14.65, -17.25, 14.85])

# ERA5-Land — couche sol 0-7cm
era5 = (ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR")
    .filterBounds(dakar_urban)
    .filterDate('2015-01-01', '2024-12-31')
    .select('volumetric_soil_water_layer_1'))

print(f"ERA5-Land images disponibles : {era5.size().getInfo()}")

seasons = [
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

rows = []
print("\nHumidité sol ERA5-Land — saisons des pluies :")
print("=" * 55)

for start, end, year in seasons:
    stats = (era5
        .filterDate(start, end)
        .mean()
        .reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=dakar_urban,
            scale=11132,
            maxPixels=1e8
        ).getInfo())

    sm = round(stats.get('volumetric_soil_water_layer_1', 0), 4)
    rows.append({'year': year, 'soil_moisture_mean': sm})
    print(f"  {year} : {sm} m³/m³")

df_sm = pd.DataFrame(rows)

# Fusionner avec ground truth
df_gt = pd.read_csv('flood_ground_truth_dakar_2015_2024.csv')
df_merged = df_gt.merge(df_sm, on='year')

print("\nDataset enrichi :")
print(df_merged[['year','soil_moisture_mean',
                 'precip_season_mm','flood_detected']].to_string(index=False))

df_merged.to_csv('flood_ground_truth_dakar_2015_2024.csv', index=False)
df_sm.to_csv('dekkal_era5_soil_moisture.csv', index=False)
print("\n✓ Ground truth mis à jour → flood_ground_truth_dakar_2015_2024.csv")
print("✓ ERA5 sauvegardé     → dekkal_era5_soil_moisture.csv")
