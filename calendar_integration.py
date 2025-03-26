import os
import json
import logging
import pickle
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Configuratie
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_PATH = os.path.join(LOG_DIR, 'calendar.log')
PREFERENCES_FILE = os.path.join(DATA_DIR, 'user_preferences.json')
CREDENTIALS_FILE = os.path.join(DATA_DIR, 'google_credentials.json')
TOKEN_FILE = os.path.join(DATA_DIR, 'google_token.pickle')

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Zorg ervoor dat de data en logs directories bestaan
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Logging configuratie
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Configureer ook logging naar console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

class GoogleCalendarIntegration:
    def __init__(self):
        """Initialiseer de Google Calendar integratie."""
        self.load_preferences()
        self.service = self.get_calendar_service()
        logging.info("Google Calendar integratie geïnitialiseerd")

    def load_preferences(self):
        """Laad gebruikersvoorkeuren uit het configuratiebestand."""
        # Standaard voorkeuren
        self.preferences = {
            "travel_time_between_jobs": 60,  # minuten
            "calendar_id": "primary"  # Gebruik de primaire agenda
        }
        
        try:
            if os.path.exists(PREFERENCES_FILE):
                with open(PREFERENCES_FILE, 'r') as f:
                    user_prefs = json.load(f)
                    # Update de voorkeuren die relevant zijn voor de agenda
                    if "travel_time_between_jobs" in user_prefs:
                        self.preferences["travel_time_between_jobs"] = user_prefs["travel_time_between_jobs"]
                    if "calendar_id" in user_prefs:
                        self.preferences["calendar_id"] = user_prefs["calendar_id"]
                    
                    logging.info(f"Gebruikersvoorkeuren geladen uit {PREFERENCES_FILE}")
            else:
                logging.warning(f"Voorkeuren bestand niet gevonden: {PREFERENCES_FILE}, standaardwaarden worden gebruikt")
        except Exception as e:
            logging.error(f"Fout bij laden van voorkeuren: {e}")

    def get_calendar_service(self):
        """Authenticeer en krijg toegang tot de Google Calendar API."""
        creds = None
        
        # Controleer of er een token bestand is met opgeslagen credentials
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        
        # Als er geen geldige credentials zijn, laat de gebruiker inloggen
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logging.error(f"Fout bij vernieuwen van token: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(CREDENTIALS_FILE):
                    logging.error(f"Google credentials bestand niet gevonden: {CREDENTIALS_FILE}")
                    logging.error("Volg de installatie-instructies om de Google Calendar API te configureren")
                    return None
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    logging.error(f"Fout bij authenticatie: {e}")
                    return None
                
                # Sla de credentials op voor de volgende keer
                with open(TOKEN_FILE, 'wb') as token:
                    pickle.dump(creds, token)
        
        try:
            service = build('calendar', 'v3', credentials=creds)
            logging.info("Google Calendar service succesvol opgezet")
            return service
        except Exception as e:
            logging.error(f"Fout bij opzetten van Google Calendar service: {e}")
            return None

    def check_calendar_availability(self, start_time, duration_minutes):
        """Controleer of er beschikbaarheid is in de agenda voor een bepaalde tijd en duur."""
        if not self.service:
            logging.error("Google Calendar service niet beschikbaar")
            return {"available": False, "suggested_time": None}
        
        try:
            # Bereken de eindtijd
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            # Converteer naar ISO 8601 formaat
            start_iso = start_time.isoformat() + 'Z'  # 'Z' geeft aan dat het UTC tijd is
            end_iso = end_time.isoformat() + 'Z'
            
            # Zoek naar evenementen in dit tijdvak
            events_result = self.service.events().list(
                calendarId=self.preferences["calendar_id"],
                timeMin=start_iso,
                timeMax=end_iso,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                # Geen evenementen gevonden, tijd is beschikbaar
                logging.info(f"Tijd beschikbaar: {start_time.isoformat()} - {end_time.isoformat()}")
                return {"available": True, "suggested_time": start_time}
            else:
                # Evenementen gevonden, tijd is niet beschikbaar
                logging.info(f"Tijd niet beschikbaar: {start_time.isoformat()} - {end_time.isoformat()}")
                
                # Zoek naar de volgende beschikbare tijd
                suggested_time = self.find_next_available_time(end_time, duration_minutes)
                return {"available": False, "suggested_time": suggested_time}
                
        except Exception as e:
            logging.error(f"Fout bij controleren van beschikbaarheid: {e}")
            return {"available": False, "suggested_time": None}

    def find_next_available_time(self, start_from, duration_minutes):
        """Vind de volgende beschikbare tijd in de agenda."""
        if not self.service:
            logging.error("Google Calendar service niet beschikbaar")
            return None
        
        try:
            # Zoek naar evenementen voor de komende 7 dagen
            end_search = start_from + timedelta(days=7)
            
            # Converteer naar ISO 8601 formaat
            start_iso = start_from.isoformat() + 'Z'
            end_iso = end_search.isoformat() + 'Z'
            
            # Haal alle evenementen op voor de komende 7 dagen
            events_result = self.service.events().list(
                calendarId=self.preferences["calendar_id"],
                timeMin=start_iso,
                timeMax=end_iso,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                # Geen evenementen gevonden, start_from is beschikbaar
                return start_from
            
            # Maak een lijst van alle bezette tijdvakken
            busy_periods = []
            for event in events:
                start = event['start'].get('dateTime')
                end = event['end'].get('dateTime')
                
                if start and end:
                    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                    busy_periods.append((start_dt, end_dt))
            
            # Sorteer de bezette tijdvakken
            busy_periods.sort()
            
            # Begin bij start_from en zoek naar een vrij tijdvak
            current_time = start_from
            
            for busy_start, busy_end in busy_periods:
                # Als er genoeg tijd is voor de opdracht voor het volgende bezette tijdvak
                if (busy_start - current_time).total_seconds() / 60 >= duration_minutes:
                    return current_time
                
                # Anders, ga verder na het bezette tijdvak
                current_time = busy_end
            
            # Als we hier komen, is er geen conflict na het laatste bezette tijdvak
            return current_time
            
        except Exception as e:
            logging.error(f"Fout bij zoeken naar volgende beschikbare tijd: {e}")
            return None

    def add_event_to_calendar(self, event_details):
        """Voeg een evenement toe aan de Google Agenda."""
        if not self.service:
            logging.error("Google Calendar service niet beschikbaar")
            return False
        
        try:
            # Maak het evenement
            event = {
                'summary': event_details['summary'],
                'location': event_details['location'],
                'description': event_details['description'],
                'start': {
                    'dateTime': event_details['start_time'].isoformat(),
                    'timeZone': 'Europe/Amsterdam',
                },
                'end': {
                    'dateTime': event_details['end_time'].isoformat(),
                    'timeZone': 'Europe/Amsterdam',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 30},
                        {'method': 'email', 'minutes': 60},
                    ],
                },
            }
            
            # Voeg het evenement toe aan de agenda
            event = self.service.events().insert(
                calendarId=self.preferences["calendar_id"],
                body=event
            ).execute()
            
            logging.info(f"Evenement toegevoegd: {event.get('htmlLink')}")
            return True
            
        except Exception as e:
            logging.error(f"Fout bij toevoegen van evenement: {e}")
            return False

    def get_busy_times_for_day(self, date):
        """Haal alle bezette tijden op voor een specifieke dag."""
        if not self.service:
            logging.error("Google Calendar service niet beschikbaar")
            return []
        
        try:
            # Stel de start- en eindtijd in voor de hele dag
            start_of_day = datetime.combine(date.date(), datetime.min.time())
            end_of_day = datetime.combine(date.date(), datetime.max.time())
            
            # Converteer naar ISO 8601 formaat
            start_iso = start_of_day.isoformat() + 'Z'
            end_iso = end_of_day.isoformat() + 'Z'
            
            # Haal alle evenementen op voor deze dag
            events_result = self.service.events().list(
                calendarId=self.preferences["calendar_id"],
                timeMin=start_iso,
                timeMax=end_iso,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            busy_times = []
            for event in events:
                start = event['start'].get('dateTime')
                end = event['end'].get('dateTime')
                
                if start and end:
                    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                    busy_times.append({
                        'start': start_dt,
                        'end': end_dt,
                        'summary': event.get('summary', 'Bezet')
                    })
            
            return busy_times
            
        except Exception as e:
            logging.error(f"Fout bij ophalen van bezette tijden: {e}")
            return []

# Singleton instantie
_calendar_integration = None

def get_calendar_integration():
    """Verkrijg een singleton instantie van de GoogleCalendarIntegration."""
    global _calendar_integration
    if _calendar_integration is None:
        _calendar_integration = GoogleCalendarIntegration()
    return _calendar_integration

def check_calendar_availability(start_time, duration_minutes):
    """Controleer of er beschikbaarheid is in de agenda voor een bepaalde tijd en duur."""
    calendar = get_calendar_integration()
    return calendar.check_calendar_availability(start_time, duration_minutes)

def add_event_to_calendar(event_details):
    """Voeg een evenement toe aan de Google Agenda."""
    calendar = get_calendar_integration()
    return calendar.add_event_to_calendar(event_details)

def get_busy_times_for_day(date):
    """Haal alle bezette tijden op voor een specifieke dag."""
    calendar = get_calendar_integration()
    return calendar.get_busy_times_for_day(date)

# Voor testen
if __name__ == "__main__":
    # Test de Google Calendar integratie
    calendar = get_calendar_integration()
    
    if calendar.service:
        # Test beschikbaarheid controleren
        now = datetime.now()
        availability = check_calendar_availability(now, 60)
        print(f"Beschikbaarheid voor nu: {availability}")
        
        # Test evenement toevoegen
        if availability['available']:
            event_details = {
                'summary': 'Test MrFix Opdracht',
                'location': 'Amsterdam',
                'description': 'Dit is een test evenement',
                'start_time': now,
                'end_time': now + timedelta(minutes=60)
            }
            success = add_event_to_calendar(event_details)
            print(f"Evenement toegevoegd: {success}")
        
        # Test bezette tijden ophalen
        busy_times = get_busy_times_for_day(now)
        print(f"Bezette tijden voor vandaag: {len(busy_times)}")
        for time in busy_times:
            print(f"  {time['start']} - {time['end']}: {time['summary']}")
    else:
        print("Google Calendar service niet beschikbaar")
