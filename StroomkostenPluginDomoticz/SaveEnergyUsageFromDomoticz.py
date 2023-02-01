#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Version 1.4b
Python plugin voor Domoticz
"""

import requests
import json
import datetime as dt
import pytz
import csv
import time

# Domoticz variabelen - wijzig naar je eigen wens
vasteStroomprijs = 0.232 # kosten per kW in euros, iets boven gemiddelde van dal- en normaaltarief
vasteGasprijs = 0.93579 # kosten per m3 in euros
EnergiemeterIDX = '652' # P1 meter stroom
GasmeterIDX = '662' # P1 meter gas
energiekostenHuidigContractIDX = '699' # Custom sensor in Domoticz, met aslabel Euro
energiekostenDynamischContractIDX = '700' # Custom sensor in Domoticz, met aslabel Euro
actueleStroomprijsIDX = '677' # Custom sensor in Domoticz, met aslabel Euro/kWh, welke via Lua-script elk uur gevuld wordt met actuele stroomprijs
actueleGasprijsIDX = '678' # Custom sensor in Domoticz, met aslabel Euro/m3, welke via Lua elke dag gevuld wordt met actuele stroomprijs
buitenThermometerIDX = '365' # Thermometer met buitentemperatuur
werkelijkStroomverbruikIDX = '670' # Custom sensor (type stroommeter) in Domoticz, welke via Lua-script elk uur gevuld wordt met actueel verbruik (handig als stroom van PV ook direct verbruikt wordt
DomoBaseURL = 'http://192.168.10.10:8080/json.htm?type=devices&rid=' # 192.168.10.10:8080 zijn het IP-adres en de poort waarop Domoticz in je netwerk te benaderen is
DomoWriteURL = 'http://192.168.10.10:8080/json.htm?type=command&param=udevice&nvalue=0&idx='
# Einde van Domoticz variabelen

def utc2local(dagTijd):
    # Utc-tijd omzetten naar lokale tijd Amsterdam
    timeLocal = dagTijd.astimezone(pytz.timezone('Europe/Amsterdam')).strftime('%Y-%m-%d %H:%M:%S')
    return timeLocal

def domoticzread(idx, var):
    # Ophalen waarde van object uit Domoticz
    url = DomoBaseURL + idx
    response = requests.get(url)
    jsonData = json.loads(response.text)
    result = jsonData['result'][0][var]
    return result;

def discoverDeviceCharateristics(idx):
    # ongebruikte functie, te gebruiken om de parameters van een Domoticz device te kunnen ontdekken en die te kunnen gebruiken in domoticzread(idx, var):
    url = DomoBaseURL + idx
    response = requests.get(url)
    jsonData = json.loads(response.text)
    result = jsonData['result'][0]
    print (result)
    return result;

def domoticzwrite(idx, var):
    # Write value of a custom sensor back to Domoticz
    url = DomoWriteURL + idx + '&svalue=' + var
    r = requests.get(url)

def main():
    # Inlezen van data uit Domoticz
    dagprijsGas = domoticzread(actueleGasprijsIDX, 'Data')
    uurprijsStroom = domoticzread(actueleStroomprijsIDX, 'Data')
    buitenTemperatuur = domoticzread(buitenThermometerIDX, 'Data')
    
    # 30 minten slapen om er zeker van te zijn dat juiste  energieprijs om ..:30 wordt opgehaald en verbruik om ..:00
    time.sleep(1800)
    #time.sleep(1) #te gebruiken bij testen

    # Ophalen verbruik vanuit Domoticz op het hele uur
    kWVandaag = domoticzread(EnergiemeterIDX, 'CounterToday')
    kWTotaal = domoticzread(EnergiemeterIDX, 'Counter')
    kWTerugVandaag = domoticzread(EnergiemeterIDX, 'CounterDelivToday') 
    kWTerugTotaal = domoticzread(EnergiemeterIDX, 'CounterDeliv')
    
    werkelijkStroomverbruikVandaag = domoticzread(werkelijkStroomverbruikIDX, 'CounterToday')
    m3Vandaag = domoticzread(GasmeterIDX, 'CounterToday')
    m3Totaal = domoticzread(GasmeterIDX, 'Counter')
    

    # Berekenen van dagelijkse energiekosten bij contract met vaste prijzen
    kWhVerbruikVandaag = kWVandaag.split()[0]
    kWhTerugVandaag = kWTerugVandaag.split()[0]
    m3VerbruikVandaag = m3Vandaag.split()[0]
    kostenVerbruikVandaagVast = round(((float(kWhVerbruikVandaag) - float(kWhTerugVandaag)) * vasteStroomprijs*100 ) / 100 ,2) + round((float(m3VerbruikVandaag) * vasteGasprijs*100 ) / 100 ,2)
    
    # Berekenen van dagelijkse energiekosten bij contract met dynamische prijzen
    kWVandaag = kWVandaag.split()[0]
    kWTerugVandaag = kWTerugVandaag.split()[0]
    m3VerbruikVandaag = m3Vandaag.split()[0]
    dagprijsGas = dagprijsGas.split()[0] 
    uurprijsStroom = uurprijsStroom.split()[0]
    kostenVerbruikVandaagDynamisch = round(((float(kWVandaag) - float(kWTerugVandaag)) * float(uurprijsStroom)*100 ) / 100 ,2) + round((float(m3VerbruikVandaag) * float(dagprijsGas)*100 ) / 100 ,2)

    # Actuele tijd naar lokale tijd zetten
    nu=dt.datetime.now(dt.timezone.utc)
    datum=utc2local(nu)

    # Waarden naar bestaand csv-bestand sturen
    with open('/home/pi/usage.csv', mode='a') as file:
        writer = csv.writer(file)
        writer.writerow([datum, kWTotaal, kWTerugTotaal, uurprijsStroom.replace(" EUR/kWh", ""), werkelijkStroomverbruikVandaag.replace(" kWh", ""), m3Totaal, dagprijsGas.replace(" EUR/m³", ""), buitenTemperatuur.replace(" C", "")])
    
    # Energiekosten naar Domoticz schrijven, alleen om ..:00 dus actueel, want ververst maar 1x per uur
    kostenVerbruikVandaagVast = str(kostenVerbruikVandaagVast) + " Euro"
    kostenVerbruikVandaagDynamisch = str(kostenVerbruikVandaagDynamisch) + " Euro" 
    domoticzwrite(energiekostenHuidigContractIDX, kostenVerbruikVandaagVast)
    domoticzwrite(energiekostenDynamischContractIDX, kostenVerbruikVandaagDynamisch) 

main()