import pandas as pd
import warnings

warnings.filterwarnings('ignore')

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

def getIndex(weatherData):
    # Temperature completely irrelevant --> for this: <0 little danger, >30 little danger
    # Wind <10 irrelevant 20 medium 30 relevant
    # Rain 4  mild, 10 strong, >10 extreme
    index = 0
    if weatherData['temperature_2m'] > 30 or weatherData['temperature_2m'] < 0:
        index += 1
    if weatherData['wind_speed_10m'] > 10:
        index += 1
    if weatherData['wind_speed_10m'] > 30:
        index += 1
    if weatherData['rain'] > 4:
        index += 1
    if weatherData['rain'] > 10:
        index += 1

    out = (index / 10)+0.1
    return out  # Range von 0.1 bis 0.6


def getWeatherDangerIndex(lat, long):
    weatherOut = getWeather(lat, long, temperature2=True, windSpeed10=True, rain=True)
    index = getIndex(weatherOut)
    return index

def getHistWeatherDangerIndex(lat, long, startDate, endDate):
    url = f"https://archive-api.open-meteo.com/v1/era5?latitude={lat}&longitude={long}&start_date={startDate}&end_date={endDate}&daily=temperature_2m_max,rain_sum,wind_speed_10m_max"
    histData = pd.read_json(url)
    histData = histData[["daily"]].transpose()

    time = histData['time'][0]
    temperature_2m_max = histData['temperature_2m_max'][0]
    rain_sum = histData['rain_sum'][0]
    wind_speed_10m_max = histData['wind_speed_10m_max'][0]
    zipped = zip(time, temperature_2m_max, rain_sum, wind_speed_10m_max)
    data = pd.DataFrame(zipped, columns=['date','temperature_2m','rain','wind_speed_10m'])
    indices = []
    for row in data.iterrows():
        index = getIndex(row[1])
        indices.append(index)
    data['index'] = indices
    data = data[['date', 'index']]
    return data


#getWeather(46.84986, 9.53287, temperature2 = True)

#startDate = '2024-01-01'
#endDate = '2024-04-01'
#data = getHistWeatherDangerIndex(46.84986, 9.53287, startDate, endDate)



