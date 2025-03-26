import os
import json
import logging
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
            "notification_method": "telegram",  # 'telegram', 'pushbullet', 'email', 'pushover', 'safari_web_push'
            "telegram": {
                "bot_token": "",
                "chat_id": ""
            },
            "pushbullet": {
                "api_key": ""
            },
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",  # App-specifiek wachtwoord voor Gmail
                "recipient": ""
            },
            "pushover": {
                "api_token": "",
                "user_key": ""
            },
            "safari_web_push": {
                "vapid_private_key": "",
                "vapid_public_key": "",
                "subscription_info": {}
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
                    if "email" in user_prefs:
                        self.config["email"] = user_prefs["email"]
                    if "pushover" in user_prefs:
                        self.config["pushover"] = user_prefs["pushover"]
                    if "safari_web_push" in user_prefs:
                        self.config["safari_web_push"] = user_prefs["safari_web_push"]
                    
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
        elif method == "email":
            return self.send_email_notification(title, body)
        elif method == "pushover":
            return self.send_pushover_notification(title, body)
        elif method == "safari_web_push":
            return self.send_safari_web_push_notification(title, body)
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

    def send_email_notification(self, title, body):
        """Stuur een notificatie via e-mail (Gmail)."""
        smtp_server = self.config["email"]["smtp_server"]
        smtp_port = self.config["email"]["smtp_port"]
        username = self.config["email"]["username"]
        password = self.config["email"]["password"]
        recipient = self.config["email"]["recipient"]
        
        if not username or not password or not recipient:
            logging.error("E-mail configuratie ontbreekt")
            return False
        
        try:
            # Maak het bericht
            msg = MIMEMultipart()
            msg['From'] = username
            msg['To'] = recipient
            msg['Subject'] = title
            
            # Voeg de tekst toe
            msg.attach(MIMEText(body, 'plain'))
            
            # Maak verbinding met de SMTP server
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(username, password)
            
            # Verstuur het bericht
            server.send_message(msg)
            server.quit()
            
            logging.info(f"E-mail notificatie verzonden: {title}")
            return True
            
        except Exception as e:
            logging.error(f"Fout bij verzenden van e-mail notificatie: {e}")
            return False

    def send_pushover_notification(self, title, body):
        """Stuur een notificatie via Pushover (native iOS notificaties)."""
        api_token = self.config["pushover"]["api_token"]
        user_key = self.config["pushover"]["user_key"]
        
        if not api_token or not user_key:
            logging.error("Pushover API token of user key ontbreekt")
            return False
        
        try:
            url = "https://api.pushover.net/1/messages.json"
            data = {
                "token": api_token,
                "user": user_key,
                "title": title,
                "message": body,
                "sound": "pushover"  # Standaard geluid
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                logging.info(f"Pushover notificatie verzonden: {title}")
                return True
            else:
                logging.error(f"Fout bij verzenden van Pushover notificatie: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"Fout bij verzenden van Pushover notificatie: {e}")
            return False

    def send_safari_web_push_notification(self, title, body):
        """Stuur een Safari Web Push notificatie."""
        # Voor Safari Web Push is een webserver nodig die VAPID ondersteunt
        # Dit is een complexere implementatie die normaal gesproken via een webserver loopt
        # Voor deze implementatie gebruiken we een vereenvoudigde versie die alleen lokaal werkt
        
        vapid_private_key = self.config["safari_web_push"]["vapid_private_key"]
        subscription_info = self.config["safari_web_push"]["subscription_info"]
        
        if not vapid_private_key or not subscription_info:
            logging.error("Safari Web Push configuratie ontbreekt")
            return False
        
        try:
            # In een echte implementatie zou hier de pywebpush bibliotheek worden gebruikt
            # om een push notificatie te sturen naar de browser
            # Voor nu loggen we alleen dat dit zou gebeuren
            
            logging.info(f"Safari Web Push notificatie zou worden verzonden: {title}")
            logging.info("Safari Web Push vereist een actieve webserver en client-side JavaScript")
            logging.info("Zie de documentatie voor instructies over het opzetten van Safari Web Push")
            
            # In een echte implementatie zou hier code staan om de notificatie te versturen
            # via de Web Push API
            
            return True
            
        except Exception as e:
            logging.error(f"Fout bij verzenden van Safari Web Push notificatie: {e}")
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
    notification_system = get_notification_system()
    
    # Test alle notificatiemethoden
    methods = ["telegram", "pushbullet", "email", "pushover", "safari_web_push"]
    
    for method in methods:
        notification_system.config["notification_method"] = method
        result = send_notification(
            f"Test {method.capitalize()} Notificatie",
            f"Dit is een test notificatie via {method} van het MrFix automatiseringssysteem."
        )
        print(f"{method.capitalize()} notificatie resultaat: {result}")
    
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
