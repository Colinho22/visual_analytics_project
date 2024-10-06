from api import geoLocation_API as g_Api
from api import weather_API as w_Api
from api import airTraffic_API as a_Api
ortsname1 = "Zurich"
ortsname2 = "Berlin"

lat1, long1 = g_Api.getlatLong(ortsname1)
lat2, long2 = g_Api.getlatLong(ortsname2)

temp1 = w_Api.getWeather(lat1, long1, temperature2 = True, windSpeed10 = False, windDirection10 = False, rain = False)
temp2 = w_Api.getWeather(lat2, long2, temperature2 = True)

#Beispiel mit der ganzen Schweiz
#flightData = a_Api.getAirTraffic(45.8389, 5.9966, 47.8229, 10.5226)

flightData = a_Api.getAirTraffic(lat1, long1, lat2, long2)

out1 = f"In {ortsname1} ({lat1}, {long1}) ist es momentan {temp1['temperature_2m']} Grad"
out2 = f"In {ortsname2} ({lat2}, {long2}) ist es momentan {temp2['temperature_2m']} Grad"
out3 = f"Zwischen {ortsname1} und {ortsname2} fliegen momentan folgende Flugzeuge:"
print(out1)
print(out2)
print(out3)
print(flightData)