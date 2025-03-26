import os
import json
import logging
import sqlite3
from datetime import datetime, timedelta

# Probeer de andere componenten te importeren
try:
    from calendar_integration import check_calendar_availability, add_event_to_calendar
    from notification import send_notification, request_permission
except ImportError:
    # Mock functies voor testen
    def check_calendar_availability(start_time, duration_minutes):
        return {"available": True, "suggested_time": start_time}
    
    def add_event_to_calendar(event_details):
        return True
    
    def send_notification(title, body):
        return True
    
    def request_permission(message, job):
        return True

# Configuratie
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'mrfix.db')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_PATH = os.path.join(LOG_DIR, 'filter.log')
PREFERENCES_FILE = os.path.join(DATA_DIR, 'user_preferences.json')

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

class JobFilter:
    def __init__(self):
        """Initialiseer de opdracht filter."""
        self.load_preferences()
        self.setup_database()
        logging.info("JobFilter geïnitialiseerd")

    def load_preferences(self):
        """Laad gebruikersvoorkeuren uit het configuratiebestand."""
        # Standaard voorkeuren
        self.preferences = {
            "prefer_ikea": True,
            "prefer_electrical": True,
            "prefer_internet": True,
            "min_hourly_rate": 79,
            "prefer_urgent": True,
            "max_jobs_weekday": {
                "0": 3,  # Zondag
                "1": 5,  # Maandag
                "2": 2,  # Dinsdag
                "3": 5,  # Woensdag
                "4": 2,  # Donderdag
                "5": 2,  # Vrijdag
                "6": 3,  # Zaterdag
            },
            "prefer_amsterdam": True,
            "max_distance_without_permission": 20,
            "travel_time_between_jobs": 60
        }
        
        try:
            if os.path.exists(PREFERENCES_FILE):
                with open(PREFERENCES_FILE, 'r') as f:
                    user_prefs = json.load(f)
                    # Update de voorkeuren die relevant zijn voor filtering
                    for key in self.preferences:
                        if key in user_prefs:
                            self.preferences[key] = user_prefs[key]
                    
                    logging.info(f"Gebruikersvoorkeuren geladen uit {PREFERENCES_FILE}")
            else:
                logging.warning(f"Voorkeuren bestand niet gevonden: {PREFERENCES_FILE}, standaardwaarden worden gebruikt")
        except Exception as e:
            logging.error(f"Fout bij laden van voorkeuren: {e}")

    def setup_database(self):
        """Initialiseer de SQLite database connectie."""
        try:
            self.conn = sqlite3.connect(DB_PATH)
            self.cursor = self.conn.cursor()
            logging.info("Database connectie opgezet")
        except sqlite3.Error as e:
            logging.error(f"Database fout: {e}")
            raise

    def filter_and_process_jobs(self, new_jobs):
        """Filter en verwerk nieuwe opdrachten."""
        logging.info(f"Start filtering van {len(new_jobs)} nieuwe opdrachten")
        
        # Sorteer opdrachten op prioriteit
        sorted_jobs = self.sort_jobs_by_priority(new_jobs)
        
        for job in sorted_jobs:
            try:
                # Controleer of de opdracht voldoet aan de basisvoorwaarden
                if not self.meets_basic_criteria(job):
                    logging.info(f"Opdracht \"{job['title']}\" voldoet niet aan basisvoorwaarden, overgeslagen")
                    continue
                
                # Controleer of we toestemming nodig hebben voor deze opdracht (buiten Amsterdam)
                if job['distance_to_amsterdam'] > self.preferences['max_distance_without_permission']:
                    logging.info(f"Opdracht \"{job['title']}\" is {job['distance_to_amsterdam']}km van Amsterdam, toestemming vragen")
                    
                    # Vraag toestemming aan de gebruiker
                    permission_message = f"Opdracht buiten Amsterdam ({job['distance_to_amsterdam']}km): {job['title']} in {job['location']}. Accepteren?"
                    permission_granted = request_permission(permission_message, job)
                    
                    if not permission_granted:
                        logging.info(f"Toestemming geweigerd voor opdracht \"{job['title']}\", overgeslagen")
                        continue
                
                # Controleer of er beschikbare tijdslots zijn
                if not job.get('available_timeslots'):
                    logging.info(f"Geen beschikbare tijdslots voor opdracht \"{job['title']}\", overgeslagen")
                    continue
                
                # Selecteer het beste tijdslot
                selected_timeslot = self.select_best_timeslot(job)
                
                if not selected_timeslot:
                    logging.info(f"Geen geschikt tijdslot gevonden voor opdracht \"{job['title']}\", overgeslagen")
                    continue
                
                # Converteer het tijdslot naar een datetime object
                job_date = self.parse_timeslot(selected_timeslot)
                if not job_date:
                    logging.error(f"Kon tijdslot niet parsen voor opdracht \"{job['title']}\": {selected_timeslot}")
                    continue
                
                job_duration = self.estimate_job_duration(job)
                
                logging.info(f"Controleren van beschikbaarheid voor opdracht \"{job['title']}\" op {job_date.isoformat()}")
                
                # Controleer beschikbaarheid in Google Agenda
                availability = check_calendar_availability(
                    job_date,
                    job_duration + self.preferences['travel_time_between_jobs']
                )
                
                if not availability['available']:
                    logging.info(f"Geen beschikbaarheid voor opdracht \"{job['title']}\", overgeslagen")
                    continue
                
                # Controleer of we het maximum aantal opdrachten voor deze dag niet overschrijden
                day_of_week = job_date.weekday()
                jobs_on_same_day = self.count_jobs_on_date(job_date)
                
                max_jobs_key = str(day_of_week)
                if max_jobs_key in self.preferences['max_jobs_weekday']:
                    max_jobs = self.preferences['max_jobs_weekday'][max_jobs_key]
                else:
                    max_jobs = 2  # Standaard maximum
                
                if jobs_on_same_day >= max_jobs:
                    logging.info(f"Maximum aantal opdrachten bereikt voor {job_date.strftime('%Y-%m-%d')}, overgeslagen")
                    continue
                
                # Alles is in orde, accepteer de opdracht
                logging.info(f"Accepteren van opdracht \"{job['title']}\" voor tijdslot {selected_timeslot}")
                
                accepted = self.accept_job(job, selected_timeslot)
                
                if accepted:
                    # Voeg de opdracht toe aan Google Agenda
                    event_details = {
                        'summary': f"MrFix: {job['title']}",
                        'location': job['location'],
                        'description': job['description'],
                        'start_time': job_date,
                        'end_time': job_date + timedelta(minutes=job_duration)
                    }
                    
                    calendar_success = add_event_to_calendar(event_details)
                    
                    if calendar_success:
                        # Markeer de opdracht als geaccepteerd
                        self.mark_job_as_accepted(job, job_date)
                        
                        # Stuur een notificatie naar de gebruiker
                        notification_title = f"Opdracht geaccepteerd: {job['title']}"
                        notification_body = f"Deze opdracht is ingepland op {job_date.strftime('%Y-%m-%d %H:%M')} in {job['location']}"
                        send_notification(notification_title, notification_body)
                    else:
                        logging.error(f"Fout bij toevoegen van opdracht aan agenda: {job['title']}")
                
            except Exception as e:
                logging.error(f"Fout bij verwerken van opdracht \"{job['title']}\": {e}")

    def sort_jobs_by_priority(self, jobs):
        """Sorteer opdrachten op prioriteit."""
        return sorted(jobs, key=self.calculate_priority_score, reverse=True)

    def calculate_priority_score(self, job):
        """Bereken een prioriteitsscore voor een opdracht."""
        score = 0
        
        # Voorkeur voor type opdracht
        if job['is_ikea'] and self.preferences['prefer_ikea']:
            score += 10
        if job['is_electrical'] and self.preferences['prefer_electrical']:
            score += 10
        if job['is_internet'] and self.preferences['prefer_internet']:
            score += 10
        
        # Voorkeur voor uurloon
        if job['hourly_rate'] >= self.preferences['min_hourly_rate']:
            score += 5 + (job['hourly_rate'] - self.preferences['min_hourly_rate']) / 10
        
        # Voorkeur voor urgente opdrachten
        if job['is_urgent'] and self.preferences['prefer_urgent']:
            score += 15
        
        # Voorkeur voor Amsterdam
        if job['is_amsterdam'] and self.preferences['prefer_amsterdam']:
            score += 20
        else:
            # Lagere score voor opdrachten verder van Amsterdam
            score -= job['distance_to_amsterdam'] / 2
        
        return score

    def meets_basic_criteria(self, job):
        """Controleer of een opdracht voldoet aan de basisvoorwaarden."""
        # Controleer of het een voorkeursopdracht is OF het uurloon hoog genoeg is OF het urgent is
        is_preferred_type = (
            (job['is_ikea'] and self.preferences['prefer_ikea']) or
            (job['is_electrical'] and self.preferences['prefer_electrical']) or
            (job['is_internet'] and self.preferences['prefer_internet'])
        )
        
        has_good_rate = job['hourly_rate'] >= self.preferences['min_hourly_rate']
        is_urgent_job = job['is_urgent'] and self.preferences['prefer_urgent']
        
        return is_preferred_type or has_good_rate or is_urgent_job

    def select_best_timeslot(self, job):
        """Selecteer het beste tijdslot voor een opdracht."""
        if not job.get('available_timeslots'):
            return None
        
        # Sorteer tijdslots chronologisch
        sorted_timeslots = sorted(job['available_timeslots'])
        
        # Controleer elk tijdslot op beschikbaarheid in de agenda
        for timeslot in sorted_timeslots:
            try:
                # Converteer het tijdslot naar een datetime object
                slot_datetime = self.parse_timeslot(timeslot)
                if not slot_datetime:
                    continue
                
                # Controleer of dit tijdslot in de toekomst ligt
                if slot_datetime <= datetime.now():
                    continue
                
                # Controleer of we het maximum aantal opdrachten voor deze dag niet overschrijden
                day_of_week = slot_datetime.weekday()
                jobs_on_same_day = self.count_jobs_on_date(slot_datetime)
                
                max_jobs_key = str(day_of_week)
                if max_jobs_key in self.preferences['max_jobs_weekday']:
                    max_jobs = self.preferences['max_jobs_weekday'][max_jobs_key]
                else:
                    max_jobs = 2  # Standaard maximum
                
                if jobs_on_same_day >= max_jobs:
                    continue
                
                # Controleer beschikbaarheid in Google Agenda
                job_duration = self.estimate_job_duration(job)
                availability = check_calendar_availability(
                    slot_datetime,
                    job_duration + self.preferences['travel_time_between_jobs']
                )
                
                if availability['available']:
                    return timeslot
                
            except Exception as e:
                logging.error(f"Fout bij controleren van tijdslot {timeslot}: {e}")
        
        return None

    def parse_timeslot(self, timeslot):
        """Converteer een tijdslot string naar een datetime object."""
        try:
            # Probeer verschillende formaten
            formats = [
                '%Y-%m-%d %H:%M',  # 2025-03-25 18:00
                '%Y-%m-%d %H:%M:%S',  # 2025-03-25 18:00:00
                '%d-%m-%Y %H:%M',  # 25-03-2025 18:00
                '%d/%m/%Y %H:%M',  # 25/03/2025 18:00
                '%d %b %Y %H:%M',  # 25 Mar 2025 18:00
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(timeslot, fmt)
                except ValueError:
                    continue
            
            # Als geen van de formaten werkt, log een waarschuwing
            logging.warning(f"Kon tijdslot niet parsen: {timeslot}")
            return None
            
        except Exception as e:
            logging.error(f"Fout bij parsen van tijdslot: {e}")
            return None

    def estimate_job_duration(self, job):
        """Schat de duur van een opdracht (voor nu gebruiken we een eenvoudige benadering)."""
        # Voor nu gebruiken we een standaard duur van 2 uur (120 minuten)
        # In een echte implementatie zou dit gebaseerd zijn op het type opdracht
        return 120

    def count_jobs_on_date(self, date):
        """Tel het aantal opdrachten op een bepaalde datum."""
        date_str = date.strftime('%Y-%m-%d')
        
        try:
            self.cursor.execute('''
                SELECT COUNT(*) FROM accepted_jobs 
                WHERE DATE(scheduled_date) = DATE(?)
            ''', (date_str,))
            
            count = self.cursor.fetchone()[0]
            return count
        except sqlite3.Error as e:
            logging.error(f"Database fout bij tellen van opdrachten: {e}")
            return 0

    def accept_job(self, job, selected_timeslot):
        """Accepteer een opdracht via de acceptatielink."""
        if not job['accept_link']:
            logging.error(f"Geen acceptatielink gevonden voor opdracht \"{job['title']}\"")
            return False
        
        try:
            # In een echte implementatie zouden we hier Selenium gebruiken om de acceptatielink te volgen
            # en het geselecteerde tijdslot te kiezen
            logging.info(f"Accepteren van opdracht \"{job['title']}\" via link: {job['accept_link']} voor tijdslot: {selected_timeslot}")
            
            # Hier zou de logica komen om de acceptatie te bevestigen
            # Dit is afhankelijk van hoe de MrFix acceptatiepagina werkt
            
            return True
            
        except Exception as e:
            logging.error(f"Fout bij accepteren van opdracht \"{job['title']}\": {e}")
            return False

    def mark_job_as_accepted(self, job, scheduled_date):
        """Markeer een opdracht als geaccepteerd."""
        try:
            self.cursor.execute('''
                INSERT INTO accepted_jobs (
                    id, title, description, location, date_posted,
                    scheduled_date, accepted_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                job['id'], job['title'], job['description'], job['location'],
                job['date_posted'], scheduled_date.isoformat(), datetime.now().isoformat()
            ))
            self.conn.commit()
            logging.info(f"Opdracht gemarkeerd als geaccepteerd: {job['title']}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Database fout bij markeren van opdracht als geaccepteerd: {e}")
            self.conn.rollback()
            return False

    def cleanup(self):
        """Ruim resources op."""
        if hasattr(self, 'conn'):
            self.conn.close()
            logging.info("Database connectie gesloten")

# Singleton instantie
_job_filter = None

def get_job_filter():
    """Verkrijg een singleton instantie van de JobFilter."""
    global _job_filter
    if _job_filter is None:
        _job_filter = JobFilter()
    return _job_filter

def filter_and_process_jobs(new_jobs):
    """Filter en verwerk nieuwe opdrachten."""
    job_filter = get_job_filter()
    try:
        return job_filter.filter_and_process_jobs(new_jobs)
    except Exception as e:
        logging.error(f"Fout bij filteren en verwerken van opdrachten: {e}")
        return False

# Voor testen
if __name__ == "__main__":
    # Test data
    test_jobs = [
        {
            'id': 'test-ikea-job-amsterdam',
            'title': 'IKEA kast monteren',
            'description': 'Montage van een IKEA PAX kast, 2 uur werk, €85 per uur',
            'location': 'Amsterdam',
            'date_posted': '25 maart 2025',
            'accept_link': 'https://klussenvoormij.mrfix.nl/accept/123',
            'is_ikea': True,
            'is_electrical': False,
            'is_internet': False,
            'hourly_rate': 85,
            'is_urgent': False,
            'is_amsterdam': True,
            'distance_to_amsterdam': 0,
            'available_timeslots': [
                '2025-03-25 18:00',
                '2025-03-25 19:00',
                '2025-03-25 20:00',
                '2025-03-26 18:00',
                '2025-03-26 19:00'
            ]
        },
        {
            'id': 'test-electrical-job-amsterdam',
            'title': 'Elektra aanleggen voor nieuwe keuken',
            'description': 'Elektra werkzaamheden voor nieuwe keuken, €90 per uur',
            'location': 'Amsterdam',
            'date_posted': '25 maart 2025',
            'accept_link': 'https://klussenvoormij.mrfix.nl/accept/456',
            'is_ikea': False,
            'is_electrical': True,
            'is_internet': False,
            'hourly_rate': 90,
            'is_urgent': False,
            'is_amsterdam': True,
            'distance_to_amsterdam': 0,
            'available_timeslots': [
                '2025-03-25 21:00',
                '2025-03-25 22:00',
                '2025-03-26 20:00',
                '2025-03-26 21:00'
            ]
        }
    ]
    
    # Test de filtering functie
    filter_and_process_jobs(test_jobs)
