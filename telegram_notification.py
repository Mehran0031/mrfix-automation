import requests
import logging
import os
import json

class TelegramNotifier:
    def __init__(self, bot_token=None, chat_id=None):
        """
        Initialiseer de Telegram notifier.
        
        Args:
            bot_token (str): Telegram bot token
            chat_id (str): Telegram chat ID
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        
        # Als geen token/chat_id is opgegeven, probeer uit config te laden
        if not bot_token or not chat_id:
            self.load_config()
        
        # Configureer logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'notification.log')),
                logging.StreamHandler()
            ]
        )
    
    def load_config(self):
        """Laad Telegram configuratie uit het voorkeuren bestand."""
        try:
            config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'user_preferences.json')
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    preferences = json.load(f)
                
                telegram_config = preferences.get('telegram', {})
                self.bot_token = telegram_config.get('bot_token', self.bot_token)
                self.chat_id = telegram_config.get('chat_id', self.chat_id)
        except Exception as e:
            logging.error(f"Fout bij laden Telegram configuratie: {e}")
    
    def send_notification(self, message, job=None):
        """
        Stuur een Telegram notificatie.
        
        Args:
            message (str): Het bericht om te verzenden
            job (dict, optional): Opdracht details om toe te voegen aan het bericht
        
        Returns:
            bool: True als het bericht succesvol is verzonden, anders False
        """
        if not self.bot_token or not self.chat_id:
            logging.error("Telegram bot token of chat ID ontbreekt. Kan geen notificatie verzenden.")
            return False
        
        try:
            # Bereid het bericht voor
            text = message
            
            # Voeg opdracht details toe als beschikbaar
            if job:
                text += f"\n\nOpdracht details:"
                for key, value in job.items():
                    text += f"\n{key}: {value}"
            
            # Verzend het bericht via Telegram API
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=data) 
            
            if response.status_code == 200:
                logging.info(f"Telegram notificatie verzonden: {message}")
                return True
            else:
                logging.error(f"Fout bij verzenden Telegram notificatie: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"Fout bij verzenden Telegram notificatie: {e}")
            return False
    
    def test_notification(self):
        """Stuur een test notificatie."""
        return self.send_notification("Dit is een test notificatie van uw MrFix Automatisering tool.")

# Voorbeeld gebruik
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Gebruik: python telegram_notification.py <BOT_TOKEN> <CHAT_ID>")
        sys.exit(1)
    
    bot_token = sys.argv[1]
    chat_id = sys.argv[2]
    
    notifier = TelegramNotifier(bot_token, chat_id)
    success = notifier.test_notification()
    
    if success:
        print("Test notificatie succesvol verzonden!")
    else:
        print("Fout bij verzenden test notificatie. Controleer de logs voor details.")
