import dash
import dateutil
from dash import dcc, html, callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import airportsdata
import pandas as pd
import numpy as np
import dash_leaflet as dl
import dash_leaflet.express as dlx
from sklearn.cluster import KMeans
import plotly.express as px
from datetime import date, timedelta

import gunicorn

from api import weather_API as w_Api
from api import airTraffic_API as a_Api
from api import histAirTraffic_API as h_Api
from api import random_API as r_Api

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
    #Als Alternative wird das File globalGeoJson geladen, welches aus demselben globalen Aufruf enstand
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
        ], center=(0, 4), zoom=zoom, style={'height': '24vh', 'margin-left': '5px','margin-right': '5px','margin-top': '5px'}, id="miniMap", zoomControl=False)
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
    flightData = pd.DataFrame.from_dict(flightData)
    flightData = flightData.rename(columns={"alt": "Altitude", "vel": "Velocity", "cat": "Category"})
    fig = px.scatter(flightData, x="Altitude", y="Velocity", color='Category', hover_name= 'callsign')
    fig.update_layout(margin=dict(l=0, r=10, t=35, b=0))
    fig.update_coloraxes(showscale=False)
    return fig

def genHistoPlot(startDate, endDate, x_selection, y_selection):
    #startDate = date.strftime(startDate, "%Y-%m-%d")
    #endDate = date.strftime(endDate, "%Y-%m-%d")

    if x_selection == "Summe":
        histFlightData = h_Api.getHistoricalFlightData(startDate, endDate, sum=True)
    elif x_selection == "Alle":
        histFlightData = h_Api.getHistoricalFlightData(startDate, endDate, sum=False)
    else:
        histFlightData = h_Api.getHistoricalFlightData(startDate, endDate, sum=False)
        histFlightData = histFlightData[histFlightData["cat"] == x_selection]
    histFlightData['date'] = pd.to_datetime(histFlightData['date'])

    histWeatherData = w_Api.getHistWeatherDangerIndex(static_lat, static_lon, startDate, endDate)
    histWeatherData['date'] = pd.to_datetime(histWeatherData['date'])

    merge = histFlightData.merge(histWeatherData, on='date')
    merge = merge.rename(columns={"wind_speed_10m": "Wind Speed", "rain": "Rain", "temperature_2m": "Temperature", "cat": "Category", "mvt": "Plane movements", "index": "Weather danger index", "date": "Date"})

    fig = px.scatter(merge, x="Plane movements", y=y_selection, hover_name= 'Date')
    if x_selection == "Alle":
        fig = px.scatter(merge, x="Plane movements", y=y_selection, color= 'Category', hover_name='Date')
    else:
        fig = px.scatter(merge, x="Plane movements", y=y_selection, hover_name='Date')
    fig.update_layout(margin=dict(l=0, r=10, t=35, b=0))
    fig.update_layout(paper_bgcolor='azure')
    #fig.show()
    return fig

def returnModalText():
    modalText = '''
    This dashboard shows the impact of the weather on the current and historical aircraft travel.
    
    ## Live Data
    The live data is displayed in the top left map, with the overlay that displays the severity of the weather in that area.
    It can be manipulated by dragging with the middle-mouse button, zooming with the mouse wheel or a specific area can be selected by shift+dragging the mouse over the screen. 
    It is also possible to deselect overlays by clicking on the map symbol in the top right corner.
    
    All tools to further manipulate or analyse the live data are signaled by white boxes.
    In the top right corner is the "Choose Airport" menu, that lets you fly to a specified airport. 
    Below it is the "Select Hotspot" menu. It displays a minimap, that shows the most active clusters of air traffic. It can be zoomed in to show more specific clusters by selecting "countries" in the dropdown menu.
    In the bottom right is the analysis of all currently displayed aircrafts. It shows their velocity in comparison to their altitude while also displaying the callsign and category of the plane when hovering over it. 
    
    ## Historical Data
    The historical data is displayed in the bottem left corner in the lightblue box. 
    It shows a comparison of weather data and flight data at the EuroAirport Basel-Mulhouse-Freiburg.
    Each dot in the graph represents a day in the selected timeframe. The type of comparison can be adjusted by changing the radio-buttons on the left-hand side. 
    Its therefore possible to show the sum of all air-traffic in a day compared to the rainfall of said day or another example would be to show all Cargo-air-traffic compared with the same weather index used in the live map. 
    '''
    return modalText

# Start App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])
server = app.server

#Get Airports Data
airports = airportsdata.load()
airp = pd.DataFrame.from_dict(airports)
airp = airp.drop(index=(['icao', 'iata', 'subd', 'elevation', 'tz', 'lid']))
airp = airp.dropna()
airp = airp.T


# Boolean for switiching to Random Data
RANDOM_DATA = False
# Amount of Data Points (Only relevant when RANDOM_DATA = True
AMOUNT = 100

# Start Pos for Map
lat, lon = getLatLongFromName('EuroAirport Basel-Mulhouse-Freiburg Airport')
static_lat, static_lon  = getLatLongFromName('EuroAirport Basel-Mulhouse-Freiburg Airport')

# Set Plane Categories for Main Map
PLANE_CATEGORIES = ['Commercial Airplane','No ADS-B Emitter Category Information','Light (< 15500 lbs)','Small (15500 to 75000 lbs)','Large (75000 to 300000 lbs)','High Vortex Large (aircraft such as B-757)','Heavy (> 300000 lbs)','High Performance (> 5g acceleration and 400 kts)','Rotorcraft','Glider / sailplane','Lighter-than-air','Parachutist / Skydiver','Ultralight / hang-glider / paraglider','Reserved','Unmanned Aerial Vehicle','Space / Trans-atmospheric vehicle','Surface Vehicle – Emergency Vehicle','Surface Vehicle – Service Vehicle','Point Obstacle (includes tethered balloons)','Cluster Obstacle','Line Obstacle']

# Options for Radio Buttons in Histo-Plot
xSelList = ['Summe', 'Alle', 'Passagierverkehr', 'Fracht Cargo', 'Fracht Express', 'Andere Kategorien']
xSelListEnglish = [{'label':'Sum', 'value':xSelList[0]}, {'label':'All', 'value':xSelList[1]}, {'label':'Passenger planes', 'value':xSelList[2]}, {'label':'Cargo planes', 'value':xSelList[3]}, {'label':'Cargo Express', 'value':xSelList[4]},{'label':'others', 'value':xSelList[5]}]
ySelList = ['Weather danger index', 'Temperature', 'Rain', 'Wind Speed']

# Dates for DatePicker in Histo-Plot
static_endDate = date.today()
static_startDate = (static_endDate - timedelta(days=30)).strftime("%Y-%m-%d")
static_endDate = static_endDate.strftime("%Y-%m-%d")
static_minStartDate = date(2019,7,1).strftime("%Y-%m-%d")

# Create Start Data for MainMap and MiniMap
if RANDOM_DATA:
    weatherData, flightData =createFakeData(lat, lon)
else:
    weatherData, flightData = createData(lat, lon)
contClusters, countClusters = createGlobalData()

# Generate App Layout
app.layout = html.Div(
    style={'height': '97.5vh', 'width': '99.5vw', 'overflow': 'hidden', 'box-sizing': 'border-box', 'background-color': 'lightgray'},
    children=[
        # Top Banner
        html.Div(style={'height': '10%','width': '100%', 'background-color': 'lightgray'},
                 children=html.Div(style={'height': '90%', 'width': '99.5%', 'background-color': 'white', 'box-sizing': 'border-box', 'border-bottom-left-radius': '30px', 'border-bottom-right-radius': '30px', 'margin-right': '10px', 'margin-left': '10px','display': 'flex', 'flex-direction': 'row'},
                                   children=[
                                        html.Div("Analysis of weather impact on flight frequency", style={'width': '92%', 'font-size': 'xxx-large', "margin-top": "10px", 'margin-left': '30px'}),
                                        html.Div(children=[
                                                dbc.Button("Info", id="open", n_clicks=0, style={'font-size': 'large'}),
                                                dbc.Modal([
                                                    dbc.ModalHeader(dbc.ModalTitle("Information")),
                                                    dbc.ModalBody(dcc.Markdown(returnModalText())),
                                                    dbc.ModalFooter(
                                                    dbc.Button(
                                                "Close", id="close", className="ms-auto", n_clicks=0
                                                        )
                                                    ),
                                                ],
                                                id="modal",
                                                is_open=False,
                                            ),
                                        ], style={'width': '3%', 'margin-top': '20px'})
                                   ]
                )
        ),
        # Left Side (Top Left and Bottom Left)
        html.Div(style={'width': '75%', 'float': 'left', 'height': '100%'}, children=[

            # Top Left (Main Frame)
            html.Div(
                style={'height': '50%','width': '100%','background-color': 'lightgray'},
                children=html.Div([genFig(weatherData, flightData)], id="map")
            ),
            # Bottom Left
            html.Div(
                style={'height': '42%', 'width': '100%', 'background-color': 'lightgray', 'display': 'flex', 'flex-direction': 'row'},
                children=[
                    # Bottom Left, Right (historical Analysis)
                    html.Div(
                        style={'height': '100%', 'width': '100%', 'background-color': 'lightgray'},
                        children=[
                            html.Div(
                            style={'height': '84%', 'width': '99%', 'background-color': 'azure', 'box-sizing': 'border-box', 'border-radius': '30px', 'margin-top': '40px', 'margin-right': '10px', 'margin-left': '10px','text-align': 'center', 'font-size': 'xx-large', "margin-bottom": "5px"},
                             children=[
                                "Air-traffic and weather comparison in the EuroAirport Basel-Mulhouse-Freiburg",
                                 html.Div(style={'display': 'flex', 'flex-direction': 'row'},
                                 children=[
                                     html.Div(
                                        children=[
                                        html.Div("Date picker", style={'text-align': 'left', 'font-size': 'large', 'font-weight':'bold',"margin-bottom": "2px", "margin-left": "20px"}),
                                        dcc.DatePickerRange(start_date=static_startDate, end_date=static_endDate,display_format='DD MMM YYYY', min_date_allowed=static_minStartDate, max_date_allowed=static_endDate, style={"margin-bottom": "10px"}, id='histoDate'),
                                        html.Div(style={'display': 'flex', 'flex-direction': 'row'},children=[
                                            html.Div(children=[
                                                html.Div("X-Axis control", style={'text-align': 'left', 'font-size': 'large', 'font-weight':'bold',"margin-bottom": "2px", "margin-left": "20px", "margin-top": "5px"}),
                                                dcc.RadioItems(value= xSelList[0], options=xSelListEnglish,  style={'text-align': 'left', 'font-size': 'medium', "margin-left": "20px"}, id='histoXaxis'),]),
                                            html.Div(children=[
                                                html.Div("Y-Axis control", style={'text-align': 'left', 'font-size': 'large', 'font-weight':'bold', "margin-bottom": "2px", "margin-left": "20px", "margin-top": "5px"}),
                                                dcc.RadioItems(ySelList, ySelList[0], style={'text-align': 'left', 'font-size': 'medium', "margin-left": "20px"}, id='histoYaxis'),]),
                                        ])
                                     ]),
                                     html.Div(children=[
                                        dcc.Graph(figure=genHistoPlot(static_startDate, static_endDate, xSelList[0], ySelList[0]), id="histoPlot", style={'height': '300px', 'width':'1250px', "margin-left": "50px"}),
                                     ])
                                ])
                                ]
                            ),
                        ]
                    ),
                ]
            )
        ]),
        # Right Side
        html.Div(
            style={'width': '25%', 'float': 'left', 'height': '100%', 'background-color': 'lightgray',},
            children=[
                # Top (Choose Airport)
                html.Div(
                    style={'height': '12.2%', 'width': '96.5%', 'margin-left': '20px', 'margin-top': '0px', 'background-color': 'white', 'box-sizing': 'border-box', 'border-radius': '30px', 'margin-right': '10px'
                    },
                    children=[
                        html.Div("Choose airport", style={'text-align': 'center', 'font-size': 'xx-large', "margin-bottom": "20px", 'margin-left': '5px','margin-right': '5px',}),
                        dcc.Dropdown(airp['name'], 'EuroAirport Basel-Mulhouse-Freiburg Airport', id='airport-dropdown', searchable=True, style={'margin-left': '6px', 'width':'98%'})
                    ]
                ),
                # Middle (Select Hotspot)
                html.Div(
                    style={'height': '37.5%', 'width': '96.5%', 'margin-left': '20px',  'margin-top': '20px', 'background-color': 'white', 'box-sizing': 'border-box', 'border-radius': '30px', 'margin-right': '10%'},
                    children=[html.Div("Select Hotspot", style={'text-align': 'center', 'font-size': 'xx-large', "margin-bottom": "5px"}),
                              dcc.Dropdown(["Continents", "Countries"], 'Continents', id='cont-dd', style={'margin-left': '6px', 'width':'98%'}),
                              html.Div([genMiniMap(contClusters, 1)], id="miniMapContainer")
                    ]
                ),
                # Botton (Flight comparisons)
                html.Div(
                    style={'height': '35.8%', 'width': '96.5%', 'margin-left': '20px',  'margin-top': '20px', 'background-color': 'white', 'box-sizing': 'border-box', 'border-radius': '30px', 'margin-right': '10px','text-align': 'center', 'font-size': 'xx-large', "margin-bottom": "5px"},
                    children=[
                        "Live Flight comparisons",
                        dcc.Graph(figure = genCompPlot(flightData), id="compPlot", style={'height':'83%','width': '90%', 'margin-left':'5%'})
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
    Output("compPlot", "figure", allow_duplicate=True),
    Input('airport-dropdown', 'value'),
    prevent_initial_call=True,
)
def updateMapBasedOnDropdown(value):
    lat, lon = getLatLongFromName(value)
    if RANDOM_DATA:
        weatherData, flightData = createFakeData(lat, lon)
    else:
        weatherData, flightData =createData(lat, lon)
    fig = [genFig(weatherData, flightData)]
    grid = generate_grid(weatherData)
    view = dict(center=[lat, lon], zoom=9, transition="flyTo")
    compFigure = genCompPlot(flightData)
    return fig, grid, view, compFigure

@callback(
    Output("map", "children", allow_duplicate=True),
    Output("grid-layer", "children", allow_duplicate=True),
    Output("mapCore", "viewport", allow_duplicate=True),
    Output("compPlot", "figure", allow_duplicate=True),
    Input("geojson_layer", "clickData"),
    prevent_initial_call=True,
)
def updateMapBasedOnMiniMapClick(click_data):
    lon, lat= click_data['geometry']['coordinates']
    if RANDOM_DATA:
        weatherData, flightData = createFakeData(lat, lon)
    else:
        weatherData, flightData =createData(lat, lon)
    fig = [genFig(weatherData, flightData)]
    grid = generate_grid(weatherData)
    view = dict(center=[lat, lon], zoom=9, transition="flyTo")
    compFigure = genCompPlot(flightData)
    return fig, grid, view, compFigure

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

@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@callback(
    Output('histoPlot', 'figure'),
    Input('histoDate', 'start_date'),
    Input('histoDate', 'end_date'),
    Input('histoXaxis', 'value'),
    Input('histoYaxis', 'value'),
)
def update_figure(start_date, end_date, xaxis, yaxis):
    fig = genHistoPlot(start_date, end_date, xaxis, yaxis)
    return fig


# Starte die Dash-Anwendung
if __name__ == '__main__':
    app.server.static_folder = 'static'
    app.run_server(debug=False)

