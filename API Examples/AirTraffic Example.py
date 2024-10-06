#The OpenSky Network, https://opensky-network.org

#Matthias Schäfer, Martin Strohmeier, Vincent Lenders, Ivan Martinovic and Matthias Wilhelm.
#"Bringing Up OpenSky: A Large-scale ADS-B Sensor Network for Research".
#In Proceedings of the 13th IEEE/ACM International Symposium on Information Processing in Sensor Networks (IPSN), pages 83-94, April 2014.


import pandas as pd
import datetime

#URL mit Switzerland Bounding Box
url =  "https://opensky-network.org/api/states/all?lamin=45.8389&lomin=5.9962&lamax=47.8229&lomax=10.5226"
flightData = pd.read_json(url)
print(flightData)
timestamp = flightData['time']

print(datetime.datetime.fromtimestamp(int(timestamp[0])).strftime('%Y-%m-%d %H:%M:%S'))



#URL to state Components
#https://openskynetwork.github.io/opensky-api/rest.html#flights-by-aircraft



#print(flightData['states'][0])

#5 Longitude
#WGS-84 longitude in decimal degrees.
lon = flightData['states'][0][5]

#6 Latitude
#WGS-84 latitude in decimal degrees
lat = flightData['states'][0][6]

#7 Altitude
#Barometric altitude in meters.
alt = flightData['states'][0][7]

#9 Velocity
#Velocity over ground in m/s
Vel = flightData['states'][0][9]

#10 True Track
#True track (Flugrichtung) in decimal degrees clockwise from north (north=0°)
dir = flightData['states'][0][10]

#17 Category
#Aircraft category.0 = No information at all,
# 1 = No ADS-B Emitter Category Information
# 2 = Light (< 15500 lbs)
# 3 = Small (15500 to 75000 lbs)
# 4 = Large (75000 to 300000 lbs)
# 5 = High Vortex Large (aircraft such as B-757)
# 6 = Heavy (> 300000 lbs)
# 7 = High Performance (> 5g acceleration and 400 kts)
# 8 = Rotorcraft
# 9 = Glider / sailplane
# 10 = Lighter-than-air
# 11 = Parachutist / Skydiver
# 12 = Ultralight / hang-glider / paraglider
# 13 = Reserved
# 14 = Unmanned Aerial Vehicle
# 15 = Space / Trans-atmospheric vehicle
# 16 = Surface Vehicle – Emergency Vehicle
# 17 = Surface Vehicle – Service Vehicle
# 18 = Point Obstacle (includes tethered balloons)
# 19 = Cluster Obstacle
# 20 = Line Obstacle
cat = flightData['states'][0][16]



print(f"{lon}, {lat}, {alt}, {Vel}, {dir}, {cat}")


