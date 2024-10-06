import pandas as pd
def getlatLong(locationName = ""):
    baseUrl = "https://geocoding-api.open-meteo.com/v1/search"
    urlEnd = "&count=1&language=en&format=json"
    url =  f"{baseUrl}?name={locationName}{urlEnd}"
    try:
        geoData = pd.read_json(url)
    except Exception as e:
        return -1,-1


    #Extract lat and Long
    lat = geoData["results"][0]["latitude"]
    long = geoData["results"][0]["longitude"]

    return lat, long