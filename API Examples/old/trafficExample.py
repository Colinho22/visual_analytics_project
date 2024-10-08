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
    "Content-Type": "XML",
    "SOAPAction": "http://opentransportdata.swiss/TDP/Soap_Datex2/Pull/v1/pullMeasurementSiteTable"
}

print(url)
print(headers)
payload = """
<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://schemas.xmlsoap.org/wsdl/" xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" xmlns:soapbind="http://schemas.xmlsoap.org/wsdl/soap/" xmlns:http="http://schemas.xmlsoap.org/wsdl/http/" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:mime="http://schemas.xmlsoap.org/wsdl/mime/" xmlns:tns="http://datex2.eu/wsdl/TDP/Soap_Datex2/Pull/v1" xmlns:d2ns="http://datex2.eu/schema/2/2_0" name="FERDOTDPCHPull" targetNamespace="http://datex2.eu/wsdl/TDP/Soap_Datex2/Pull/v1">
	<documentation>
		PDT Pull service with 2 bindings : 1) base data 2) aggregated traffic data
	</documentation>
	<types>
		<xs:schema targetNamespace="http://datex2.eu/wsdl/TDP/Soap_Datex2/Pull/v1">
			<xs:import namespace="http://datex2.eu/schema/2/2_0" schemaLocation="MeasurementPublications_FEDRO_02-01-00.xsd"/>			
		</xs:schema>
	</types>
	<message name="exchange">
      <part name="exchange" type="d2ns:Exchange"/>
    </message>
	<message name="consumerMessage">
		<part name="consumerBody" element="d2ns:d2LogicalModel"/>
	</message>
	<message name="supplierMessage">
		<part name="supplierBody" element="d2ns:d2LogicalModel"/>
	</message>
	<portType name="PullInterface">
		<operation name="pullMeasurementSiteTable">
			<input message="tns:consumerMessage"/>
			<output message="tns:supplierMessage"/>
		</operation>
	</portType>
	<binding name="PullSoapBinding" type="tns:PullInterface">
		<soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
		<operation name="pullMeasurementSiteTable">
			<soap:operation soapAction="http://opentransportdata.swiss/TDP/Soap_Datex2/Pull/v1/pullMeasurementSiteTable" style="document"/>
			<input>
				<soapbind:body parts="consumerBody" use="literal"/>
			</input>
			<output>
				<soapbind:body parts="supplierBody" use="literal"/>
			</output>
		</operation>
		<operation name="pullMeasuredData">
			<soap:operation soapAction="http://opentransportdata.swiss/TDP/Soap_Datex2/Pull/v1/pullMeasuredData" style="document"/>
			<input>
				<soapbind:body parts="consumerBody" use="literal"/>
			</input>
			<output>
				<soapbind:body parts="supplierBody" use="literal"/>
			</output>
		</operation>
		<operation name="keepAlive">
			<soapbind:operation soapAction="http://opentransportdata.swiss/TDP/Soap_Datex2/Pull/v1/keepAlive" style="document"/>
			<input>
				<soapbind:body parts="exchange" use="literal"/>
			</input>
			<output>
				<soapbind:body parts="exchange" use="literal"/>
			</output>
		</operation>
	</binding>
	<service name="PullService">
		<port name="PullSoapEndPoint" binding="tns:PullSoapBinding">
			<soap:address location="https://api.opentransportdata.swiss/TDP/Soap_Datex2/Pull"/>
		</port>
	</service>
</definitions>
"""
response = requests.post(url, data= payload, headers=headers)

print(response.text)
print(response.content)


#############################
#Abruf der Daten noch nicht erfolgreich
#############################