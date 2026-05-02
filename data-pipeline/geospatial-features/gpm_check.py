"""
Dëkkal — GPM IMERG availability check
Source : NASA/GPM_L3/IMERG_V07
Author : Babacar Ndao
"""
import ee
import datetime

ee.Initialize(project='dekkal-04')

dakar = ee.Geometry.Rectangle([-17.52, 14.65, -17.25, 14.85])

# GPM IMERG Final Run — journalier
gpm_daily = (ee.ImageCollection("NASA/GPM_L3/IMERG_V07")
    .filterBounds(dakar)
    .filterDate('2024-01-01', '2024-12-31')
    .select('precipitation'))

print(f"GPM IMERG images 2024 : {gpm_daily.size().getInfo()}")

# Dernière image disponible
latest = gpm_daily.sort('system:time_start', False).first()
props  = latest.getInfo()['properties']
import datetime
ts = props.get('system:time_start', 0)
date = datetime.datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M')
print(f"Dernière image : {date}")

# Précipitations récentes sur Dakar
recent = (gpm_daily
    .filterDate('2024-08-01', '2024-10-31')
    .sum()
    .reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=dakar,
        scale=11132
    ).getInfo())

precip = round(recent.get('precipitation', 0), 1)
print(f"Précip cumulée août-oct 2024 : {precip} mm")
