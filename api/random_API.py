import numpy as np

def getAirTrafficDicts(min_lat, min_lon, max_lat, max_lon, amount):
    #Output list of dicts
    # Dict shape: (dict(callsign=i[1], originCountry=i[2], lat=float(i[6]), lon=float(i[5]), alt=i[7], vel=i[9], dir=i[10], cat=i[16]))
    liste = []
    for i in range(amount):
        callsign = "fake"
        originCountry = "switz"
        lat = np.random.rand() * 180 - 90
        lon = np.random.rand() * 360 - 180
        alt = 1000
        speed = 123
        dir = np.random.rand() * 7200 - 3600
        cat = 1
        liste.append(dict(callsign=callsign, originCountry=originCountry, lat=lat, lon=lon, alt=alt, vel=speed, dir=dir,cat=cat))
    return liste

def getWeatherDangerIndex(i,j):
    #Output single value
    return np.random.rand()