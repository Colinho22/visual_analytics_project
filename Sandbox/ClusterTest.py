from sklearn.cluster import KMeans
from api import airTraffic_API as a_Api
import dash_leaflet.express as dlx
import geojson

weatherData = []
#####################################
#Daten umbedingt Zwischenspeichern --> maximale Anzahl Auffrufe vermeiden
#####################################
#-90 to 90 for latitude and -180 to 180 for longitude
#flightData = a_Api.getAirTrafficDicts(-90, -180, 90, 180)
#df = pd.DataFrame.from_dict(flightData)
#df.to_csv('assets/globalFlights.csv', index=False)



with open('../assets/globalGeojson') as f:
    geojson = geojson.load(f)


listOfPlanes = []
for item in geojson['features']:
    listOfPlanes.append(item["geometry"]["coordinates"])

#7 Kontinente
continentClusters = KMeans(n_clusters=7).fit(listOfPlanes)
# 195 Countries
countryClusters = KMeans(n_clusters=195).fit(listOfPlanes)


print(continentClusters.cluster_centers_, countryClusters.cluster_centers_)