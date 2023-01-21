#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""

stroomkosten.py

Leest 'CounterToday' van de energiemeter uit en schrijft de berekende kosten naar een custom sensor. Het script wordt gedraaid via de crontab.

"""

import requests
import json
import datetime as dt
import pytz
import csv

# Domoticz variabelen - wijzig naar je eigen wens

vast = 0 # vaste kosten in eurocenten
eenheid = 1 # kosten per kW in eurocenten

EnergiemeterIDX = '652'
GasmeterIDX = '662'
CustomSensorIDX = '699'
DomoBaseURL = 'http://192.168.10.10:8080/json.htm?type=devices&rid='
DomoWriteURL = 'http://192.168.10.10:8080/json.htm?type=command&param=udevice&nvalue=0&idx='

# Einde van Domoticz variabelen

def utc2local(dagTijd):
    timeLocal = dagTijd.astimezone(pytz.timezone('Europe/Amsterdam')).strftime('%Y-%m-%d %H:%M:%S')
    return timeLocal

def domoticzread(idx, var):
    url = DomoBaseURL + idx
    response = requests.get(url)
    jsonData = json.loads(response.text)
    result = jsonData['result'][0][var]
    return result;

kWVandaag = domoticzread(EnergiemeterIDX, 'CounterToday')
kWTotaal = domoticzread(EnergiemeterIDX, 'Counter')
kwTerugVandaag = domoticzread(EnergiemeterIDX, 'CounterDelivToday') 
kwTerugTotaal = domoticzread(EnergiemeterIDX, 'CounterDeliv')

m3Vandaag = domoticzread(GasmeterIDX, 'CounterToday')
m3Totaal = domoticzread(GasmeterIDX, 'Counter')
kWhVerbruikVandaag = kWVandaag.split()[0]
kostenVerbruikVandaag = round((float(kWhVerbruikVandaag) * eenheid + vast) / 100 ,2)
kostenVerbruikVandaag = str(kostenVerbruikVandaag) + " Euro"
#print ("kW verbruikt vandaag en kosten ", kWVandaag, kostenVerbruikVandaag)
#print ("kW verbruikt totaal ", kWTotaal)
#print ("kW geleverd vandaag ", kwTerugVandaag)
#print ("kW geleverd totaal ", kwTerugTotaal)
#print ("m3 verbruikt vandaag ", m3Vandaag)
#print ("m3 verbruikt totaal ", m3Totaal)

nu=dt.datetime.now(dt.timezone.utc)
datum=utc2local(nu)
#print(datum)

# Write values to file
with open('/home/pi/usage.csv', mode='a') as file:
    # Create a csv writer object and write
    writer = csv.writer(file)
    writer.writerow([datum, kWTotaal, kwTerugTotaal, m3Totaal])
    print("geschreven")


# Write value current spendage to
url = DomoWriteURL + CustomSensorIDX + '&svalue=' + kostenVerbruikVandaag
r = requests.get(url)
