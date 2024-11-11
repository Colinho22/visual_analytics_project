import plotly.express as px
import pandas as pd


# Import data from USGS
data = pd.read_csv('https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.csv')


# Drop rows with missing or invalid values in the 'mag' column
data = data.dropna(subset=['mag'])
data = data[data.mag >= 0]


# Create scatter map
fig = px.scatter_geo(data, lat='latitude', lon='longitude', color='mag',
                     hover_name='place', size='mag',
                     title='Earthquakes Around the World', scope='europe')
fig.show()