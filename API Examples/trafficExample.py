import pandas as pd
import requests

#Your token for this API is: eyJvcmciOiI2NDA2NTFhNTIyZmEwNTAwMDEyOWJiZTEiLCJpZCI6IjJkMmMzNGU0ZmMzZDRkN2JhOGVmNjMyOWVhZTE5MTg3IiwiaCI6Im11cm11cjEyOCJ9 and we will only show this once. Please save it somewhere now
#token Page: https://opentransportdata.swiss/de/dev-dashboard/



import pandas as pd

url = "https://api.opentransportdata.swiss/TDP/Soap_Datex2/Pull"
geoData = pd.read_json(url)

print(geoData)


url = "https://api.opentransportdata.swiss/TDP/Soap_Datex2/Pull"
token  = "eyJvcmciOiI2NDA2NTFhNTIyZmEwNTAwMDEyOWJiZTEiLCJpZCI6IjJkMmMzNGU0ZmMzZDRkN2JhOGVmNjMyOWVhZTE5MTg3IiwiaCI6Im11cm11cjEyOCJ9"

headers = {
    "Authorization": "eyJvcmciOiI2NDA2NTFhNTIyZmEwNTAwMDEyOWJiZTEiLCJpZCI6IjJkMmMzNGU0ZmMzZDRkN2JhOGVmNjMyOWVhZTE5MTg3IiwiaCI6Im11cm11cjEyOCJ9",
    "Content-Type": "application/XML"
}

response = requests.get(url, headers=headers)
print(response.text)