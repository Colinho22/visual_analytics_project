import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import plotly.express as px
import airportsdata
import pandas as pd
import numpy as np
import dash_leaflet as dl
import dash_leaflet.express as dlx


import gunicorn

from api import weather_API as w_Api
from api import airTraffic_API as a_Api

# Erstelle eine Dash-Anwendung
app = dash.Dash(__name__)
server = app.server

# Beispiel-Daten für die Karte (Koordinaten)
data = px.data.carshare()
#print(data)

airports = airportsdata.load()
airp = pd.DataFrame.from_dict(airports)
airp = airp.drop(index=(['icao', 'iata', 'subd', 'elevation', 'tz', 'lid']))
airp = airp.dropna()
airp = airp.T
#print(airp)

#Init lat und lon
lat, lon = 5,5

def createData(center_lat, center_lon):
    #offset = 3 #ganze Schweiz
    offset = 1
    min_lat = center_lat - offset
    max_lat = center_lat + offset
    min_lon = center_lon - offset
    max_lon = center_lon + offset

    #Create Grid
    #Gridsize 10km
    a = np.linspace(min_lat, max_lat, 2)
    b = np.linspace(min_lon, max_lon, 2)

    weatherData = []
    for i in a:
        for j in b:
            x = w_Api.getWeatherDangerIndex(i,j)
            weatherData.append([i,j,x])
    flightData = a_Api.getAirTrafficDicts(min_lat, min_lon, max_lat, max_lon)   #Output as List of JSON

    return weatherData, flightData

def getLatLongFromName(name):
    index = airp.isin([name]).any(axis=1).idxmax()
    lat = airp._get_value(index, 'lat')
    lon = airp._get_value(index, 'lon')

    return lat, lon

def genFig(weatherData, flightData, lat, lon):
    map = dl.Map([
        dl.TileLayer(),
        # From in-memory geojson. All markers at same point forces spiderfy at any zoom level.
        dl.GeoJSON(data=dlx.dicts_to_geojson(flightData), cluster=True, zoomToBoundsOnClick=True),
        ], center=(lat, lon), zoom=11, style={'height': '80vh'})

    return map
'''

def genFig(weatherData, flightData, lat, lon):
    # Funktion zur Erstellung eines individuellen Icons für die Flugzeuge
    def create_airplane_marker(feature):
        # Setze den Kurswinkel basierend auf dem 'bearing'-Wert im Feature (falls vorhanden)
        bearing = feature['dir']  # Default-Winkel ist 0 Grad, falls 'bearing' fehlt
        icon = {
            "iconUrl": "/assets/airplane.svg",  # Pfad zum Flugzeugsymbol
            "iconSize": [32, 32],  # Größe des Icons
            "iconAnchor": [16, 16],  # Mittelpunkt des Icons
            "popupAnchor": [0, -16],  # Position für das Popup
            "rotateAngle": bearing  # Rotation basierend auf Flugrichtung
        }
        return dl.Marker(position=feature["geometry"]["coordinates"][::-1], icon=icon)

    # Konvertiere flightData zu GeoJSON und passe die Marker und Rotation an
    geojson_data = dlx.dicts_to_geojson(flightData)

    # Erstelle die Map-Komponente mit dem angepassten Icon
    map = dl.Map([
        dl.TileLayer(),
        dl.GeoJSON(
            data=geojson_data,
            cluster=True,
            zoomToBoundsOnClick=True,
            zoomToBounds=True,
            #options=dict(pointToLayer=create_airplane_marker),  # Verwende benutzerdefinierte Marker
        ),
    ], center=(lat, lon), zoom=11, style={'height': '80vh'})

    return map
'''

lat, lon = getLatLongFromName('Zurich Airport')
weatherData, flightData =createData(lat, lon)


# Layout für die Dash-App
app.layout = html.Div([
    html.Div("Bitte Flughafen auswählen", style={'text-align': 'center', 'font-size': 'xx-large', "margin-bottom": "15px"}),
    dcc.Dropdown(airp['name'], 'Zurich Airport', id='airport-dropdown', searchable=True),
    html.Div([genFig(weatherData, flightData, lat, lon)], id="map", style={"margin-left": "15px", "margin-right": "15px","margin-top": "15px", "margin-bottom": "15px"}),
])

@callback(
    Output('map', 'children'),
    Input('airport-dropdown', 'value')
)
def update_output(value):
    lat, lon = getLatLongFromName(value)
    weatherData, flightData = createData(lat, lon)
    fig = [genFig(weatherData, flightData, lat, lon)]
    return fig


# Starte die Dash-Anwendung
if __name__ == '__main__':
    app.run_server(debug=True)
    




