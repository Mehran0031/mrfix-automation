# MrFix Opdracht Automatisering - Architectuur met GUI

## Overzicht
Dit document beschrijft de architectuur van het geautomatiseerde systeem voor het monitoren, filteren, accepteren en inplannen van MrFix opdrachten volgens de voorkeuren van de gebruiker, geïmplementeerd in Python met een Tkinter GUI.

## Systeemcomponenten

### 1. GUI Component
- **Technologie**: Python Tkinter
- **Functionaliteit**:
  - Gebruiksvriendelijke interface voor het beheren van voorkeuren
  - Tabs voor verschillende categorieën voorkeuren:
    - Opdrachttypes (IKEA, elektriciteit, internet, minimum uurloon)
    - Planning (maximum aantal opdrachten per dag)
    - Locatie (Amsterdam voorkeuren, maximale afstand)
    - Notificaties (Telegram of Pushbullet configuratie)
  - Opslaan en laden van voorkeuren in JSON-formaat
  - Testen van notificatie-instellingen

### 2. Website Monitoring Component
- **Technologie**: Python met Selenium/BeautifulSoup
- **Functionaliteit**:
  - Periodiek de MrFix website (https://klussenvoormij.mrfix.nl/3900) bezoeken
  - HTML-inhoud ophalen en parseren
  - Nieuwe opdrachten detecteren
  - Details van opdrachten extraheren (type, locatie, uurloon, urgentie)
  - Beschikbare tijdslots identificeren
  - Gegevens doorgeven aan het filtering component

### 3. Opdracht Filtering & Acceptatie Component
- **Technologie**: Python
- **Functionaliteit**:
  - Opdrachten filteren op basis van gebruikersvoorkeuren:
    - Type: IKEA-gerelateerd, elektriciteitsklussen, internet-gerelateerd
    - Uurloon: Minimum drempelwaarde
    - Urgentie: Urgente opdrachten prioriteren
  - Locatie controleren:
    - Amsterdam opdrachten prioriteren
    - Afstand berekenen voor opdrachten buiten Amsterdam
  - Beschikbaarheid controleren via Google Agenda API
  - Planningsregels toepassen:
    - Maximum aantal opdrachten per dag (instelbaar per dag)
    - Reistijd tussen opdrachten
  - Opdrachten accepteren via de beschikbare links
  - Communiceren met het notificatie component

### 4. Google Agenda Integratie Component
- **Technologie**: Python met Google API Client Library
- **Functionaliteit**:
  - Authenticeren met Google Calendar API
  - Beschikbare tijdslots identificeren
  - Nieuwe afspraken toevoegen voor geaccepteerde opdrachten
  - Reistijd tussen opdrachten inplannen

### 5. Notificatie Component
- **Technologie**: Python met Telegram/Pushbullet API
- **Functionaliteit**:
  - Pushnotificaties sturen bij succesvolle inplanning
  - Toestemming vragen voor opdrachten buiten maximale afstand
  - Statusupdates versturen over systeemactiviteit
  - Ondersteuning voor zowel Telegram als Pushbullet

### 6. Hoofdapplicatie Component
- **Technologie**: Python
- **Functionaliteit**:
  - Integratie van alle componenten
  - Opstarten van de GUI
  - Beheren van de monitoring loop
  - Foutafhandeling en logging

## Datastromen

1. **GUI → Voorkeuren Opslag**:
   - Gebruikersvoorkeuren worden opgeslagen in JSON-formaat

2. **Voorkeuren Opslag → Componenten**:
   - Alle componenten lezen de gebruikersvoorkeuren

3. **Website Monitoring → Opdracht Filtering**:
   - Nieuwe opdrachten met geëxtraheerde details

4. **Opdracht Filtering → Google Agenda**:
   - Verzoeken om beschikbaarheid te controleren
   - Instructies om nieuwe afspraken toe te voegen

5. **Opdracht Filtering → Notificatie**:
   - Verzoeken om pushnotificaties te versturen
   - Verzoeken om toestemming voor opdrachten buiten maximale afstand

6. **Notificatie → Opdracht Filtering**:
   - Gebruikersreacties op toestemmingsverzoeken

## Bestandsstructuur

```
mrfix-python-gui/
├── README.md                  # Projectdocumentatie en installatie-instructies
├── requirements.txt           # Python dependencies
├── gui.py                     # GUI component
├── website_monitor.py         # Website monitoring component
├── job_filter.py              # Opdracht filtering component
├── calendar_integration.py    # Google Agenda integratie component
├── notification.py            # Notificatie component
├── app.py                     # Hoofdapplicatie
├── test.py                    # Testcode
├── data/                      # Data directory
│   ├── user_preferences.json  # Gebruikersvoorkeuren
│   ├── google_credentials.json # Google API credentials
│   └── notification_config.json # Notificatie configuratie
└── logs/                      # Log bestanden
```

## Implementatiedetails

### Monitoring Frequentie
- Elke 5 minuten de MrFix website controleren op nieuwe opdrachten (instelbaar)

### Authenticatie
- OAuth 2.0 voor Google Calendar API
- API tokens voor notificatiediensten (Telegram/Pushbullet)

### Opslag
- JSON bestanden voor configuratie en voorkeuren
- SQLite database voor:
  - Reeds gecontroleerde opdrachten
  - Geaccepteerde opdrachten

### Foutafhandeling
- Uitgebreide logging naar bestand
- Foutmeldingen in de GUI
- Automatische herverbinding bij netwerkfouten

## Gebruikersinteractie

### Voorkeuren Instellen
1. Gebruiker start de applicatie
2. GUI wordt getoond met huidige voorkeuren
3. Gebruiker past voorkeuren aan in de verschillende tabs
4. Gebruiker slaat voorkeuren op
5. Systeem gebruikt nieuwe voorkeuren voor toekomstige opdrachten

### Automatische Monitoring
1. Systeem controleert periodiek de MrFix website
2. Nieuwe opdrachten worden gefilterd volgens voorkeuren
3. Geschikte opdrachten worden geaccepteerd en ingepland
4. Gebruiker ontvangt notificaties over geaccepteerde opdrachten

### Toestemming Vragen
1. Systeem detecteert een opdracht buiten de maximale afstand
2. Notificatie wordt verzonden met verzoek om toestemming
3. Gebruiker reageert op de notificatie
4. Systeem verwerkt de reactie en handelt de opdracht af

## GitHub Integratie
- Volledige code en documentatie beschikbaar op GitHub
- Duidelijke installatie-instructies in README.md
- requirements.txt voor eenvoudige installatie van dependencies
- Licentie-informatie
- Bijdrage-richtlijnen

## Toekomstige Uitbreidingen
- Dashboard voor het bekijken van statistieken
- Meer geavanceerde planningsalgoritmen
- Integratie met routeplanners voor nauwkeurigere reistijdschattingen
- Ondersteuning voor meerdere MrFix accounts
