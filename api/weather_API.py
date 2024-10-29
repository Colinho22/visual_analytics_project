import pandas as pd

def getWeather(lat, long,temperature2 = False, windSpeed10 = False, windDirection10 = False, rain = False):

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&current="

    if temperature2:
        url += f"temperature_2m,"
    if windSpeed10:
        url += f"wind_speed_10m,"
    if windDirection10:
        url += f"wind_speed_10m,"
    if rain:
        url += f"rain,"

    #print(url)
    geoData = pd.read_json(url)

    return geoData['current'].drop('time').drop('interval')

def getWeatherDangerIndex(lat, long):
    weatherOut = getWeather(lat, long, temperature2=True, windSpeed10=True, rain=True)
    #temp completly irrelevant --> for this: <0 little danger, >30 little danger
    # Wind <10 irrelevant 20 medium 30 relevant
    #Rain 4  mild, 10 strong, <10 extreme

    index = 0
    if weatherOut['temperature_2m'] > 30 or weatherOut['temperature_2m'] < 0:
        index += 1
    if weatherOut['wind_speed_10m'] > 10:
        index += 1
    if weatherOut['wind_speed_10m'] > 30:
        index += 1
    if weatherOut['rain'] > 4:
        index += 1
    if weatherOut['rain'] > 10:
        index += 1

    return index


#getWeather(46.84986, 9.53287, temperature2 = True)


