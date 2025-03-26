# MrFix Opdracht Automatisering

Een Python-applicatie met GUI voor het automatisch monitoren, filteren, accepteren en inplannen van MrFix opdrachten volgens uw voorkeuren.

## Functionaliteiten

- **Website Monitoring**: Controleert automatisch de MrFix website op nieuwe opdrachten
- **Slim Filteren**: Selecteert opdrachten op basis van uw voorkeuren:
  - IKEA-gerelateerde opdrachten
  - Elektriciteitsklussen
  - Internet-gerelateerde opdrachten
  - Opdrachten met uurloon ≥€79
  - Urgente opdrachten
- **Agenda Integratie**: Controleert uw Google Agenda en plant opdrachten in volgens uw voorkeuren:
  - Meer opdrachten op maandag en woensdag
  - Maximaal 2 opdrachten op di/do/vr
  - Maximaal 3 opdrachten in het weekend
  - 1 uur reistijd tussen opdrachten in Amsterdam
- **Locatie Voorkeuren**: 
  - Prioriteit voor opdrachten in Amsterdam
  - Vraagt toestemming voor opdrachten buiten 20km van Amsterdam
- **Tijdslot Selectie**: Kiest automatisch het beste beschikbare tijdslot uit de opties die MrFix aanbiedt
- **Notificaties**: Stuurt u pushberichten via Telegram of Pushbullet
- **Gebruiksvriendelijke GUI**: Pas al uw voorkeuren eenvoudig aan via de interface

## Installatie

### Vereisten

- Python 3.8 of hoger
- Google account voor Google Agenda integratie
- Telegram of Pushbullet account voor notificaties

### Stappen

1. Clone deze repository:
   ```
   git clone https://github.com/uw-gebruikersnaam/mrfix-automation.git
   cd mrfix-automation
   ```

2. Maak een virtuele omgeving aan en activeer deze:
   ```
   python -m venv venv
   source venv/bin/activate  # Op Windows: venv\Scripts\activate
   ```

3. Installeer de benodigde packages:
   ```
   pip install -r requirements.txt
   ```

4. Download de Chrome WebDriver voor Selenium:
   - Ga naar: https://chromedriver.chromium.org/downloads
   - Download de versie die overeenkomt met uw Chrome browser
   - Plaats het `chromedriver` bestand in de hoofdmap van het project

5. Configureer de Google Calendar API:
   - Volg de instructies in [Google Calendar API Setup](docs/google_calendar_setup.md)
   - Plaats het `google_credentials.json` bestand in de `data` map

6. Configureer het notificatiesysteem:
   - Voor Telegram: Volg de instructies in [Telegram Setup](docs/telegram_setup.md)
   - Voor Pushbullet: Volg de instructies in [Pushbullet Setup](docs/pushbullet_setup.md)
   - Maak een bestand `notification_config.json` in de `data` map

## Gebruik

1. Start de applicatie:
   ```
   python app.py
   ```

2. Pas uw voorkeuren aan in de "Voorkeuren" tab:
   - Opdrachttypes (IKEA, elektriciteit, internet)
   - Planning (maximum aantal opdrachten per dag)
   - Locatie (Amsterdam voorkeuren, maximale afstand)
   - Notificatie-instellingen (Telegram of Pushbullet)

3. Start de monitoring in de "Dashboard" tab

4. Bekijk de logboeken in de "Logboek" tab

## Projectstructuur

```
mrfix-python-gui/
├── README.md                  # Projectdocumentatie
├── requirements.txt           # Python dependencies
├── app.py                     # Hoofdapplicatie
├── gui.py                     # GUI component
├── website_monitor.py         # Website monitoring component
├── job_filter.py              # Opdracht filtering component
├── calendar_integration.py    # Google Agenda integratie component
├── notification.py            # Notificatie component
├── test.py                    # Testcode
├── docs/                      # Documentatie
│   ├── google_calendar_setup.md
│   ├── telegram_setup.md
│   └── pushbullet_setup.md
├── data/                      # Data directory (wordt automatisch aangemaakt)
│   ├── user_preferences.json  # Gebruikersvoorkeuren
│   ├── google_credentials.json # Google API credentials
│   └── notification_config.json # Notificatie configuratie
└── logs/                      # Log bestanden (wordt automatisch aangemaakt)
```

## Configuratie

### user_preferences.json

Dit bestand wordt automatisch aangemaakt en bijgewerkt via de GUI. Handmatige aanpassingen zijn mogelijk, maar gebruik bij voorkeur de GUI.

### notification_config.json

Voorbeeld voor Telegram:
```json
{
  "notification_method": "telegram",
  "telegram": {
    "bot_token": "UW_BOT_TOKEN",
    "chat_id": "UW_CHAT_ID"
  },
  "pushbullet": {
    "api_key": ""
  },
  "permission_timeout": 600
}
```

Voorbeeld voor Pushbullet:
```json
{
  "notification_method": "pushbullet",
  "telegram": {
    "bot_token": "",
    "chat_id": ""
  },
  "pushbullet": {
    "api_key": "UW_API_KEY"
  },
  "permission_timeout": 600
}
```

## Bijdragen

Bijdragen zijn welkom! Volg deze stappen:

1. Fork de repository
2. Maak een feature branch: `git checkout -b mijn-nieuwe-feature`
3. Commit uw wijzigingen: `git commit -am 'Voeg nieuwe feature toe'`
4. Push naar de branch: `git push origin mijn-nieuwe-feature`
5. Dien een Pull Request in

## Licentie

Dit project is gelicenseerd onder de MIT Licentie - zie het [LICENSE](LICENSE) bestand voor details.

## Contact

Als u vragen heeft of hulp nodig heeft, neem dan contact op via GitHub issues.
