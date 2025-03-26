import os
import unittest
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Voeg de project directory toe aan het pad
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import de modules die we willen testen
try:
    from website_monitor import MrFixMonitor
    from job_filter import JobFilter, filter_and_process_jobs
    from calendar_integration import GoogleCalendarIntegration, check_calendar_availability
    from notification import NotificationSystem, send_notification
    from gui import MrFixPreferencesGUI
except ImportError:
    print("Kon de modules niet importeren. Zorg ervoor dat je in de juiste directory bent.")
    sys.exit(1)

class TestWebsiteMonitor(unittest.TestCase):
    """Test cases voor de website monitoring component."""
    
    def setUp(self):
        """Setup voor elke test."""
        # Maak een tijdelijke directory voor test data
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.test_dir, 'data')
        self.log_dir = os.path.join(self.test_dir, 'logs')
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Mock de database en webdriver
        self.patcher1 = patch('website_monitor.sqlite3')
        self.patcher2 = patch('website_monitor.webdriver')
        self.mock_sqlite = self.patcher1.start()
        self.mock_webdriver = self.patcher2.start()
        
        # Mock de database connectie en cursor
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_sqlite.connect.return_value = self.mock_conn
        self.mock_conn.cursor.return_value = self.mock_cursor
        
        # Mock de webdriver
        self.mock_driver = MagicMock()
        self.mock_webdriver.Chrome.return_value = self.mock_driver
        
        # Patch de constanten
        self.patcher3 = patch('website_monitor.DATA_DIR', self.data_dir)
        self.patcher4 = patch('website_monitor.LOG_DIR', self.log_dir)
        self.patcher5 = patch('website_monitor.DB_PATH', os.path.join(self.data_dir, 'test.db'))
        self.patcher6 = patch('website_monitor.PREFERENCES_FILE', os.path.join(self.data_dir, 'test_prefs.json'))
        
        self.patcher3.start()
        self.patcher4.start()
        self.patcher5.start()
        self.patcher6.start()
    
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
        """Test de initialisatie van de MrFixMonitor."""
        monitor = MrFixMonitor()
        
        # Controleer of de database en webdriver correct zijn geïnitialiseerd
        self.mock_sqlite.connect.assert_called_once()
        self.mock_conn.cursor.assert_called_once()
        self.mock_webdriver.Chrome.assert_called_once()
        
        # Controleer of de tabellen zijn aangemaakt
        self.mock_cursor.execute.assert_called()
    
    @patch('website_monitor.BeautifulSoup')
    def test_extract_jobs(self, mock_bs):
        """Test het extraheren van opdrachten van de MrFix pagina."""
        # Mock de BeautifulSoup parser
        mock_soup = MagicMock()
        mock_bs.return_value = mock_soup
        
        # Mock de job elementen
        mock_job_elem1 = MagicMock()
        mock_job_elem2 = MagicMock()
        mock_soup.select.return_value = [mock_job_elem1, mock_job_elem2]
        
        # Mock de titel, beschrijving, locatie en datum elementen
        mock_title_elem = MagicMock()
        mock_title_elem.text = "IKEA kast monteren"
        mock_job_elem1.select_one.side_effect = lambda selector: {
            '.job-title, h3, h2': mock_title_elem,
            '.job-description, p, .description': MagicMock(text="Montage van een IKEA PAX kast"),
            '.job-location, span.location, .address': MagicMock(text="Amsterdam"),
            '.job-date, span.date, .posted-date': MagicMock(text="25 maart 2025"),
            'a[href*="accept"], a.btn, button.accept': MagicMock(attrs={'href': '/accept/123'})
        }.get(selector, None)
        
        mock_job_elem2.select_one.side_effect = lambda selector: {
            '.job-title, h3, h2': MagicMock(text="Elektra aanleggen"),
            '.job-description, p, .description': MagicMock(text="Elektra werkzaamheden voor nieuwe keuken, €90 per uur"),
            '.job-location, span.location, .address': MagicMock(text="Utrecht"),
            '.job-date, span.date, .posted-date': MagicMock(text="25 maart 2025"),
            'a[href*="accept"], a.btn, button.accept': MagicMock(attrs={'href': '/accept/456'})
        }.get(selector, None)
        
        # Mock de driver
        self.mock_driver.current_url = "https://klussenvoormij.mrfix.nl/3900"
        self.mock_driver.page_source = "<html></html>"
        
        # Maak een monitor instantie
        monitor = MrFixMonitor()
        
        # Mock de extract_timeslots methode
        monitor.extract_timeslots = MagicMock(return_value=["2025-03-25 18:00", "2025-03-25 19:00"])
        
        # Roep de extract_jobs methode aan
        jobs = monitor.extract_jobs()
        
        # Controleer de resultaten
        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs[0]['title'], "IKEA kast monteren")
        self.assertEqual(jobs[0]['location'], "Amsterdam")
        self.assertEqual(jobs[0]['is_ikea'], True)
        self.assertEqual(jobs[0]['is_amsterdam'], True)
        
        self.assertEqual(jobs[1]['title'], "Elektra aanleggen")
        self.assertEqual(jobs[1]['location'], "Utrecht")
        self.assertEqual(jobs[1]['is_electrical'], True)
        self.assertEqual(jobs[1]['hourly_rate'], 90)
        self.assertEqual(jobs[1]['is_amsterdam'], False)
        self.assertGreater(jobs[1]['distance_to_amsterdam'], 0)

class TestJobFilter(unittest.TestCase):
    """Test cases voor de opdracht filtering component."""
    
    def setUp(self):
        """Setup voor elke test."""
        # Maak een tijdelijke directory voor test data
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.test_dir, 'data')
        self.log_dir = os.path.join(self.test_dir, 'logs')
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Mock de database
        self.patcher1 = patch('job_filter.sqlite3')
        self.mock_sqlite = self.patcher1.start()
        
        # Mock de database connectie en cursor
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_sqlite.connect.return_value = self.mock_conn
        self.mock_conn.cursor.return_value = self.mock_cursor
        
        # Patch de constanten
        self.patcher2 = patch('job_filter.DATA_DIR', self.data_dir)
        self.patcher3 = patch('job_filter.LOG_DIR', self.log_dir)
        self.patcher4 = patch('job_filter.DB_PATH', os.path.join(self.data_dir, 'test.db'))
        self.patcher5 = patch('job_filter.PREFERENCES_FILE', os.path.join(self.data_dir, 'test_prefs.json'))
        
        self.patcher2.start()
        self.patcher3.start()
        self.patcher4.start()
        self.patcher5.start()
        
        # Mock de calendar_integration en notification modules
        self.patcher6 = patch('job_filter.check_calendar_availability')
        self.patcher7 = patch('job_filter.add_event_to_calendar')
        self.patcher8 = patch('job_filter.send_notification')
        self.patcher9 = patch('job_filter.request_permission')
        
        self.mock_check_calendar = self.patcher6.start()
        self.mock_add_event = self.patcher7.start()
        self.mock_send_notification = self.patcher8.start()
        self.mock_request_permission = self.patcher9.start()
        
        # Standaard return values
        self.mock_check_calendar.return_value = {"available": True, "suggested_time": datetime.now()}
        self.mock_add_event.return_value = True
        self.mock_send_notification.return_value = True
        self.mock_request_permission.return_value = True
        
        # Test data
        self.test_jobs = [
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
                    '2025-03-25 20:00'
                ]
            },
            {
                'id': 'test-electrical-job-utrecht',
                'title': 'Elektra aanleggen',
                'description': 'Elektra werkzaamheden voor nieuwe keuken, €90 per uur',
                'location': 'Utrecht',
                'date_posted': '25 maart 2025',
                'accept_link': 'https://klussenvoormij.mrfix.nl/accept/456',
                'is_ikea': False,
                'is_electrical': True,
                'is_internet': False,
                'hourly_rate': 90,
                'is_urgent': False,
                'is_amsterdam': False,
                'distance_to_amsterdam': 40,
                'available_timeslots': [
                    '2025-03-25 21:00',
                    '2025-03-25 22:00'
                ]
            }
        ]
    
    def tearDown(self):
        """Cleanup na elke test."""
        self.patcher1.stop()
        self.patcher2.stop()
        self.patcher3.stop()
        self.patcher4.stop()
        self.patcher5.stop()
        self.patcher6.stop()
        self.patcher7.stop()
        self.patcher8.stop()
        self.patcher9.stop()
        
        # Verwijder de tijdelijke directory
        shutil.rmtree(self.test_dir)
    
    def test_init(self):
        """Test de initialisatie van de JobFilter."""
        job_filter = JobFilter()
        
        # Controleer of de database correct is geïnitialiseerd
        self.mock_sqlite.connect.assert_called_once()
        self.mock_conn.cursor.assert_called_once()
    
    def test_calculate_priority_score(self):
        """Test het berekenen van de prioriteitsscore voor opdrachten."""
        job_filter = JobFilter()
        
        # Test de score voor een IKEA opdracht in Amsterdam
        score1 = job_filter.calculate_priority_score(self.test_jobs[0])
        
        # Test de score voor een elektra opdracht in Utrecht
        score2 = job_filter.calculate_priority_score(self.test_jobs[1])
        
        # De Amsterdam opdracht zou een hogere score moeten hebben
        self.assertGreater(score1, score2)
    
    def test_meets_basic_criteria(self):
        """Test of opdrachten voldoen aan de basisvoorwaarden."""
        job_filter = JobFilter()
        
        # Test een IKEA opdracht met goed uurloon
        self.assertTrue(job_filter.meets_basic_criteria(self.test_jobs[0]))
        
        # Test een elektra opdracht met goed uurloon
        self.assertTrue(job_filter.meets_basic_criteria(self.test_jobs[1]))
        
        # Test een opdracht die niet aan de voorwaarden voldoet
        bad_job = self.test_jobs[0].copy()
        bad_job['is_ikea'] = False
        bad_job['is_electrical'] = False
        bad_job['is_internet'] = False
        bad_job['hourly_rate'] = 50
        bad_job['is_urgent'] = False
        
        self.assertFalse(job_filter.meets_basic_criteria(bad_job))
    
    def test_select_best_timeslot(self):
        """Test het selecteren van het beste tijdslot."""
        job_filter = JobFilter()
        
        # Mock de parse_timeslot methode
        job_filter.parse_timeslot = lambda ts: datetime.strptime(ts, '%Y-%m-%d %H:%M')
        
        # Mock de count_jobs_on_date methode
        job_filter.count_jobs_on_date = MagicMock(return_value=0)
        
        # Test met een opdracht met meerdere tijdslots
        best_slot = job_filter.select_best_timeslot(self.test_jobs[0])
        
        # Het eerste beschikbare tijdslot zou moeten worden geselecteerd
        self.assertEqual(best_slot, '2025-03-25 18:00')
    
    def test_filter_and_process_jobs(self):
        """Test het filteren en verwerken van opdrachten."""
        # Mock de JobFilter.filter_and_process_jobs methode
        with patch('job_filter.JobFilter.filter_and_process_jobs') as mock_filter:
            # Roep de functie aan
            filter_and_process_jobs(self.test_jobs)
            
            # Controleer of de methode is aangeroepen met de juiste argumenten
            mock_filter.assert_called_once_with(self.test_jobs)

class TestCalendarIntegration(unittest.TestCase):
    """Test cases voor de Google Calendar integratie component."""
    
    def setUp(self):
        """Setup voor elke test."""
        # Maak een tijdelijke directory voor test data
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.test_dir, 'data')
        self.log_dir = os.path.join(self.test_dir, 'logs')
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Patch de constanten
        self.patcher1 = patch('calendar_integration.DATA_DIR', self.data_dir)
        self.patcher2 = patch('calendar_integration.LOG_DIR', self.log_dir)
        self.patcher3 = patch('calendar_integration.PREFERENCES_FILE', os.path.join(self.data_dir, 'test_prefs.json'))
        self.patcher4 = patch('calendar_integration.CREDENTIALS_FILE', os.path.join(self.data_dir, 'test_creds.json'))
        self.patcher5 = patch('calendar_integration.TOKEN_FILE', os.path.join(self.data_dir, 'test_token.pickle'))
        
        self.patcher1.start()
        self.patcher2.start()
        self.patcher3.start()
        self.patcher4.start()
        self.patcher5.start()
        
        # Mock de Google API
        self.patcher6 = patch('calendar_integration.build')
        self.mock_build = self.patcher6.start()
        
        # Mock de service
        self.mock_service = MagicMock()
        self.mock_build.return_value = self.mock_service
        
        # Mock de events methode
        self.mock_events = MagicMock()
        self.mock_service.events.return_value = self.mock_events
        
        # Mock de list methode
        self.mock_list = MagicMock()
        self.mock_events.list.return_value = self.mock_list
        
        # Mock de execute methode
        self.mock_execute = MagicMock()
        self.mock_list.execute.return_value = {'items': []}
        
        # Mock de insert methode
        self.mock_insert = MagicMock()
        self.mock_events.insert.return_value = self.mock_insert
        self.mock_insert.execute.return_value = {'htmlLink': 'https://calendar.google.com/event?id=123'}
    
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
    
    @patch('calendar_integration.pickle')
    @patch('calendar_integration.InstalledAppFlow')
    @patch('calendar_integration.Request')
    @patch('os.path.exists')
    def test_get_calendar_service(self, mock_exists, mock_request, mock_flow, mock_pickle):
        """Test het verkrijgen van de Google Calendar service."""
        # Mock os.path.exists
        mock_exists.side_effect = lambda path: path == os.path.join(self.data_dir, 'test_creds.json')
        
        # Mock InstalledAppFlow
        mock_flow_instance = MagicMock()
        mock_flow.from_client_secrets_file.return_value = mock_flow_instance
        mock_flow_instance.run_local_server.return_value = MagicMock()
        
        # Maak een GoogleCalendarIntegration instantie
        calendar = GoogleCalendarIntegration()
        
        # Controleer of de service correct is geïnitialiseerd
        self.mock_build.assert_called_once_with('calendar', 'v3', credentials=mock_flow_instance.run_local_server.return_value)
        self.assertEqual(calendar.service, self.mock_service)
    
    def test_check_calendar_availability(self):
        """Test het controleren van beschikbaarheid in de agenda."""
        # Maak een GoogleCalendarIntegration instantie
        calendar = GoogleCalendarIntegration()
        
        # Test met een tijd die beschikbaar is
        start_time = datetime.now() + timedelta(hours=1)
        duration = 60  # minuten
        
        availability = calendar.check_calendar_availability(start_time, duration)
        
        # Controleer of de juiste methodes zijn aangeroepen
        self.mock_events.list.assert_called_once()
        self.mock_list.execute.assert_called_once()
        
        # Controleer het resultaat
        self.assertTrue(availability['available'])
        self.assertEqual(availability['suggested_time'], start_time)
    
    def test_add_event_to_calendar(self):
        """Test het toevoegen van een evenement aan de agenda."""
        # Maak een GoogleCalendarIntegration instantie
        calendar = GoogleCalendarIntegration()
        
        # Test event details
        event_details = {
            'summary': 'Test Evenement',
            'location': 'Amsterdam',
            'description': 'Dit is een test',
            'start_time': datetime.now() + timedelta(hours=1),
            'end_time': datetime.now() + timedelta(hours=2)
        }
        
        result = calendar.add_event_to_calendar(event_details)
        
        # Controleer of de juiste methodes zijn aangeroepen
        self.mock_events.insert.assert_called_once()
        self.mock_insert.execute.assert_called_once()
        
        # Controleer het resultaat
        self.assertTrue(result)

class TestNotificationSystem(unittest.TestCase):
    """Test cases voor het notificatiesysteem."""
    
    def setUp(self):
        """Setup voor elke test."""
        # Maak een tijdelijke directory voor test data
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.test_dir, 'data')
        self.log_dir = os.path.join(self.test_dir, 'logs')
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Patch de constanten
        self.patcher1 = patch('notification.DATA_DIR', self.data_dir)
        self.patcher2 = patch('notification.LOG_DIR', self.log_dir)
        self.patcher3 = patch('notification.PREFERENCES_FILE', os.path.join(self.data_dir, 'test_prefs.json'))
        self.patcher4 = patch('notification.NOTIFICATION_CONFIG_FILE', os.path.join(self.data_dir, 'test_notification.json'))
        
        self.patcher1.start()
        self.patcher2.start()
        self.patcher3.start()
        self.patcher4.start()
        
        # Mock requests
        self.patcher5 = patch('notification.requests')
        self.mock_requests = self.patcher5.start()
        
        # Mock response
        self.mock_response = MagicMock()
        self.mock_response.status_code = 200
        self.mock_requests.post.return_value = self.mock_response
        
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
        
        # Verwijder de tijdelijke directory
        shutil.rmtree(self.test_dir)
    
    def test_init(self):
        """Test de initialisatie van het NotificationSystem."""
        notification = NotificationSystem()
        
        # Controleer of de configuratie correct is geladen
        self.assertEqual(notification.config["notification_method"], "telegram")
        self.assertEqual(notification.config["telegram"]["bot_token"], "test_token")
        self.assertEqual(notification.config["telegram"]["chat_id"], "test_chat_id")
    
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
        # Verander de notificatiemethode naar Pushbullet
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

class TestGUI(unittest.TestCase):
    """Test cases voor de GUI component."""
    
    def setUp(self):
        """Setup voor elke test."""
        # Maak een tijdelijke directory voor test data
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.test_dir, 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Patch tkinter
        self.patcher1 = patch('gui.tk')
        self.patcher2 = patch('gui.ttk')
        self.patcher3 = patch('gui.messagebox')
        
        self.mock_tk = self.patcher1.start()
        self.mock_ttk = self.patcher2.start()
        self.mock_messagebox = self.patcher3.start()
        
        # Mock root
        self.mock_root = MagicMock()
        
        # Patch os.path.dirname en os.path.join
        self.patcher4 = patch('gui.os.path.dirname', return_value=self.test_dir)
        self.patcher5 = patch('gui.os.path.join', side_effect=os.path.join)
        
        self.patcher4.start()
        self.patcher5.start()
        
        # Patch os.makedirs
        self.patcher6 = patch('gui.os.makedirs')
        self.mock_makedirs = self.patcher6.start()
    
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
    
    @patch('gui.open', new_callable=unittest.mock.mock_open, read_data='{}')
    @patch('gui.json.load', return_value={})
    def test_init(self, mock_json_load, mock_open):
        """Test de initialisatie van de MrFixPreferencesGUI."""
        gui = MrFixPreferencesGUI(self.mock_root)
        
        # Controleer of de root correct is ingesteld
        self.assertEqual(gui.root, self.mock_root)
        
        # Controleer of de data directory is aangemaakt
        self.mock_makedirs.assert_called_with(os.path.join(self.test_dir, 'data'), exist_ok=True)
        
        # Controleer of de voorkeuren zijn geladen
        mock_open.assert_called_with(os.path.join(self.test_dir, 'data', 'user_preferences.json'), 'r')
        mock_json_load.assert_called_once()
    
    @patch('gui.open', new_callable=unittest.mock.mock_open)
    @patch('gui.json.dump')
    def test_save_preferences(self, mock_json_dump, mock_open):
        """Test het opslaan van voorkeuren."""
        # Mock de load_preferences methode
        with patch.object(MrFixPreferencesGUI, 'load_preferences', return_value={}):
            # Mock de create_gui methode
            with patch.object(MrFixPreferencesGUI, 'create_gui'):
                gui = MrFixPreferencesGUI(self.mock_root)
                
                # Stel enkele voorkeuren in
                gui.preferences = {
                    "prefer_ikea": True,
                    "min_hourly_rate": 85
                }
                
                # Sla de voorkeuren op
                gui.save_preferences()
                
                # Controleer of het bestand correct is geopend
                mock_open.assert_called_with(os.path.join(self.test_dir, 'data', 'user_preferences.json'), 'w')
                
                # Controleer of json.dump is aangeroepen met de juiste argumenten
                mock_json_dump.assert_called_once()
                args, kwargs = mock_json_dump.call_args
                self.assertEqual(args[0], gui.preferences)
                self.assertEqual(kwargs['indent'], 4)
                
                # Controleer of messagebox.showinfo is aangeroepen
                self.mock_messagebox.showinfo.assert_called_once()

if __name__ == '__main__':
    unittest.main()
