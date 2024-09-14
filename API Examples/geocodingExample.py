import pandas as pd

url =  "https://geocoding-api.open-meteo.com/v1/search?name=Landqu&count=10&language=en&format=json"
geoData = pd.read_json(url)

print(geoData)