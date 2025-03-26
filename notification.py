import os
import json
import logging
import requests
from datetime import datetime

# Configuratie
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_PATH = os.path.join(LOG_DIR, 'notification.log')
PREFERENCES_FILE = os.path.join(DATA_DIR, 'user_preferences.json')
NOTIFICATION_CONFIG_FILE = os.path.join(DATA_DIR, 'notification_config.json')

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

class NotificationSystem:
    def __init__(self):
        """Initialiseer het notificatiesysteem."""
        self.load_config()
        logging.info("Notificatiesysteem geïnitialiseerd")

    def load_config(self):
        """Laad notificatie configuratie uit het configuratiebestand."""
        # Standaard configuratie
        self.config = {
            "notification_method": "telegram",  # 'telegram' of 'pushbullet'
            "telegram": {
                "bot_token": "",
                "chat_id": ""
            },
            "pushbullet": {
                "api_key": ""
            },
            "permission_timeout": 600  # 10 minuten in seconden
        }
        
        try:
            # Probeer eerst het specifieke notificatie configuratiebestand
            if os.path.exists(NOTIFICATION_CONFIG_FILE):
                with open(NOTIFICATION_CONFIG_FILE, 'r') as f:
                    notification_config = json.load(f)
                    # Update de configuratie
                    for key, value in notification_config.items():
                        self.config[key] = value
                    
                    logging.info(f"Notificatie configuratie geladen uit {NOTIFICATION_CONFIG_FILE}")
            # Als dat niet bestaat, probeer de algemene voorkeuren
            elif os.path.exists(PREFERENCES_FILE):
                with open(PREFERENCES_FILE, 'r') as f:
                    user_prefs = json.load(f)
                    # Update alleen de notificatie-gerelateerde voorkeuren
                    if "notification_method" in user_prefs:
                        self.config["notification_method"] = user_prefs["notification_method"]
                    if "telegram" in user_prefs:
                        self.config["telegram"] = user_prefs["telegram"]
                    if "pushbullet" in user_prefs:
                        self.config["pushbullet"] = user_prefs["pushbullet"]
                    
                    logging.info(f"Notificatie configuratie geladen uit {PREFERENCES_FILE}")
            else:
                logging.warning(f"Geen configuratiebestanden gevonden, standaardwaarden worden gebruikt")
                logging.warning("Notificaties zullen niet werken zonder geldige configuratie")
        except Exception as e:
            logging.error(f"Fout bij laden van notificatie configuratie: {e}")

    def send_notification(self, title, body):
        """Stuur een notificatie naar de gebruiker."""
        method = self.config["notification_method"]
        
        if method == "telegram":
            return self.send_telegram_notification(title, body)
        elif method == "pushbullet":
            return self.send_pushbullet_notification(title, body)
        else:
            logging.error(f"Onbekende notificatiemethode: {method}")
            return False

    def send_telegram_notification(self, title, body):
        """Stuur een notificatie via Telegram."""
        bot_token = self.config["telegram"]["bot_token"]
        chat_id = self.config["telegram"]["chat_id"]
        
        if not bot_token or not chat_id:
            logging.error("Telegram bot token of chat ID ontbreekt")
            return False
        
        try:
            message = f"*{title}*\n\n{body}"
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                logging.info(f"Telegram notificatie verzonden: {title}")
                return True
            else:
                logging.error(f"Fout bij verzenden van Telegram notificatie: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"Fout bij verzenden van Telegram notificatie: {e}")
            return False

    def send_pushbullet_notification(self, title, body):
        """Stuur een notificatie via Pushbullet."""
        api_key = self.config["pushbullet"]["api_key"]
        
        if not api_key:
            logging.error("Pushbullet API key ontbreekt")
            return False
        
        try:
            url = "https://api.pushbullet.com/v2/pushes"
            headers = {
                "Access-Token": api_key,
                "Content-Type": "application/json"
            }
            data = {
                "type": "note",
                "title": title,
                "body": body
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                logging.info(f"Pushbullet notificatie verzonden: {title}")
                return True
            else:
                logging.error(f"Fout bij verzenden van Pushbullet notificatie: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"Fout bij verzenden van Pushbullet notificatie: {e}")
            return False

    def request_permission(self, message, job):
        """Vraag toestemming aan de gebruiker voor een actie."""
        # In een echte implementatie zou dit een interactieve notificatie sturen
        # en wachten op een antwoord van de gebruiker
        
        # Voor nu simuleren we dit door een notificatie te sturen en altijd True terug te geven
        title = "Toestemming gevraagd"
        body = f"{message}\n\nDetails:\n- Titel: {job['title']}\n- Locatie: {job['location']}\n- Afstand: {job['distance_to_amsterdam']}km\n\nDeze toestemming wordt automatisch goedgekeurd na {self.config['permission_timeout'] / 60} minuten."
        
        self.send_notification(title, body)
        
        logging.info(f"Toestemming gevraagd voor opdracht: {job['title']}")
        
        # In een echte implementatie zou hier een wachtlus komen die wacht op een antwoord
        # Voor nu geven we altijd True terug
        return True

# Singleton instantie
_notification_system = None

def get_notification_system():
    """Verkrijg een singleton instantie van het NotificationSystem."""
    global _notification_system
    if _notification_system is None:
        _notification_system = NotificationSystem()
    return _notification_system

def send_notification(title, body):
    """Stuur een notificatie naar de gebruiker."""
    notification_system = get_notification_system()
    return notification_system.send_notification(title, body)

def request_permission(message, job):
    """Vraag toestemming aan de gebruiker voor een actie."""
    notification_system = get_notification_system()
    return notification_system.request_permission(message, job)

# Voor testen
if __name__ == "__main__":
    # Test het notificatiesysteem
    send_notification(
        "Test Notificatie",
        "Dit is een test notificatie van het MrFix automatiseringssysteem."
    )
    
    # Test toestemming vragen
    test_job = {
        'id': 'test-job',
        'title': 'Test Opdracht',
        'location': 'Utrecht',
        'distance_to_amsterdam': 40
    }
    
    request_permission(
        "Wilt u deze opdracht accepteren die buiten Amsterdam ligt?",
        test_job
    )
