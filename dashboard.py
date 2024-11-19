import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output, State
import airportsdata
import pandas as pd
import numpy as np
import dash_leaflet as dl
import dash_leaflet.express as dlx
from sklearn.cluster import KMeans


import gunicorn

from api import weather_API as w_Api
from api import airTraffic_API as a_Api

# Erstelle eine Dash-Anwendung
app = dash.Dash(__name__)
server = app.server

#Get Airports Data
airports = airportsdata.load()
airp = pd.DataFrame.from_dict(airports)
airp = airp.drop(index=(['icao', 'iata', 'subd', 'elevation', 'tz', 'lid']))
airp = airp.dropna()
airp = airp.T

#Init lat und lon
lat, lon = 5,5

def createData(center_lat, center_lon):
    #offset = 3 #ganze Schweiz
    offset = 1
    #-90 to 90 for latitude and -180 to 180 for longitude
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
    flightData = a_Api.getAirTrafficDicts(min_lat, min_lon, max_lat, max_lon)

    return weatherData, flightData

def listToGeoJson(points):
    points = [point.tolist() if not isinstance(point, list) else point for point in points]
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates":point
                },
                "properties": {}
            }for point in points
        ]
    }

    return geojson_data


def createGlobalData():
    weatherData = []
    ####################################################################################################################
    #Die globalen Daten, welche für das Clustering verwendet werden, werden nur noch lokal bezogen.
    #Bie wiederholtem Einsazt der gratis API kommt es sehr schnell zu zu hohen Abfragezahlen und somit zum Unterbruch
    ####################################################################################################################

    #-90 to 90 for latitude and -180 to 180 for longitude
    #flightData = a_Api.getAirTrafficDicts(-90, -180, 90, 180)
    #geojson = dlx.dicts_to_geojson(flightData)

    ####################################################################################################################
    #Als Alternative wird das File flobalGeoJson geladen, welches aus demselben globalen Aufruf enstand
    ####################################################################################################################
    import geojson
    with open('assets/globalGeojson') as f:
        geojson = geojson.load(f)
    ####################################################################################################################


    listOfPlanes = []
    for item in geojson['features']:
        listOfPlanes.append(item["geometry"]["coordinates"])

    # 7 Kontinente
    continentClusters = KMeans(n_clusters=7, random_state=22).fit(listOfPlanes)
    # 195 Countries
    countryClusters = KMeans(n_clusters=195, random_state=22).fit(listOfPlanes)

    contOut = [[round(float(i), 4) for i in nested] for nested in continentClusters.cluster_centers_]
    countOut = [[round(float(i), 4) for i in nested] for nested in countryClusters.cluster_centers_]

    #convert back to Geojson for the dash_leaflet
    contGeoJson = listToGeoJson(contOut)
    countGeoJson = listToGeoJson(countOut)

    return contGeoJson, countGeoJson

def getLatLongFromName(name):
    index = airp.isin([name]).any(axis=1).idxmax()
    lat = airp._get_value(index, 'lat')
    lon = airp._get_value(index, 'lon')

    return lat, lon

def genFig(weatherData, flightData, lat, lon):
    map = dl.Map([
        dl.TileLayer(),
        dl.GeoJSON(data=dlx.dicts_to_geojson(flightData), cluster=True, zoomToBoundsOnClick=True),
        ], center=(lat, lon), zoom=11, style={'height': '80vh'})

    return map

def genMiniMap(activeClusters, zoom):
    map = dl.Map([
        dl.TileLayer(),
        dl.GeoJSON(data=activeClusters, cluster=True, zoomToBoundsOnClick=True, id = "geojson_layer"),
        ], center=(lat, lon), zoom=zoom, style={'height': '30vh'}, id="miniMap", zoomControl=False)

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
contClusters, countClusters = createGlobalData()

app.layout = html.Div(
    style={'height': '100vh', 'width': '100vw', 'overflow': 'hidden','margin': '0','padding': '0', 'box-sizing': 'border-box'},
    children=[

        # Left Side (Top Left and Bottom Left)
        html.Div(style={'width': '75%', 'float': 'left', 'height': '100%'}, children=[

            # Top Left (Main Frame)
            html.Div(
                style={
                    'height': '75%',  # 3/4 of the height
                    'width': '100%',  # Full width of left side (75%)
                    'background-color': 'lightblue',  # Optional color for visibility
                },
                children=html.Div([genFig(weatherData, flightData, lat, lon)], id="map")
            ),

            # Bottom Left
            html.Div(
                style={
                    'height': '21%',  # 1/4 of the height - 4% so not scrollable
                    'width': '100%',  # Full width of left side (75%)
                    'background-color': 'lightgray',  # Optional color for visibility
                },
                children=" "
            )
        ]),

        # Right Side
        html.Div(
            style={
                'width': '23%',  # 1/4 of the width - 2% so not scrollable
                'float': 'left',
                'height': '96%',  # Full height of the screen
                'background-color': 'lightgray',  # Optional color for visibility
            },
            children=[

                # Top Division (1/5 height of Right Division)
                html.Div(
                    style={
                        'height': '12.2%',  # 1/5 of Right Division's height
                        'width': '90%',  # Slightly smaller width for margin effect
                        'margin': '5%',  # Margin to create space around this div
                        'background-color': 'white',
                        'box-sizing': 'border-box',
                        'border-radius': '25px'
                    },
                    children=[
                        html.Div("Bitte Flughafen auswählen", style={'text-align': 'center', 'font-size': 'xx-large', "margin-bottom": "15px"}),
                        dcc.Dropdown(airp['name'], 'Zurich Airport', id='airport-dropdown', searchable=True)
                    ]
                ),

                # Middle Division (2/5 height of Right Division)
                html.Div(
                    style={
                        'height': '42%',  # 2/5 of Right Division's height
                        'width': '90%',  # Slightly smaller width for margin effect
                        'margin': '5%',  # Margin to create space around this div
                        'background-color': 'white',
                        'box-sizing': 'border-box',
                        'border-radius': '25px'
                    },
                    children=[html.Div("Bitte Zoom auswählen", style={'text-align': 'center', 'font-size': 'xx-large', "margin-bottom": "5px"}),
                              dcc.Dropdown(["Continents", "Countries"], 'Continents', id='cont-dd'),
                              html.Div([genMiniMap(contClusters, 1)], id="miniMapContainer")
                    ]
                ),

                # Bottom Division (2/5 height of Right Division)
                html.Div(
                    style={
                        'height': '35%',  # 2/5 of Right Division's height
                        'width': '90%',  # Slightly smaller width for margin effect
                        'margin': '5%',  # Margin to create space around this div
                        'background-color': 'white',
                        'box-sizing': 'border-box',
                        'border-radius': '25px'
                    },
                    children=""
                )
            ]
        )
    ]
)



@callback(
    Output('map', 'children', allow_duplicate=True),
    Input('airport-dropdown', 'value'),
    prevent_initial_call=True,
)
def update_output(value):
    lat, lon = getLatLongFromName(value)
    weatherData, flightData = createData(lat, lon)
    fig = [genFig(weatherData, flightData, lat, lon)]
    return fig

@callback(
    Output("map", "children", allow_duplicate=True),
    Input("geojson_layer", "clickData"),
    prevent_initial_call=True,
)
def updateMapBasedOnMiniMapClick(click_data):
    lon, lat = click_data['geometry']['coordinates']
    weatherData, flightData = createData(lat, lon)
    fig = [genFig(weatherData, flightData, lat, lon)]
    return fig


@callback(
    Output('miniMapContainer', 'children'),
    Input('cont-dd', 'value')
)
def update_Minioutput(value):
    if value == "Continents":
        fig = genMiniMap(contClusters, 1)
    else:
        fig = genMiniMap(countClusters, 5)
    return fig


# Starte die Dash-Anwendung
if __name__ == '__main__':
    app.run_server(debug=True)
    




