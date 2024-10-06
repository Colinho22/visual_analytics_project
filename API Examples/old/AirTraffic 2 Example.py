import requests

key = '70b36ebfd410582cc400eeeb0f832218'
params = {
  'access_key': key
}

api_result = requests.get('https://api.aviationstack.com/v1/flights', params)

api_response = api_result.json()
#print(api_response)

for flight in api_response['data']:
    #if (flight['live'].keys()
    #if (flight['live']['is_ground'] is False):
    print(u'%s flight %s from %s (%s) to %s (%s) is in the air.' % (
        flight['airline']['name'],
        flight['flight']['iata'],
        flight['departure']['airport'],
        flight['departure']['iata'],
        flight['arrival']['airport'],
        flight['arrival']['iata']))


#############################
#NUR 100 Abrufe pro Monat
#Sonst KOSTET 4.50.- im Monat
#############################