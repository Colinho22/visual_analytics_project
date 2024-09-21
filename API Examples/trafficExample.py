import pandas as pd
import requests
import xml.etree.ElementTree as ET


#Your token for this API is: eyJvcmciOiI2NDA2NTFhNTIyZmEwNTAwMDEyOWJiZTEiLCJpZCI6IjJkMmMzNGU0ZmMzZDRkN2JhOGVmNjMyOWVhZTE5MTg3IiwiaCI6Im11cm11cjEyOCJ9 and we will only show this once. Please save it somewhere now
#token Page: https://opentransportdata.swiss/de/dev-dashboard/


url = "https://api.opentransportdata.swiss/TDP/Soap_Datex2/Pull"
#url = "http://opentransportdata.swiss/TDP/Soap_Datex2/Pull/v1/pullMeasuredData"
#url = "http://opentransportdata.swiss/TDP/Soap_Datex2/Pull/v1/pullMeasurementSiteTable"
token  = "eyJvcmciOiI2NDA2NTFhNTIyZmEwNTAwMDEyOWJiZTEiLCJpZCI6IjJkMmMzNGU0ZmMzZDRkN2JhOGVmNjMyOWVhZTE5MTg3IiwiaCI6Im11cm11cjEyOCJ9"

headers = {
    "Authorization": token,
    "Content-Type": "text/XML",
    "SoapAction": "http://opentransportdata.swiss/TDP/Soap_Datex2/Pull/v1/pullMeasurementSiteTable"
}

print(url)
print(headers)
response = requests.post(url, headers=headers)

print(response.text)
print(response.content)


#############################
#Abruf der Daten noch nicht erfolgreich
#############################