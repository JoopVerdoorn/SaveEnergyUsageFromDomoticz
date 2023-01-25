#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Version 1.2

Python plugin voor Domoticz
Plugin is gebaseerd op stroomkosten.py, te vinden op https://ehoco.nl/stroomkosten-zichtbaar-maken-in-domoticz/
Doelen van dit script:
- historie opbouwen van gas en stroomgebruik, samen met dynamische energietarieven, om later te kunnen evalueren in Excel hoe een dynamisch contract uitgewerkt zou hebben in verhouding tot een vast contract
- dagelijkse energiekosten in Domoticz tonen, op basis van contract met vaste tarieven en met dynamische tarieven
 
Dit script slaat gas en stroomgebruik vanuit Domoticz op in een csv-bestand en moet via cron (in te stellen via crontab -e) elk uur uitgevoerd worden. Het bestand usage.csv moet met het touch-commando aangemaakt wordenOptional it pushes the costs of usage of gas and electricity back to Domo$
Dit script uitvoeren om ..:30 elk uur. Daardoor wordt de uurprijs voor stroom gebruikt die past bij het verbruik van het afgelpen uur, welke om ..:00 opgehaald en berekend wordt.

Nog te doen:
- In csv-bestand EUR/kWh, EUR/m³ en C verwijderen
- Lua-script functionaliteit voor ophalen stroom- en gasprijs naar dit script overzetten 
- Lua-script voor berekenen van werkelijk stroomverbruik (alsof er geen PV-installatie aanwezig is) naar dit script overzetten 
- Kosten van gas toevoegen aan dagelijkse vaste en dynamische energiekosten
- Terugleverkosten vanwege PV aftrekken van dagelijkse vaste en dynamische energiekosten
- Een user variable definieren voor de opslaglocatie van het csv-bestand
- Switch om het berekenen van dagelijkse kosten niet uit te voeren
- Switch om buitentemperatuur niet op te halen en op te slaan
- Switch om werkelijk energieverbruik niet op te halen en op te slaan
- Hier tekst toevoegen over de vereiste modules, te installeren via pip
- Readme-file voor Github-users maken
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

def domoticzread2(idx):
    # ongebruikte functie, te gebruiken om de onderdelen van een object te kunnen zien en die te kunnen gebruiken in domoticzread(idx, var):
    url = DomoBaseURL + idx
    response = requests.get(url)
    jsonData = json.loads(response.text)
    result = jsonData['result'][0]
    print (result)

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
    kWVandaag = domoticzread(EnergiemeterIDX, 'CounterToday')
    kWTotaal = domoticzread(EnergiemeterIDX, 'Counter')
    kwTerugVandaag = domoticzread(EnergiemeterIDX, 'CounterDelivToday') 
    kwTerugTotaal = domoticzread(EnergiemeterIDX, 'CounterDeliv')
    
    werkelijkStroomverbruikVandaag = domoticzread(werkelijkStroomverbruikIDX, 'CounterToday')
    m3Vandaag = domoticzread(GasmeterIDX, 'CounterToday')
    m3Totaal = domoticzread(GasmeterIDX, 'Counter')
    

    # Berekenen van dagelijkse energiekosten bij contract met vaste prijzen
    kWhVerbruikVandaag = kWVandaag.split()[0]
    kostenVerbruikVandaagVast = round((float(kWhVerbruikVandaag) * vasteStroomprijs*100 ) / 100 ,2)
    """Nog aanvullen"""
    
    # Berekenen van dagelijkse energiekosten bij contract met dynamische prijzen
    """Nog aanvullen"""

    nu=dt.datetime.now(dt.timezone.utc)
    datum=utc2local(nu)
    #print(datum)

    # Write values to file
    with open('/home/pi/usage.csv', mode='a') as file:
        # Create a csv writer object and write
        writer = csv.writer(file)
        writer.writerow([datum, kWTotaal, kwTerugTotaal, uurprijsStroom, werkelijkStroomverbruikVandaag, m3Totaal, dagprijsGas, buitenTemperatuur])
        #print("geschreven")
    
    # Energiekosten naar Domoticz schrijven
    kostenVerbruikVandaagVast = str(kostenVerbruikVandaagVast) + " Euro"
    domoticzwrite(energiekostenHuidigContractIDX, kostenVerbruikVandaagVast)

main()


