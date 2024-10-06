from ipyleaflet.velocity import Velocity
from ipyleaflet import Map, Marker
import xarray as xr
import os
import requests



if not os.path.exists('wind-global.nc'):
  url = 'https://github.com/benbovy/xvelmap/raw/master/notebooks/wind-global.nc'
  r = requests.get(url)
  wind_data = r.content
  with open('wind-global.nc', 'wb') as f:
      f.write(wind_data)

m = Map(center=(45, 2), zoom=4, interpolation='nearest')#,basemap=basemaps.CartoDB.DarkMatter)
display(m)
#ds = xr.open_dataset('wind-global.nc')
'''
wind = Velocity(data=ds,
                zonal_speed='u_wind',
                meridional_speed='v_wind',
                latitude_dimension='lat',
                longitude_dimension='lon',
                velocity_scale=0.01,
                max_velocity=20)
m.add(wind)
'''