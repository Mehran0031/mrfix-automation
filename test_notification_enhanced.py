import unittest
import os
import sys
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Voeg de project directory toe aan het pad
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import de modules die we willen testen
try:
    from notification_enhanced import NotificationSystem, send_notification
except ImportError:
    print("Kon de notification_enhanced module niet importeren. Zorg ervoor dat je in de juiste directory bent.")
    sys.exit(1)

class TestNotificationEnhanced(unittest.TestCase):
    """Test cases voor het verbeterde notificatiesysteem."""
    
    def setUp(self):
        """Setup voor elke test."""
        # Maak een tijdelijke directory voor test data
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.test_dir, 'data')
        self.log_dir = os.path.join(self.test_dir, 'logs')
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Patch de constanten
        self.patcher1 = patch('notification_enhanced.DATA_DIR', self.data_dir)
        self.patcher2 = patch('notification_enhanced.LOG_DIR', self.log_dir)
        self.patcher3 = patch('notification_enhanced.PREFERENCES_FILE', os.path.join(self.data_dir, 'test_prefs.json'))
        self.patcher4 = patch('notification_enhanced.NOTIFICATION_CONFIG_FILE', os.path.join(self.data_dir, 'test_notification.json'))
        
        self.patcher1.start()
        self.patcher2.start()
        self.patcher3.start()
        self.patcher4.start()
        
        # Mock requests
        self.patcher5 = patch('notification_enhanced.requests')
        self.mock_requests = self.patcher5.start()
        
        # Mock response
        self.mock_response = MagicMock()
        self.mock_response.status_code = 200
        self.mock_requests.post.return_value = self.mock_response
        
        # Mock smtplib
        self.patcher6 = patch('notification_enhanced.smtplib')
        self.mock_smtplib = self.patcher6.start()
        
        # Mock SMTP server
        self.mock_smtp = MagicMock()
        self.mock_smtplib.SMTP.return_value = self.mock_smtp
        
        # Maak een test configuratiebestand
        self.config = {
            "notification_method": "telegram",
            "telegram": {
                "bot_token": "test_token",
                "chat_id": "test_chat_id"
            },
            "pushbullet": {
                "api_key": "test_api_key"
            },
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "test@gmail.com",
                "password": "test_password",
                "recipient": "recipient@example.com"
            },
            "pushover": {
                "api_token": "test_api_token",
                "user_key": "test_user_key"
            },
            "safari_web_push": {
                "vapid_private_key": "test_private_key",
                "vapid_public_key": "test_public_key",
                "subscription_info": {}
            },
            "permission_timeout": 10
        }
        
        with open(os.path.join(self.data_dir, 'test_notification.json'), 'w') as f:
            json.dump(self.config, f)
    
    def tearDown(self):
        """Cleanup na elke test."""
        self.patcher1.stop()
        self.patcher2.stop()
        self.patcher3.stop()
        self.patcher4.stop()
        self.patcher5.stop()
        self.patcher6.stop()
        
        # Verwijder de tijdelijke directory
        shutil.rmtree(self.test_dir)
    
    def test_init(self):
        """Test de initialisatie van het NotificationSystem."""
        notification = NotificationSystem()
        
        # Controleer of de configuratie correct is geladen
        self.assertEqual(notification.config["notification_method"], "telegram")
        self.assertEqual(notification.config["telegram"]["bot_token"], "test_token")
        self.assertEqual(notification.config["telegram"]["chat_id"], "test_chat_id")
        self.assertEqual(notification.config["email"]["username"], "test@gmail.com")
        self.assertEqual(notification.config["pushover"]["api_token"], "test_api_token")
    
    def test_send_telegram_notification(self):
        """Test het versturen van een Telegram notificatie."""
        notification = NotificationSystem()
        
        result = notification.send_telegram_notification("Test Titel", "Test Bericht")
        
        # Controleer of de juiste methode is aangeroepen
        self.mock_requests.post.assert_called_once()
        
        # Controleer de argumenten
        args, kwargs = self.mock_requests.post.call_args
        self.assertEqual(args[0], f"https://api.telegram.org/bot{self.config['telegram']['bot_token']}/sendMessage")
        self.assertEqual(kwargs['data']['chat_id'], self.config['telegram']['chat_id'])
        self.assertIn("Test Titel", kwargs['data']['text'])
        self.assertIn("Test Bericht", kwargs['data']['text'])
        
        # Controleer het resultaat
        self.assertTrue(result)
    
    def test_send_pushbullet_notification(self):
        """Test het versturen van een Pushbullet notificatie."""
        notification = NotificationSystem()
        notification.config["notification_method"] = "pushbullet"
        
        result = notification.send_pushbullet_notification("Test Titel", "Test Bericht")
        
        # Controleer of de juiste methode is aangeroepen
        self.mock_requests.post.assert_called_once()
        
        # Controleer de argumenten
        args, kwargs = self.mock_requests.post.call_args
        self.assertEqual(args[0], "https://api.pushbullet.com/v2/pushes")
        self.assertEqual(kwargs['headers']['Access-Token'], self.config['pushbullet']['api_key'])
        self.assertEqual(kwargs['json']['title'], "Test Titel")
        self.assertEqual(kwargs['json']['body'], "Test Bericht")
        
        # Controleer het resultaat
        self.assertTrue(result)
    
    def test_send_email_notification(self):
        """Test het versturen van een e-mail notificatie."""
        notification = NotificationSystem()
        notification.config["notification_method"] = "email"
        
        result = notification.send_email_notification("Test Titel", "Test Bericht")
        
        # Controleer of de juiste methodes zijn aangeroepen
        self.mock_smtplib.SMTP.assert_called_once_with(
            self.config['email']['smtp_server'], 
            self.config['email']['smtp_port']
        )
        self.mock_smtp.starttls.assert_called_once()
        self.mock_smtp.login.assert_called_once_with(
            self.config['email']['username'],
            self.config['email']['password']
        )
        self.mock_smtp.send_message.assert_called_once()
        self.mock_smtp.quit.assert_called_once()
        
        # Controleer het resultaat
        self.assertTrue(result)
    
    def test_send_pushover_notification(self):
        """Test het versturen van een Pushover notificatie."""
        notification = NotificationSystem()
        notification.config["notification_method"] = "pushover"
        
        result = notification.send_pushover_notification("Test Titel", "Test Bericht")
        
        # Controleer of de juiste methode is aangeroepen
        self.mock_requests.post.assert_called_once()
        
        # Controleer de argumenten
        args, kwargs = self.mock_requests.post.call_args
        self.assertEqual(args[0], "https://api.pushover.net/1/messages.json")
        self.assertEqual(kwargs['data']['token'], self.config['pushover']['api_token'])
        self.assertEqual(kwargs['data']['user'], self.config['pushover']['user_key'])
        self.assertEqual(kwargs['data']['title'], "Test Titel")
        self.assertEqual(kwargs['data']['message'], "Test Bericht")
        
        # Controleer het resultaat
        self.assertTrue(result)
    
    def test_send_safari_web_push_notification(self):
        """Test het versturen van een Safari Web Push notificatie."""
        notification = NotificationSystem()
        notification.config["notification_method"] = "safari_web_push"
        
        result = notification.send_safari_web_push_notification("Test Titel", "Test Bericht")
        
        # Safari Web Push is een vereenvoudigde implementatie die alleen logt
        # Controleer het resultaat
        self.assertTrue(result)
    
    def test_send_notification(self):
        """Test de algemene send_notification functie."""
        # Test voor elke notificatiemethode
        methods = ["telegram", "pushbullet", "email", "pushover", "safari_web_push"]
        
        for method in methods:
            # Patch de specifieke send_*_notification methode
            method_name = f"send_{method}_notification"
            with patch.object(NotificationSystem, method_name, return_value=True) as mock_method:
                notification = NotificationSystem()
                notification.config["notification_method"] = method
                
                result = notification.send_notification("Test Titel", "Test Bericht")
                
                # Controleer of de juiste methode is aangeroepen
                mock_method.assert_called_once_with("Test Titel", "Test Bericht")
                
                # Controleer het resultaat
                self.assertTrue(result)
    
    def test_request_permission(self):
        """Test het vragen van toestemming aan de gebruiker."""
        notification = NotificationSystem()
        
        # Mock de send_notification methode
        notification.send_notification = MagicMock(return_value=True)
        
        # Test job
        job = {
            'id': 'test-job',
            'title': 'Test Opdracht',
            'location': 'Utrecht',
            'distance_to_amsterdam': 40
        }
        
        result = notification.request_permission("Test Toestemming", job)
        
        # Controleer of de juiste methode is aangeroepen
        notification.send_notification.assert_called_once()
        
        # Controleer het resultaat (in de huidige implementatie altijd True)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
