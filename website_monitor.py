import time
import requests
import logging
from bs4 import BeautifulSoup
import json
import os
from notification import send_notification

# Configureer logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WebsiteMonitor:
    def __init__(self, url, check_interval=1):  # Interval gewijzigd naar 1 seconde
        self.url = url
        self.check_interval = check_interval  # in seconden
        self.last_content = None
        self.running = False
        
        # Maak data directory als deze niet bestaat
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Bestandspad voor opgeslagen content
        self.content_file = os.path.join(self.data_dir, 'last_content.json')
        
        # Laad eerder opgeslagen content indien beschikbaar
        self.load_saved_content()
    
    def load_saved_content(self):
        """Laad eerder opgeslagen website content."""
        try:
            if os.path.exists(self.content_file):
                with open(self.content_file, 'r') as f:
                    self.last_content = json.load(f)
                logging.info("Eerder opgeslagen content geladen.")
        except Exception as e:
            logging.error(f"Fout bij laden van opgeslagen content: {e}")
    
    def save_content(self, content):
        """Sla huidige website content op."""
        try:
            with open(self.content_file, 'w') as f:
                json.dump(content, f)
        except Exception as e:
            logging.error(f"Fout bij opslaan van content: {e}")
    
    def check_website(self):
        """Controleer de website op veranderingen."""
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Hier zou je specifieke elementen kunnen extraheren
            # Voor dit voorbeeld gebruiken we de volledige HTML
            current_content = response.text
            
            # Voor een betere vergelijking, extraheer alleen relevante delen
            # Bijvoorbeeld, alleen de opdrachten sectie
            # jobs_section = soup.find('div', class_='jobs-list')
            # current_content = str(jobs_section) if jobs_section else ""
            
            # Vergelijk met vorige content
            if self.last_content is not None and current_content != self.last_content:
                logging.info("Verandering gedetecteerd op de website!")
                # Stuur notificatie
                send_notification("Website Verandering", 
                                 f"Er is een verandering gedetecteerd op {self.url}")
            
            # Update laatste content
            self.last_content = current_content
            self.save_content(current_content)
            
        except Exception as e:
            logging.error(f"Fout bij controleren van website: {e}")
    
    def start_monitoring(self):
        """Start het monitoren van de website."""
        self.running = True
        logging.info(f"Start monitoring van {self.url} elke {self.check_interval} seconde(n).")
        
        try:
            while self.running:
                self.check_website()
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            logging.info("Monitoring gestopt door gebruiker.")
            self.running = False
    
    def stop_monitoring(self):
        """Stop het monitoren van de website."""
        self.running = False
        logging.info("Monitoring gestopt.")

# Voorbeeld gebruik
if __name__ == "__main__":
    # Vervang met de URL die je wilt monitoren
    monitor = WebsiteMonitor("https://example.com", check_interval=1) 
    monitor.start_monitoring()
