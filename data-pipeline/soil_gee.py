"""
Dëkkal — Soil Features via Google Earth Engine
Source : ISRIC SoilGrids via GEE
Author : Babacar Ndao
"""
import ee
import pandas as pd
import numpy as np

ee.Initialize(project='dekkal-04')

dakar_urban = ee.Geometry.Rectangle([-17.52, 14.65, -17.25, 14.85])

clay = ee.Image("projects/soilgrids-isric/clay_mean")
sand = ee.Image("projects/soilgrids-isric/sand_mean")
silt = ee.Image("projects/soilgrids-isric/silt_mean")

bands = ["clay_0-5cm_mean", "clay_5-15cm_mean", "clay_15-30cm_mean"]

rows = []
for band in bands:
    stats = clay.select(band).reduceRegion(
        reducer=ee.Reducer.percentile([10, 50, 90]),
        geometry=dakar_urban,
        scale=250,
        maxPixels=1e8
    ).getInfo()
    # SoilGrids units: g/kg → divide by 10 for %
    row = {"band": band}
    for k, v in stats.items():
        row[k] = round(v / 10, 2) if v else None
    rows.append(row)
    print(f"  {band:<30} : {row}")

# Sand top layer
sand_stats = sand.select("sand_0-5cm_mean").reduceRegion(
    reducer=ee.Reducer.percentile([10, 50, 90]),
    geometry=dakar_urban,
    scale=250,
    maxPixels=1e8
).getInfo()
print(f"\nSand 0-5cm (%) : { {k: round(v/10,2) for k,v in sand_stats.items() if v} }")

# Silt top layer
silt_stats = silt.select("silt_0-5cm_mean").reduceRegion(
    reducer=ee.Reducer.percentile([10, 50, 90]),
    geometry=dakar_urban,
    scale=250,
    maxPixels=1e8
).getInfo()
print(f"Silt 0-5cm (%) : { {k: round(v/10,2) for k,v in silt_stats.items() if v} }")

# Export
df = pd.DataFrame(rows)
df.to_csv("dekkal_soil_gee.csv", index=False)
print("\n✓ Sauvegardé → dekkal_soil_gee.csv")
