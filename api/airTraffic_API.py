import pandas as pd
import datetime

def getAirTraffic(lamin, lomin, lamax, lomax):
    catIndex = ['No information', 'No ADS-B Emitter Category Information', 'Light (< 15500 lbs)',
                'Small (15500 to 75000 lbs)', 'Large (75000 to 300000 lbs)',
                'High Vortex Large (aircraft such as B-757)',
                'Heavy (> 300000 lbs)', 'High Performance (> 5g acceleration and 400 kts)', 'Rotorcraft',
                'Glider / sailplane', 'Lighter-than-air', 'Parachutist / Skydiver',
                'Ultralight / hang-glider / paraglider',
                'Reserved', 'Unmanned Aerial Vehicle', 'Space / Trans-atmospheric vehicle',
                'Surface Vehicle – Emergency Vehicle',
                'Surface Vehicle – Service Vehicle', 'Point Obstacle (includes tethered balloons)', 'Cluster Obstacle',
                'Line Obstacle']


    url = f"https://opensky-network.org/api/states/all?lamin={lamin}&lomin={lomin}&lamax={lamax}&lomax={lomax}"
    try:
        flightData = pd.read_json(url)
    except Exception as e:
        #return empty Dataframe
        return pd.DataFrame(columns=['callsign', 'originCountry', 'lon', 'lat', 'alt', 'vel', 'dir', 'cat'])

    data = []
    for i in flightData['states']:
        data.append([i[1], i[2], i[5], i[6], i[7], i[9], i[10], i[16]])

    dataDf = pd.DataFrame(data)

    dataDf.columns = ['callsign', 'originCountry', 'lon', 'lat', 'alt', 'vel', 'dir', 'cat']

    return dataDf




