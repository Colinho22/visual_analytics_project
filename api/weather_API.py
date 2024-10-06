import pandas as pd

def getWeather(lat, long,temperature2 = False, windSpeed10 = False, windDirection10 = False, rain = False):

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&current="

    if temperature2:
        url += f"temperature_2m,"
    if windSpeed10:
        url += f"wind_speed_10m"
    if windDirection10:
        url += f"wind_speed_10m"
    if rain:
        url += f"raim"

    geoData = pd.read_json(url)

    return geoData['current'].drop('time').drop('interval')


#getWeather(46.84986, 9.53287, temperature2 = True)