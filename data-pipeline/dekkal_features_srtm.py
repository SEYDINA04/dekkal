import ee
ee.Initialize(project='dekkal-04')

dakar_urban = ee.Geometry.Rectangle([-17.52, 14.65, -17.25, 14.85])

dem = ee.Image('USGS/SRTMGL1_003')

# Features terrain par cellule 100m
terrain = ee.Algorithms.Terrain(dem)

stats = terrain.select(['elevation','slope','aspect']) \
    .reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=dakar_urban,
        scale=100
    ).getInfo()

print(stats)
