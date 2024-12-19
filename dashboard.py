import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output, State
import dash_daq as daq
import dash_bootstrap_components as dbc
import airportsdata
import pandas as pd
import numpy as np
import dash_leaflet as dl
import dash_leaflet.express as dlx
from sklearn.cluster import KMeans
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots


import gunicorn

from api import weather_API as w_Api
from api import airTraffic_API as a_Api
from api import histAirTraffic_API as h_Api
from api import random_API as r_Api


#app = dash.Dash(__name__)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])
server = app.server

#Get Airports Data
airports = airportsdata.load()
airp = pd.DataFrame.from_dict(airports)
airp = airp.drop(index=(['icao', 'iata', 'subd', 'elevation', 'tz', 'lid']))
airp = airp.dropna()
airp = airp.T

#Init lat und lon
lat, lon = 5,5
static_lat, static_lon = 5,5
AMOUNT = 100
PLANE_CATEGORIES = ['Commercial Airplane','No ADS-B Emitter Category Information','Light (< 15500 lbs)','Small (15500 to 75000 lbs)','Large (75000 to 300000 lbs)','High Vortex Large (aircraft such as B-757)','Heavy (> 300000 lbs)','High Performance (> 5g acceleration and 400 kts)','Rotorcraft','Glider / sailplane','Lighter-than-air','Parachutist / Skydiver','Ultralight / hang-glider / paraglider','Reserved','Unmanned Aerial Vehicle','Space / Trans-atmospheric vehicle','Surface Vehicle – Emergency Vehicle','Surface Vehicle – Service Vehicle','Point Obstacle (includes tethered balloons)','Cluster Obstacle','Line Obstacle']

def createData(center_lat, center_lon):
    #offset = 3 #ganze Schweiz
    latArea = 1
    lonArea = 2
    #-90 to 90 for latitude and -180 to 180 for longitude
    min_lat = center_lat - latArea
    max_lat = center_lat + latArea
    min_lon = center_lon - lonArea
    max_lon = center_lon + lonArea

    #Create Grid
    #Gridsize 10km
    lat_grids = 5
    lon_grids = 5
    latOffset = (max_lat - min_lat) / (2 * (lat_grids-1))
    lonOffset = (max_lon - min_lon) / (2 * (lon_grids-1))
    a = np.linspace(min_lat, max_lat, lat_grids)
    b = np.linspace(min_lon, max_lon, lon_grids)


    weatherData = []
    for i in a:
        for j in b:
            x = w_Api.getWeatherDangerIndex(i,j)
            weatherData.append([[i - latOffset, j - lonOffset], [i + latOffset, j + lonOffset], x])
    flightData = a_Api.getAirTrafficDicts(min_lat, min_lon, max_lat, max_lon)

    return weatherData, flightData

def createFakeData(center_lat, center_lon):
    #offset = 3 #ganze Schweiz
    latArea = 1
    lonArea = 2
    #-90 to 90 for latitude and -180 to 180 for longitude
    min_lat = center_lat - latArea
    max_lat = center_lat + latArea
    min_lon = center_lon - lonArea
    max_lon = center_lon + lonArea

    #Create Grid
    #Gridsize 10km
    lat_grids = 5
    lon_grids = 5
    latOffset = (max_lat - min_lat) / (2 * (lat_grids-1))
    lonOffset = (max_lon - min_lon) / (2 * (lon_grids-1))
    a = np.linspace(min_lat, max_lat, lat_grids)
    b = np.linspace(min_lon, max_lon, lon_grids)


    weatherData = []
    for i in a:
        for j in b:
            x = r_Api.getWeatherDangerIndex(i,j)
            weatherData.append([[i - latOffset, j - lonOffset], [i + latOffset, j + lonOffset], x])
    flightData = r_Api.getAirTrafficDicts(min_lat, min_lon, max_lat, max_lon, AMOUNT)

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
    #Bei wiederholtem Einsazt der gratis API kommt es sehr schnell zu zu hohen Abfragezahlen und somit zum Unterbruch
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

def genFig(weatherData, flightData):
    grid = generate_grid(weatherData)
    map = dl.Map(
        dl.LayersControl([
            dl.BaseLayer(dl.TileLayer(), name="Base Layer", checked=True),
            dl.Overlay(dl.GeoJSON(data=dlx.dicts_to_geojson(flightData), cluster=True, zoomToBoundsOnClick=True), name="Air Traffic", checked=True),
            dl.Overlay(dl.LayerGroup(children=grid,id="grid-layer"), name="Weather", checked=True)
            ]), center=(static_lat, static_lon), zoom=9, style={'height': '50vh'}, id='mapCore')

    return map

def genMiniMap(activeClusters, zoom):
    map = dl.Map([
        dl.TileLayer(),
        dl.GeoJSON(data=activeClusters, cluster=True, zoomToBoundsOnClick=True, id = "geojson_layer"),
        ], center=(0, 4), zoom=zoom, style={'height': '22vh'}, id="miniMap", zoomControl=False)
    return map

def generate_grid(weatherData):
    layers = []
    for items in weatherData:
        layers.append(
            dl.Rectangle(
                bounds=[items[0], items[1]],
                color="#ffffff1",
                fillColor="red",
                fillOpacity=items[2]
            )
        )
    return layers

def genCompPlot(flightData):
    #color_discrete_sequence = PLANE_CATEGORIES,
    flightData = pd.DataFrame.from_dict(flightData)
    flightData = flightData.rename(columns={"alt": "Altitude", "vel": "Velocity", "cat": "Category"})
    fig = px.scatter(flightData, x="Altitude", y="Velocity", color='Category', hover_name= 'callsign', title="Flight comparisons")
    fig.update_layout(margin=dict(l=0, r=10, t=35, b=0))
    fig.update_coloraxes(showscale=False)
    return fig


def genHistoPlot(startDate, endDate):
    #EuroAirport Basel-Mulhouse-Freiburg Airport
    histFlightData = h_Api.getHistoricalFlightData(startDate, endDate)
    histFlightData['date'] = pd.to_datetime(histFlightData['date'])
    histWeatherData = w_Api.getHistWeatherDangerIndex(static_lat, static_lon, startDate, endDate)
    histWeatherData['date'] = pd.to_datetime(histWeatherData['date'])

    merge = histFlightData.merge(histWeatherData, on='date')

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(x= merge['date'], y=merge['mvt'], name="yaxis data"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x= merge['date'], y=merge['index'], name="yaxis2 data"),
        secondary_y=True,
    )

    # Add figure title
    fig.update_layout(
        title_text="Double Y Axis Example"
    )

    # Set x-axis title
    fig.update_xaxes(title_text="xaxis title")

    # Set y-axes titles
    fig.update_yaxes(title_text="<b>primary</b> yaxis title", secondary_y=False)
    fig.update_yaxes(title_text="<b>secondary</b> yaxis title", secondary_y=True)

    fig.show()




lat, lon = getLatLongFromName('EuroAirport Basel-Mulhouse-Freiburg Airport')
static_lat, static_lon  = getLatLongFromName('EuroAirport Basel-Mulhouse-Freiburg Airport')

startDate = '2024-01-01'
endDate = '2024-04-01'
genHistoPlot(startDate, endDate)

#######################################################################################################################
# FAKE DATA
#######################################################################################################################
weatherData, flightData =createData(lat, lon)
#weatherData, flightData =createFakeData(lat, lon)
#######################################################################################################################
# FAKE DATA
#######################################################################################################################
contClusters, countClusters = createGlobalData()
#grid = generate_grid(weatherData)


app.layout = html.Div(
    style={'height': '100vh', 'width': '100vw', 'overflow': 'hidden', 'margin': '0', 'padding': '0', 'box-sizing': 'border-box'},
    children=[
        # Top Banner
        html.Div("Top Banner",style={
                    'height': '10%',
                    'width': '100%',
                    'background-color': 'lightgray',
                },),
        # Left Side (Top Left and Bottom Left)
        html.Div(style={'width': '75%', 'float': 'left', 'height': '100%'}, children=[

            # Top Left (Main Frame)
            html.Div(
                style={
                    'height': '50%',
                    'width': '100%',
                    'background-color': 'lightgray',
                },
                children=html.Div([genFig(weatherData, flightData)], id="map")
            ),

            # Bottom Left (Analysis windows)
            html.Div(
                style={
                    'height': '42%',
                    'width': '100%',
                    'background-color': 'lightgray',
                    'display': 'flex',
                    'flex-direction': 'row',
                },
                children=[
                    # Bottom Left, Left (Flight comparisons)
                    html.Div(
                        style={
                            'height': '100%',
                            'width': '40%',
                            'background-color': 'lightgray',
                        },
                        children=[
                            html.Div(
                            style={
                                'height': '80%',
                                'width': '90%',

                                'background-color': 'white',
                                'box-sizing': 'border-box',
                                'border-radius': '30px',
                                'margin-top': '20px',
                                'margin-right': '10px',
                                'margin-left': '20px',
                            },
                             children=[
                                dcc.Graph(figure = genCompPlot(flightData), id="compPlot", style={'height': '100%','width': '90%','margin-left':'5%'}),
                            ]),
                        ]
                    ),
                    # Bottom Left, Right (historical Analysis)
                    html.Div(
                        style={
                            'height': '100%',
                            'width': '60%',
                            'background-color': 'lightgray',
                        },
                        children=[
                            html.Div(
                            style={
                                'height': '80%',
                                'width': '100%',

                                'background-color': 'white',
                                'box-sizing': 'border-box',
                                'border-radius': '30px',
                                'margin-top': '20px',
                                'margin-right': '10px',
                            },
                             children=[
                                ]
                            ),
                        ]
                    ),

                ]
            )
        ]),

        # Right Side
        html.Div(
            style={
                'width': '25%',
                'float': 'left',
                'height': '100%',
                'background-color': 'lightgray',
            },
            children=[
                # Top (Choose Airport)
                html.Div(
                    style={
                        'height': '12.2%',
                        'width': '90%',
                        'margin': '5%',
                        'margin-top':'0px',
                        'background-color': 'white',
                        'box-sizing': 'border-box',
                        'border-radius': '30px',
                        'margin-right': '10px'
                    },
                    children=[
                        html.Div("Choose airport", style={'text-align': 'center', 'font-size': 'xx-large', "margin-bottom": "20px"}),
                        dcc.Dropdown(airp['name'], 'EuroAirport Basel-Mulhouse-Freiburg Airport', id='airport-dropdown', searchable=True)
                    ]
                ),

                # Middle (Select Hotspot)
                html.Div(
                    style={
                        'height': '34%',
                        'width': '90%',
                        'margin': '5%',
                        'background-color': 'white',
                        'box-sizing': 'border-box',
                        'border-radius': '30px',
                        'margin-right': '10%'
                    },
                    children=[html.Div("Select Hotspot", style={'text-align': 'center', 'font-size': 'xx-large', "margin-bottom": "5px"}),
                              dcc.Dropdown(["Continents", "Countries"], 'Continents', id='cont-dd'),
                              html.Div([genMiniMap(contClusters, 1)], id="miniMapContainer")
                    ]
                ),
                # Botton
                html.Div(
                    style={
                        'height': '34%',
                        'width': '90%',
                        'margin': '5%',
                        'margin-top':'0px',
                        'background-color': 'white',
                        'box-sizing': 'border-box',
                        'border-radius': '30px',
                        'margin-right': '10px'
                    },
                    children=[
                        html.Div("Overlay Control",style={'text-align': 'center', 'font-size': 'xx-large', "margin-bottom": "15px"}),
                        daq.BooleanSwitch(on=True, label={'label': "Weather overlay", 'style': {'font-size': 'x-large'}}, labelPosition="top"),
                        daq.BooleanSwitch(on=True, label={'label': "Air traffic overlay", 'style': {'font-size': 'x-large'}}, labelPosition="top")
                    ]
                )
            ]
        )
    ]
)

@callback(
    Output('map', 'children', allow_duplicate=True),
    Output("grid-layer", "children", allow_duplicate=True),
    Output("mapCore", "viewport", allow_duplicate=True),
    Input('airport-dropdown', 'value'),
    prevent_initial_call=True,
)
def updateMapBasedOnDropdown(value):
    lat, lon = getLatLongFromName(value)
    #######################################################################################################################
    # FAKE DATA
    #######################################################################################################################
    weatherData, flightData =createData(lat, lon)
    #weatherData, flightData = createFakeData(lat, lon)
    #######################################################################################################################
    # FAKE DATA
    #######################################################################################################################
    fig = [genFig(weatherData, flightData)]
    grid = generate_grid(weatherData)
    view = dict(center=[lat, lon], zoom=9, transition="flyTo")
    return fig, grid, view


@callback(
    Output("map", "children", allow_duplicate=True),
    Output("grid-layer", "children", allow_duplicate=True),
    Output("mapCore", "viewport", allow_duplicate=True),
    Input("geojson_layer", "clickData"),
    prevent_initial_call=True,
)
def updateMapBasedOnMiniMapClick(click_data):
    lon, lat= click_data['geometry']['coordinates']
    #######################################################################################################################
    # FAKE DATA
    #######################################################################################################################
    weatherData, flightData =createData(lat, lon)
    #weatherData, flightData = createFakeData(lat, lon)
    #######################################################################################################################
    # FAKE DATA
    #######################################################################################################################
    fig = [genFig(weatherData, flightData)]
    grid = generate_grid(weatherData)
    view = dict(center=[lat, lon], zoom=9, transition="flyTo")
    return fig, grid, view

@callback(
    Output('miniMapContainer', 'children'),
    Input('cont-dd', 'value')
)
def update_Minioutput(value):
    if value == "Continents":
        fig = genMiniMap(contClusters, 1)
    else:
        fig = genMiniMap(countClusters, 2)
    return fig


# Starte die Dash-Anwendung
if __name__ == '__main__':
    app.run_server(debug=True)
    





'''

def genFig(weatherData, flightData):
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
