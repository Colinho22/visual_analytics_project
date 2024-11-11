import http.client

conn = http.client.HTTPSConnection("fr24api.flightradar24.com")
payload = ''
headers = {
  'Accept': 'application/json',
  'Accept-Version': 'v1',
  'Authorization': 'Bearer <9d0fa97c-5c9f-4aa2-b5ec-8d89c60fdb2c|4onPhSN7swU8Ww0myfrMaELGuYvWZGUL34FKz34i3c31915f>'
}
conn.request("GET", "/api/live/flight-positions/light?bounds=50.682,46.218,14.422,22.243", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))


#############################
#KOSTET 9.- im Monat
#############################