# SaveEnergyUsageFromDomoticz
**Python plugin voor Domoticz**


**Doelen van dit script**

- historie opbouwen van gas en stroomgebruik, samen met dynamische energietarieven, om later te kunnen evalueren in Excel hoe een dynamisch contract uitgewerkt zou hebben in verhouding tot een vast contract
- dagelijkse energiekosten in Domoticz tonen, op basis van contract met vaste tarieven en met dynamische tarieven

**Verwijzingen**

Plugin is mede gebaseerd op stroomkosten.py, te vinden op <https://ehoco.nl/stroomkosten-zichtbaar-maken-in-domoticz/>

Dit script verwerkt dynamische prijzen uit Domoticz voor gas en stroom. Deze kunnenvia dit dzVents-script door Domoticz opgehaald kunnen worden: <https://gist.github.com/kipusoep/e1e0804ba7503e6806e8b7ec03298dfa>

Verder slaat dit script ook het werkelijke stroomverbruik op, zodat in een spreadsheetprogramma ook simulaties met een virtuele batterij gedaan kunnen worden. Dit werkelijke stroomverbruik is bij aanwezigheid van zonnepanelen niet alleen uit de P1 meter af te leiden, vandaar dit dzVents-script, welke overigens niet van mijzelf is: <https://github.com/JoopVerdoorn/CalculateRealElectricityUsageWithPV>


**Werking van het script**

Dit script slaat gas en stroomgebruik vanuit Domoticz op in een csv-bestand en moet via cron elk uur uitgevoerd worden. Om het energieverbruik beter te kunnen duiden wordt ook de buitentemperatuur elk uur opgeslagen

Dit script runt om ..:30 elk uur. Daardoor wordt de uurprijs voor stroom gebruikt die past bij het verbruik van het afgelpen uur, welke 30 minuten later om ..:00 opgehaald en berekend wordt.

Op dat moment wordt in het bestand /home/pi/usage.csv een nieuwe regel aangemaakt in de directory van waaruit het script gerund wordt. 

**Randvoorwaarden**

In deze readme wordt aangenomen dat python versie 3 geinstalleerd is en dat Domoticz met de scripts die onder verwijzingen genoemd zijn draait. Uiteraard moet Domoticz een slimme meter uitlezen.

Tenslotte wordt aangenomen dat /home/pi/usage.csv bestaat.  

**Installatie**

In Domoticz 2 virtuele sensors aanmaken, beiden Custom sensors met aslabel Euro: energiekostenHuidigContractIDX en energiekostenDynamischContractIDX

Dit script opslaan als SaveEnergyUsageFromDomoticz.py in /home/pi/domoticz/scripts/python/

Domoticz-variabelen wijzigen in het script aan de hand van jouw Domoticz-apparaten.

Het bestand usage.csv aanmaken:

touch /home/pi/usage.csv

In /home/pi/ het bestand SaveEnergyUsageFromDomoticz\_wrapper aanmaken met als inhoud: 

/usr/bin/python3 /home/pi/domoticz/scripts/python/SaveEnergyUsageFromDomoticz.py

Het wrapperbestand uitvoerbaar maken door: 

chmod +x SaveEnergyUsageFromDomoticz\_wrapper

Het wrapperbestand elk uur laten uitvoeren om ..:30, door cron in te stellen via een extra regel in crontab (te openen door crontab -e):

30 \* \* \* \* /home/pi/stroomkostenwrapper


