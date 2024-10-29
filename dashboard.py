import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import plotly.express as px
#import plotly.graph_objs as go
import plotly.graph_objects as go
import airportsdata
import pandas as pd
import numpy as np

from api import weather_API as w_Api
from api import airTraffic_API as a_Api

# Erstelle eine Dash-Anwendung
app = dash.Dash(__name__)

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

    #print(weatherData)
    flightData = a_Api.getAirTraffic(min_lat, min_lon, max_lat, max_lon)
    #print(flightData)

    return weatherData, flightData

def getLatLongFromName(name):
    index = airp.isin([name]).any(axis=1).idxmax()
    lat = airp._get_value(index, 'lat')
    lon = airp._get_value(index, 'lon')

    return lat, lon

def genFig(weatherData, flightData, lat, lon):
    # Erstelle die Karte mit Plotly und Mapbox
    fig = px.scatter_mapbox(
        flightData, lat="lat", lon="lon",
        #size="peak_hour",
        zoom=11,
        center={"lat": lat, "lon": lon},
        mapbox_style="open-street-map",  # Alternative Styles: "carto-positron", "stamen-terrain", "open-street-map"
        hover_name="callsign",
    )
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )

    fig.update_traces(marker=dict(
        color='red',  # Set marker color
        opacity=0.7,  # Set marker opacity
        sizeref=100,  # Adjusts size scaling factor
        size=100
    ))

    return fig

def genFig1(weatherData, flightData, lat, lon):
    ##########################
    #NO DETAILVIEW!!!
    ##########################
    fig = go.Figure(go.Scattergeo(
        lat=[lat],
        lon=[lon],
        mode='markers',
        marker=dict(size=10, color='red'),
        #text=['Location']
    ))

    fig.update_layout(
        geo=dict(
            scope='world',  # Choose the scope (world, usa, etc.)
            projection_type='orthographic', #'natural earth',  # Projection type
            showland=True,  # Show land features
            landcolor='lightgray'
        ),
        margin={'l': 0, 'r': 0, 't': 0, 'b': 0}
    )

    return fig

def genFig2(weatherData, flightData, lat, lon):
    fig = go.Figure(go.Scattermapbox(
        lat=[45.5017, 46.8139, 43.6532],   # Example latitudes
        lon=[-73.5673, -71.2082, -79.3832], # Example longitudes
        mode='markers+text',
        marker=go.scattermapbox.Marker(
            #size=100,        # Custom size for all markers
            #color='red',   # Marker color
            symbol='airports',   # Custom symbol

            ##SYMBOL geht nur mit mapbox provided style

            #Kommentar
            # It's important to note that the special icon symbols only work when using a
            # Mapbox-provided style, per the documentation: https://plotly.com/python/scattermapbox/#set-marker-symbols

            ##Die Mapbox Styles (basic,streets, outdoors, light, dark, satellite, satellite-streets) könnten
            #unten im Update unter der style Variable gesetzt werden. Dies wiederum geht aber NUR MIT MAPBOX TOKEN

            #Links:
            #Icons: https://labs.mapbox.com/maki-icons/
            #How to set marker symbols: https://plotly.com/python/tile-scatter-maps/
            #Issue mit Infos: https://github.com/plotly/plotly.py/issues/1804


            angle= 20
        ),
        text=['Montreal', 'Quebec City', 'Toronto'],  # Labels for markers
        textposition="bottom right"  # Position labels near markers
    ))

    # Configure map layout without a token
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",#style="basic",
            center=dict(lat=45.5017, lon=-73.5673),
            zoom=5
        ),
        margin={'l': 0, 'r': 0, 't': 0, 'b': 0}
    )

    return fig


lat, lon = getLatLongFromName('Zurich Airport')
weatherData, flightData =createData(lat, lon)


# Layout für die Dash-App
app.layout = html.Div([
    dcc.Dropdown(airp['name'], 'Zurich Airport', id='airport-dropdown', searchable=True),
    html.H1("Interaktive Karte mit Zoom und Pan-Funktion"),
    dcc.Graph(id="map", figure=genFig2(weatherData, flightData, lat, lon)),
    html.Div("hello", id='dd-output-container')
])

@callback(
    Output('map', 'figure'),
    Input('airport-dropdown', 'value')
)
def update_output(value):
    lat, lon = getLatLongFromName(value)
    weatherData, flightData = createData(lat, lon)
    fig = genFig2(weatherData, flightData, lat, lon)
    return fig

@callback(
    Output('dd-output-container', 'children'),
    Input('airport-dropdown', 'value')
)
def update_output(value):
    lat, lon = getLatLongFromName(value)
    return f'You have selected {value}, lat: {lat}, lon: {lon}'


# Starte die Dash-Anwendung
if __name__ == '__main__':
    app.run_server(debug=True)
    




