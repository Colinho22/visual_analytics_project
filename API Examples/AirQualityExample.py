import pandas as pd

url =  "https://air-quality-api.open-meteo.com/v1/air-quality?latitude=52.52&longitude=13.41&hourly=pm10,pm2_5"
airData = pd.read_json(url)

print(airData)
