import os
import json
import logging
import tkinter as tk
from tkinter import ttk, messagebox, StringVar, IntVar, BooleanVar, Frame, LabelFrame

# Configuratie
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_PATH = os.path.join(LOG_DIR, 'gui.log')
PREFERENCES_FILE = os.path.join(DATA_DIR, 'user_preferences.json')

# Zorg ervoor dat de data directory bestaat
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Logging configuratie
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class MrFixPreferencesGUI:
    def __init__(self, root):
        """Initialiseer de GUI voor voorkeuren."""
        self.root = root
        
        # Laad voorkeuren
        self.load_preferences()
        
        # Maak de GUI
        self.create_gui()
        
        logging.info("Voorkeuren GUI geïnitialiseerd")

    def load_preferences(self):
        """Laad gebruikersvoorkeuren uit het configuratiebestand."""
        # Standaard voorkeuren
        self.preferences = {
            # Opdrachttypes voorkeuren
            "prefer_ikea": True,
            "prefer_electrical": True,
            "prefer_internet": True,
            "prefer_urgent": True,
            
            # Uurloon instellingen
            "min_hourly_rate": 79,
            
            # Planningsvoorkeuren per dag
            "max_jobs_monday": 5,
            "max_jobs_tuesday": 2,
            "max_jobs_wednesday": 5,
            "max_jobs_thursday": 2,
            "max_jobs_friday": 2,
            "max_jobs_saturday": 3,
            "max_jobs_sunday": 3,
            
            # Locatievoorkeuren
            "prefer_amsterdam": True,
            "max_distance_without_permission": 20,
            "travel_time_between_jobs": 60,
            
            # Monitoring instellingen
            "monitoring_interval": 300,  # 5 minuten in seconden
            "auto_accept": True,
            
            # Notificatie-instellingen
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
            "notify_new_jobs": True,
            "notify_accepted_jobs": True,
            
            # Google Agenda instellingen
            "calendar_id": "primary",
            "auto_schedule": True
        }
        
        try:
            if os.path.exists(PREFERENCES_FILE):
                with open(PREFERENCES_FILE, 'r') as f:
                    loaded_prefs = json.load(f)
                    # Update alleen de voorkeuren die in het bestand staan
                    for key, value in loaded_prefs.items():
                        if key in self.preferences:
                            self.preferences[key] = value
                    
                    logging.info(f"Voorkeuren geladen uit {PREFERENCES_FILE}")
            else:
                logging.warning(f"Voorkeuren bestand niet gevonden: {PREFERENCES_FILE}, standaardwaarden worden gebruikt")
        except Exception as e:
            logging.error(f"Fout bij laden van voorkeuren: {e}")

    def save_preferences(self):
        """Sla gebruikersvoorkeuren op in het configuratiebestand."""
        try:
            # Update de voorkeuren met de huidige waarden uit de GUI
            self.update_preferences_from_gui()
            
            with open(PREFERENCES_FILE, 'w') as f:
                json.dump(self.preferences, f, indent=4)
            
            logging.info(f"Voorkeuren opgeslagen in {PREFERENCES_FILE}")
            messagebox.showinfo("Voorkeuren opgeslagen", "Uw voorkeuren zijn succesvol opgeslagen.")
        except Exception as e:
            logging.error(f"Fout bij opslaan van voorkeuren: {e}")
            messagebox.showerror("Fout", f"Fout bij opslaan van voorkeuren: {e}")

    def update_preferences_from_gui(self):
        """Update de voorkeuren met de huidige waarden uit de GUI."""
        # Opdrachttypes voorkeuren
        self.preferences["prefer_ikea"] = self.prefer_ikea_var.get()
        self.preferences["prefer_electrical"] = self.prefer_electrical_var.get()
        self.preferences["prefer_internet"] = self.prefer_internet_var.get()
        self.preferences["prefer_urgent"] = self.prefer_urgent_var.get()
        
        # Uurloon instellingen
        self.preferences["min_hourly_rate"] = self.min_hourly_rate_var.get()
        
        # Planningsvoorkeuren per dag
        self.preferences["max_jobs_monday"] = self.max_jobs_monday_var.get()
        self.preferences["max_jobs_tuesday"] = self.max_jobs_tuesday_var.get()
        self.preferences["max_jobs_wednesday"] = self.max_jobs_wednesday_var.get()
        self.preferences["max_jobs_thursday"] = self.max_jobs_thursday_var.get()
        self.preferences["max_jobs_friday"] = self.max_jobs_friday_var.get()
        self.preferences["max_jobs_saturday"] = self.max_jobs_saturday_var.get()
        self.preferences["max_jobs_sunday"] = self.max_jobs_sunday_var.get()
        
        # Locatievoorkeuren
        self.preferences["prefer_amsterdam"] = self.prefer_amsterdam_var.get()
        self.preferences["max_distance_without_permission"] = self.max_distance_var.get()
        self.preferences["travel_time_between_jobs"] = self.travel_time_var.get()
        
        # Monitoring instellingen
        self.preferences["monitoring_interval"] = self.monitoring_interval_var.get() * 60  # Omzetten van minuten naar seconden
        self.preferences["auto_accept"] = self.auto_accept_var.get()
        
        # Notificatie-instellingen
        self.preferences["notification_method"] = self.notification_method_var.get()
        
        # Telegram instellingen
        self.preferences["telegram"]["bot_token"] = self.telegram_bot_token_var.get()
        self.preferences["telegram"]["chat_id"] = self.telegram_chat_id_var.get()
        
        # Pushbullet instellingen
        self.preferences["pushbullet"]["api_key"] = self.pushbullet_api_key_var.get()
        
        # Email instellingen
        self.preferences["email"]["username"] = self.email_username_var.get()
        self.preferences["email"]["password"] = self.email_password_var.get()
        self.preferences["email"]["recipient"] = self.email_recipient_var.get()
        
        # Pushover instellingen
        self.preferences["pushover"]["api_token"] = self.pushover_api_token_var.get()
        self.preferences["pushover"]["user_key"] = self.pushover_user_key_var.get()
        
        # Safari Web Push instellingen
        # Deze worden meestal automatisch ingesteld via de browser
        
        self.preferences["notify_new_jobs"] = self.notify_new_jobs_var.get()
        self.preferences["notify_accepted_jobs"] = self.notify_accepted_jobs_var.get()
        
        # Google Agenda instellingen
        self.preferences["calendar_id"] = self.calendar_id_var.get()
        self.preferences["auto_schedule"] = self.auto_schedule_var.get()

    def create_gui(self):
        """Maak de GUI voor voorkeuren."""
        # Maak een frame met padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Maak een notebook (tabbed interface) voor de verschillende categorieën
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Maak tabs voor verschillende categorieën
        jobs_frame = ttk.Frame(notebook, padding="10")
        planning_frame = ttk.Frame(notebook, padding="10")
        location_frame = ttk.Frame(notebook, padding="10")
        notification_frame = ttk.Frame(notebook, padding="10")
        calendar_frame = ttk.Frame(notebook, padding="10")
        
        notebook.add(jobs_frame, text="Opdrachten")
        notebook.add(planning_frame, text="Planning")
        notebook.add(location_frame, text="Locatie")
        notebook.add(notification_frame, text="Notificaties")
        notebook.add(calendar_frame, text="Agenda")
        
        # Vul de tabs
        self.create_jobs_tab(jobs_frame)
        self.create_planning_tab(planning_frame)
        self.create_location_tab(location_frame)
        self.create_notification_tab(notification_frame)
        self.create_calendar_tab(calendar_frame)
        
        # Knoppen onderaan
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        save_button = ttk.Button(button_frame, text="Opslaan", command=self.save_preferences)
        save_button.pack(side=tk.RIGHT, padx=5)
        
        reset_button = ttk.Button(button_frame, text="Standaardwaarden", command=self.reset_to_defaults)
        reset_button.pack(side=tk.RIGHT, padx=5)

    def create_jobs_tab(self, parent):
        """Maak de tab voor opdrachttypes voorkeuren."""
        # Opdrachttypes voorkeuren
        job_types_frame = ttk.LabelFrame(parent, text="Opdrachttypes voorkeuren")
        job_types_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Maak variabelen voor de checkbuttons
        self.prefer_ikea_var = BooleanVar(value=self.preferences["prefer_ikea"])
        self.prefer_electrical_var = BooleanVar(value=self.preferences["prefer_electrical"])
        self.prefer_internet_var = BooleanVar(value=self.preferences["prefer_internet"])
        self.prefer_urgent_var = BooleanVar(value=self.preferences["prefer_urgent"])
        
        # Maak de checkbuttons
        ttk.Checkbutton(job_types_frame, text="IKEA-gerelateerde opdrachten", variable=self.prefer_ikea_var).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Checkbutton(job_types_frame, text="Elektriciteitsklussen", variable=self.prefer_electrical_var).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Checkbutton(job_types_frame, text="Internet-gerelateerde opdrachten", variable=self.prefer_internet_var).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Checkbutton(job_types_frame, text="Urgente opdrachten", variable=self.prefer_urgent_var).grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Uurloon instellingen
        hourly_rate_frame = ttk.LabelFrame(parent, text="Uurloon instellingen")
        hourly_rate_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Maak variabele voor de slider
        self.min_hourly_rate_var = IntVar(value=self.preferences["min_hourly_rate"])
        
        # Maak de slider
        ttk.Label(hourly_rate_frame, text="Minimum uurloon (€):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        hourly_rate_slider = ttk.Scale(hourly_rate_frame, from_=50, to=150, variable=self.min_hourly_rate_var, orient=tk.HORIZONTAL, length=200)
        hourly_rate_slider.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Label om de huidige waarde te tonen
        hourly_rate_label = ttk.Label(hourly_rate_frame, textvariable=self.min_hourly_rate_var)
        hourly_rate_label.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Monitoring instellingen
        monitoring_frame = ttk.LabelFrame(parent, text="Monitoring instellingen")
        monitoring_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Maak variabelen
        self.monitoring_interval_var = IntVar(value=self.preferences["monitoring_interval"] // 60)  # Omzetten van seconden naar minuten
        self.auto_accept_var = BooleanVar(value=self.preferences["auto_accept"])
        
        # Maak de widgets
        ttk.Label(monitoring_frame, text="Controle-interval (minuten):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        interval_slider = ttk.Scale(monitoring_frame, from_=1, to=60, variable=self.monitoring_interval_var, orient=tk.HORIZONTAL, length=200)
        interval_slider.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Label om de huidige waarde te tonen
        interval_label = ttk.Label(monitoring_frame, textvariable=self.monitoring_interval_var)
        interval_label.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        
        ttk.Checkbutton(monitoring_frame, text="Automatisch accepteren", variable=self.auto_accept_var).grid(row=1, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)

    def create_planning_tab(self, parent):
        """Maak de tab voor planningsvoorkeuren."""
        # Planningsvoorkeuren per dag
        planning_frame = ttk.LabelFrame(parent, text="Maximum aantal opdrachten per dag")
        planning_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Maak variabelen voor de spinboxes
        self.max_jobs_monday_var = IntVar(value=self.preferences["max_jobs_monday"])
        self.max_jobs_tuesday_var = IntVar(value=self.preferences["max_jobs_tuesday"])
        self.max_jobs_wednesday_var = IntVar(value=self.preferences["max_jobs_wednesday"])
        self.max_jobs_thursday_var = IntVar(value=self.preferences["max_jobs_thursday"])
        self.max_jobs_friday_var = IntVar(value=self.preferences["max_jobs_friday"])
        self.max_jobs_saturday_var = IntVar(value=self.preferences["max_jobs_saturday"])
        self.max_jobs_sunday_var = IntVar(value=self.preferences["max_jobs_sunday"])
        
        # Maak de labels en spinboxes
        ttk.Label(planning_frame, text="Maandag:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(planning_frame, from_=0, to=10, textvariable=self.max_jobs_monday_var, width=5).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(planning_frame, text="Dinsdag:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(planning_frame, from_=0, to=10, textvariable=self.max_jobs_tuesday_var, width=5).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(planning_frame, text="Woensdag:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(planning_frame, from_=0, to=10, textvariable=self.max_jobs_wednesday_var, width=5).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(planning_frame, text="Donderdag:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(planning_frame, from_=0, to=10, textvariable=self.max_jobs_thursday_var, width=5).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(planning_frame, text="Vrijdag:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(planning_frame, from_=0, to=10, textvariable=self.max_jobs_friday_var, width=5).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(planning_frame, text="Zaterdag:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(planning_frame, from_=0, to=10, textvariable=self.max_jobs_saturday_var, width=5).grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(planning_frame, text="Zondag:").grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(planning_frame, from_=0, to=10, textvariable=self.max_jobs_sunday_var, width=5).grid(row=6, column=1, sticky=tk.W, padx=5, pady=5)

    def create_location_tab(self, parent):
        """Maak de tab voor locatievoorkeuren."""
        # Locatievoorkeuren
        location_frame = ttk.LabelFrame(parent, text="Locatievoorkeuren")
        location_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Maak variabelen
        self.prefer_amsterdam_var = BooleanVar(value=self.preferences["prefer_amsterdam"])
        self.max_distance_var = IntVar(value=self.preferences["max_distance_without_permission"])
        self.travel_time_var = IntVar(value=self.preferences["travel_time_between_jobs"])
        
        # Maak de widgets
        ttk.Checkbutton(location_frame, text="Voorrang voor Amsterdam", variable=self.prefer_amsterdam_var).grid(row=0, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(location_frame, text="Maximale afstand (km) zonder toestemming:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        distance_slider = ttk.Scale(location_frame, from_=0, to=100, variable=self.max_distance_var, orient=tk.HORIZONTAL, length=200)
        distance_slider.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Label om de huidige waarde te tonen
        distance_label = ttk.Label(location_frame, textvariable=self.max_distance_var)
        distance_label.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(location_frame, text="Reistijd tussen opdrachten (minuten):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        travel_time_slider = ttk.Scale(location_frame, from_=15, to=120, variable=self.travel_time_var, orient=tk.HORIZONTAL, length=200)
        travel_time_slider.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Label om de huidige waarde te tonen
        travel_time_label = ttk.Label(location_frame, textvariable=self.travel_time_var)
        travel_time_label.grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)

    def create_notification_tab(self, parent):
        """Maak de tab voor notificatie-instellingen."""
        # Notificatiemethode
        method_frame = ttk.LabelFrame(parent, text="Notificatiemethode")
        method_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Maak variabele voor de radiobuttons
        self.notification_method_var = StringVar(value=self.preferences["notification_method"])
        
        # Maak de radiobuttons
        ttk.Radiobutton(method_frame, text="Telegram", variable=self.notification_method_var, value="telegram", command=self.toggle_notification_settings).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(method_frame, text="Pushbullet", variable=self.notification_method_var, value="pushbullet", command=self.toggle_notification_settings).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(method_frame, text="E-mail", variable=self.notification_method_var, value="email", command=self.toggle_notification_settings).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(method_frame, text="Pushover (iOS)", variable=self.notification_method_var, value="pushover", command=self.toggle_notification_settings).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(method_frame, text="Safari Web Push", variable=self.notification_method_var, value="safari_web_push", command=self.toggle_notification_settings).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Telegram instellingen
        self.telegram_frame = ttk.LabelFrame(parent, text="Telegram instellingen")
        self.telegram_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Maak variabelen
        self.telegram_bot_token_var = StringVar(value=self.preferences["telegram"]["bot_token"])
        self.telegram_chat_id_var = StringVar(value=self.preferences["telegram"]["chat_id"])
        
        # Maak de widgets
        ttk.Label(self.telegram_frame, text="Bot token:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(self.telegram_frame, textvariable=self.telegram_bot_token_var, width=40).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(self.telegram_frame, text="Chat ID:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(self.telegram_frame, textvariable=self.telegram_chat_id_var, width=40).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Pushbullet instellingen
        self.pushbullet_frame = ttk.LabelFrame(parent, text="Pushbullet instellingen")
        self.pushbullet_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Maak variabele
        self.pushbullet_api_key_var = StringVar(value=self.preferences["pushbullet"]["api_key"])
        
        # Maak de widget
        ttk.Label(self.pushbullet_frame, text="API key:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(self.pushbullet_frame, textvariable=self.pushbullet_api_key_var, width=40).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Email instellingen
        self.email_frame = ttk.LabelFrame(parent, text="E-mail instellingen")
        self.email_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Maak variabelen
        self.email_username_var = StringVar(value=self.preferences["email"]["username"])
        self.email_password_var = StringVar(value=self.preferences["email"]["password"])
        self.email_recipient_var = StringVar(value=self.preferences["email"]["recipient"])
        
        # Maak de widgets
        ttk.Label(self.email_frame, text="Gmail gebruikersnaam:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(self.email_frame, textvariable=self.email_username_var, width=40).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(self.email_frame, text="App-wachtwoord:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(self.email_frame, textvariable=self.email_password_var, width=40, show="*").grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(self.email_frame, text="Ontvanger e-mail:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(self.email_frame, textvariable=self.email_recipient_var, width=40).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Pushover instellingen
        self.pushover_frame = ttk.LabelFrame(parent, text="Pushover instellingen")
        self.pushover_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Maak variabelen
        self.pushover_api_token_var = StringVar(value=self.preferences["pushover"]["api_token"])
        self.pushover_user_key_var = StringVar(value=self.preferences["pushover"]["user_key"])
        
        # Maak de widgets
        ttk.Label(self.pushover_frame, text="API token:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(self.pushover_frame, textvariable=self.pushover_api_token_var, width=40).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(self.pushover_frame, text="User key:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(self.pushover_frame, textvariable=self.pushover_user_key_var, width=40).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Safari Web Push instellingen
        self.safari_web_push_frame = ttk.LabelFrame(parent, text="Safari Web Push instellingen")
        self.safari_web_push_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Maak de widgets
        ttk.Label(self.safari_web_push_frame, text="Safari Web Push vereist een webserver en client-side JavaScript.").grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        ttk.Label(self.safari_web_push_frame, text="Zie de documentatie voor instructies over het opzetten van Safari Web Push.").grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Algemene notificatie-instellingen
        general_notification_frame = ttk.LabelFrame(parent, text="Algemene notificatie-instellingen")
        general_notification_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Maak variabelen
        self.notify_new_jobs_var = BooleanVar(value=self.preferences["notify_new_jobs"])
        self.notify_accepted_jobs_var = BooleanVar(value=self.preferences["notify_accepted_jobs"])
        
        # Maak de widgets
        ttk.Checkbutton(general_notification_frame, text="Notificaties voor nieuwe opdrachten", variable=self.notify_new_jobs_var).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Checkbutton(general_notification_frame, text="Notificaties voor geaccepteerde opdrachten", variable=self.notify_accepted_jobs_var).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Toon alleen de relevante instellingen
        self.toggle_notification_settings()

    def toggle_notification_settings(self):
        """Toon alleen de relevante notificatie-instellingen."""
        method = self.notification_method_var.get()
        
        # Verberg alle frames
        self.telegram_frame.pack_forget()
        self.pushbullet_frame.pack_forget()
        self.email_frame.pack_forget()
        self.pushover_frame.pack_forget()
        self.safari_web_push_frame.pack_forget()
        
        # Toon alleen de relevante frame
        if method == "telegram":
            self.telegram_frame.pack(fill=tk.X, padx=5, pady=5, after=self.telegram_frame.master.children["!labelframe"])
        elif method == "pushbullet":
            self.pushbullet_frame.pack(fill=tk.X, padx=5, pady=5, after=self.telegram_frame.master.children["!labelframe"])
        elif method == "email":
            self.email_frame.pack(fill=tk.X, padx=5, pady=5, after=self.telegram_frame.master.children["!labelframe"])
        elif method == "pushover":
            self.pushover_frame.pack(fill=tk.X, padx=5, pady=5, after=self.telegram_frame.master.children["!labelframe"])
        elif method == "safari_web_push":
            self.safari_web_push_frame.pack(fill=tk.X, padx=5, pady=5, after=self.telegram_frame.master.children["!labelframe"])

    def create_calendar_tab(self, parent):
        """Maak de tab voor Google Agenda instellingen."""
        # Google Agenda instellingen
        calendar_frame = ttk.LabelFrame(parent, text="Google Agenda instellingen")
        calendar_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Maak variabelen
        self.calendar_id_var = StringVar(value=self.preferences["calendar_id"])
        self.auto_schedule_var = BooleanVar(value=self.preferences["auto_schedule"])
        
        # Maak de widgets
        ttk.Label(calendar_frame, text="Agenda ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(calendar_frame, textvariable=self.calendar_id_var, width=40).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(calendar_frame, text="(Gebruik 'primary' voor uw hoofdagenda)").grid(row=1, column=1, sticky=tk.W, padx=5, pady=0)
        
        ttk.Checkbutton(calendar_frame, text="Automatisch inplannen", variable=self.auto_schedule_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Instructies
        instructions_frame = ttk.LabelFrame(parent, text="Google Agenda API instructies")
        instructions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        instructions_text = """
1. Ga naar de Google Cloud Console (https://console.cloud.google.com/)
2. Maak een nieuw project aan
3. Schakel de Google Calendar API in
4. Maak OAuth 2.0 credentials aan
5. Download het credentials.json bestand
6. Plaats het bestand in de 'data' map van deze applicatie
        """
        
        ttk.Label(instructions_frame, text=instructions_text, justify=tk.LEFT).pack(padx=5, pady=5)

    def reset_to_defaults(self):
        """Reset alle voorkeuren naar standaardwaarden."""
        if messagebox.askyesno("Reset voorkeuren", "Weet u zeker dat u alle voorkeuren wilt resetten naar standaardwaarden?"):
            # Verwijder het voorkeuren bestand
            if os.path.exists(PREFERENCES_FILE):
                try:
                    os.remove(PREFERENCES_FILE)
                    logging.info(f"Voorkeuren bestand verwijderd: {PREFERENCES_FILE}")
                except Exception as e:
                    logging.error(f"Fout bij verwijderen van voorkeuren bestand: {e}")
            
            # Herlaad de standaard voorkeuren
            self.load_preferences()
            
            # Herstart de GUI
            self.root.destroy()
            self.__init__(tk.Tk())
            
            messagebox.showinfo("Voorkeuren gereset", "Alle voorkeuren zijn gereset naar standaardwaarden.")

# Voor testen
if __name__ == "__main__":
    root = tk.Tk()
    root.title("MrFix Voorkeuren")
    root.geometry("800x600")
    app = MrFixPreferencesGUI(root)
    root.mainloop()
