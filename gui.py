import tkinter as tk
from tkinter import ttk, messagebox
import logging
import os
import json

class MrFixPreferencesGUI:
    def __init__(self, parent):
        self.parent = parent
        
        # Configuratie bestandspad
        self.config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        self.config_file = os.path.join(self.config_dir, 'user_preferences.json')
        
        # Zorg ervoor dat de data directory bestaat
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Laad bestaande voorkeuren of gebruik standaardwaarden
        self.preferences = self.load_preferences()
        
        # Maak de GUI
        self.create_gui()
    
    def load_preferences(self):
        """Laad voorkeuren uit het configuratiebestand of gebruik standaardwaarden."""
        default_preferences = {
            # Opdracht type voorkeuren
            "prefer_ikea": True,
            "prefer_electrical": True,
            "prefer_internet": True,
            "min_hourly_rate": 79,  # Minimum uurloon in euro
            "prefer_urgent": True,
            
            # Planning voorkeuren
            "max_jobs_weekday": {
                "0": 3,  # Zondag: max 3
                "1": 5,  # Maandag: meer opdrachten
                "2": 2,  # Dinsdag: max 2
                "3": 5,  # Woensdag: meer opdrachten
                "4": 2,  # Donderdag: max 2
                "5": 2,  # Vrijdag: max 2
                "6": 3,  # Zaterdag: max 3
            },
            
            # Locatie voorkeuren
            "prefer_amsterdam": True,
            "max_distance_without_permission": 20,  # km
            "travel_time_between_jobs": 60,  # minuten
            
            # Notificatie voorkeuren
            "notification_method": "telegram",  # 'telegram' of 'pushbullet'
            "telegram": {
                "bot_token": "",
                "chat_id": ""
            },
            "pushbullet": {
                "api_key": ""
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    preferences = json.load(f)
                    # Zorg ervoor dat alle standaardwaarden aanwezig zijn
                    for key, value in default_preferences.items():
                        if key not in preferences:
                            preferences[key] = value
                        elif key == "max_jobs_weekday" and isinstance(value, dict):
                            for day, max_jobs in value.items():
                                if day not in preferences[key]:
                                    preferences[key][day] = max_jobs
                return preferences
            else:
                return default_preferences
        except Exception as e:
            messagebox.showerror("Fout", f"Fout bij laden van voorkeuren: {e}")
            return default_preferences
    
    def save_preferences(self):
        """Sla voorkeuren op in het configuratiebestand."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.preferences, f, indent=4)
            messagebox.showinfo("Succes", "Voorkeuren succesvol opgeslagen!")
        except Exception as e:
            messagebox.showerror("Fout", f"Fout bij opslaan van voorkeuren: {e}")
    
    def create_gui(self):
        """Maak de GUI met tabs voor verschillende categorieën voorkeuren."""
        # Maak een notebook (tabbed interface)
        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Maak tabs voor verschillende categorieën
        job_types_frame = ttk.Frame(notebook)
        scheduling_frame = ttk.Frame(notebook)
        location_frame = ttk.Frame(notebook)
        notification_frame = ttk.Frame(notebook)
        
        notebook.add(job_types_frame, text="Opdrachttypes")
        notebook.add(scheduling_frame, text="Planning")
        notebook.add(location_frame, text="Locatie")
        notebook.add(notification_frame, text="Notificaties")
        
        # Vul de tabs met formulierelementen
        self.create_job_types_tab(job_types_frame)
        self.create_scheduling_tab(scheduling_frame)
        self.create_location_tab(location_frame)
        self.create_notification_tab(notification_frame)
        
        # Maak knoppen voor opslaan en annuleren
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        save_button = ttk.Button(button_frame, text="Opslaan", command=self.save_preferences)
        save_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Annuleren", command=lambda: None)  # Doe niets bij annuleren in frame
        cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def create_job_types_tab(self, parent):
        """Maak de tab voor opdrachttypes voorkeuren."""
        # Maak een frame met padding
        frame = ttk.Frame(parent, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Checkboxes voor opdrachttypes
        self.ikea_var = tk.BooleanVar(value=self.preferences["prefer_ikea"])
        ikea_check = ttk.Checkbutton(frame, text="IKEA-gerelateerde opdrachten", variable=self.ikea_var,
                                     command=lambda: self.update_preference("prefer_ikea", self.ikea_var.get()))
        ikea_check.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.electrical_var = tk.BooleanVar(value=self.preferences["prefer_electrical"])
        electrical_check = ttk.Checkbutton(frame, text="Elektriciteitsklussen", variable=self.electrical_var,
                                          command=lambda: self.update_preference("prefer_electrical", self.electrical_var.get()))
        electrical_check.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.internet_var = tk.BooleanVar(value=self.preferences["prefer_internet"])
        internet_check = ttk.Checkbutton(frame, text="Internet-gerelateerde opdrachten", variable=self.internet_var,
                                        command=lambda: self.update_preference("prefer_internet", self.internet_var.get()))
        internet_check.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.urgent_var = tk.BooleanVar(value=self.preferences["prefer_urgent"])
        urgent_check = ttk.Checkbutton(frame, text="Urgente opdrachten", variable=self.urgent_var,
                                      command=lambda: self.update_preference("prefer_urgent", self.urgent_var.get()))
        urgent_check.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        # Minimum uurloon
        ttk.Label(frame, text="Minimum uurloon (€):").grid(row=4, column=0, sticky=tk.W, pady=5)
        
        self.hourly_rate_var = tk.StringVar(value=str(self.preferences["min_hourly_rate"]))
        hourly_rate_entry = ttk.Entry(frame, textvariable=self.hourly_rate_var, width=10)
        hourly_rate_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        hourly_rate_entry.bind("<FocusOut>", lambda e: self.update_preference("min_hourly_rate", int(self.hourly_rate_var.get())))
        
        # Uitleg
        ttk.Label(frame, text="Selecteer de types opdrachten die automatisch moeten worden geaccepteerd.").grid(
            row=5, column=0, columnspan=2, sticky=tk.W, pady=20)
    
    def create_scheduling_tab(self, parent):
        """Maak de tab voor planningsvoorkeuren."""
        # Maak een frame met padding
        frame = ttk.Frame(parent, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Titel
        ttk.Label(frame, text="Maximum aantal opdrachten per dag:", font=("", 10, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Dagen van de week
        days = ["Zondag", "Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag"]
        self.max_jobs_vars = {}
        
        for i, day in enumerate(days):
            ttk.Label(frame, text=day).grid(row=i+1, column=0, sticky=tk.W, pady=5)
            
            self.max_jobs_vars[str(i)] = tk.StringVar(value=str(self.preferences["max_jobs_weekday"][str(i)]))
            spinbox = ttk.Spinbox(frame, from_=0, to=10, textvariable=self.max_jobs_vars[str(i)], width=5)
            spinbox.grid(row=i+1, column=1, sticky=tk.W, pady=5)
            spinbox.bind("<FocusOut>", lambda e, day=str(i): self.update_max_jobs(day))
        
        # Reistijd tussen opdrachten
        ttk.Label(frame, text="Reistijd tussen opdrachten (minuten):").grid(
            row=8, column=0, sticky=tk.W, pady=5)
        
        self.travel_time_var = tk.StringVar(value=str(self.preferences["travel_time_between_jobs"]))
        travel_time_entry = ttk.Entry(frame, textvariable=self.travel_time_var, width=10)
        travel_time_entry.grid(row=8, column=1, sticky=tk.W, pady=5)
        travel_time_entry.bind("<FocusOut>", lambda e: self.update_preference("travel_time_between_jobs", int(self.travel_time_var.get())))
    
    def create_location_tab(self, parent):
        """Maak de tab voor locatievoorkeuren."""
        # Maak een frame met padding
        frame = ttk.Frame(parent, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Voorkeur voor Amsterdam
        self.amsterdam_var = tk.BooleanVar(value=self.preferences["prefer_amsterdam"])
        amsterdam_check = ttk.Checkbutton(frame, text="Geef voorrang aan opdrachten in Amsterdam", variable=self.amsterdam_var,
                                         command=lambda: self.update_preference("prefer_amsterdam", self.amsterdam_var.get()))
        amsterdam_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Maximale afstand zonder toestemming
        ttk.Label(frame, text="Maximale afstand zonder toestemming (km):").grid(
            row=1, column=0, sticky=tk.W, pady=5)
        
        self.max_distance_var = tk.StringVar(value=str(self.preferences["max_distance_without_permission"]))
        max_distance_entry = ttk.Entry(frame, textvariable=self.max_distance_var, width=10)
        max_distance_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        max_distance_entry.bind("<FocusOut>", lambda e: self.update_preference("max_distance_without_permission", int(self.max_distance_var.get())))
        
        # Uitleg
        ttk.Label(frame, text="Voor opdrachten buiten de maximale afstand wordt eerst toestemming gevraagd.").grid(
            row=2, column=0, columnspan=2, sticky=tk.W, pady=20)
    
    def create_notification_tab(self, parent):
        """Maak de tab voor notificatievoorkeuren."""
        # Maak een frame met padding
        frame = ttk.Frame(parent, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Notificatiemethode
        ttk.Label(frame, text="Notificatiemethode:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.notification_method_var = tk.StringVar(value=self.preferences["notification_method"])
        telegram_radio = ttk.Radiobutton(frame, text="Telegram", variable=self.notification_method_var, value="telegram",
                                        command=lambda: self.update_preference("notification_method", "telegram"))
        telegram_radio.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        pushbullet_radio = ttk.Radiobutton(frame, text="Pushbullet", variable=self.notification_method_var, value="pushbullet",
                                          command=lambda: self.update_preference("notification_method", "pushbullet"))
        pushbullet_radio.grid(row=0, column=2, sticky=tk.W, pady=5)
        
        # Telegram instellingen
        telegram_frame = ttk.LabelFrame(frame, text="Telegram Instellingen")
        telegram_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W+tk.E, pady=10)
        
        ttk.Label(telegram_frame, text="Bot Token:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.telegram_token_var = tk.StringVar(value=self.preferences["telegram"]["bot_token"])
        telegram_token_entry = ttk.Entry(telegram_frame, textvariable=self.telegram_token_var, width=40)
        telegram_token_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        telegram_token_entry.bind("<FocusOut>", lambda e: self.update_telegram_preference("bot_token", self.telegram_token_var.get()))
        
        ttk.Label(telegram_frame, text="Chat ID:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.telegram_chat_id_var = tk.StringVar(value=self.preferences["telegram"]["chat_id"])
        telegram_chat_id_entry = ttk.Entry(telegram_frame, textvariable=self.telegram_chat_id_var, width=40)
        telegram_chat_id_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        telegram_chat_id_entry.bind("<FocusOut>", lambda e: self.update_telegram_preference("chat_id", self.telegram_chat_id_var.get()))
        
        # Pushbullet instellingen
        pushbullet_frame = ttk.LabelFrame(frame, text="Pushbullet Instellingen")
        pushbullet_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W+tk.E, pady=10)
        
        ttk.Label(pushbullet_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.pushbullet_api_key_var = tk.StringVar(value=self.preferences["pushbullet"]["api_key"])
        pushbullet_api_key_entry = ttk.Entry(pushbullet_frame, textvariable=self.pushbullet_api_key_var, width=40)
        pushbullet_api_key_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        pushbullet_api_key_entry.bind("<FocusOut>", lambda e: self.update_pushbullet_preference("api_key", self.pushbullet_api_key_var.get()))
        
        # Test notificatie knop
        test_button = ttk.Button(frame, text="Test Notificatie", command=self.test_notification)
        test_button.grid(row=3, column=0, sticky=tk.W, pady=10)
    
    def update_preference(self, key, value):
        """Update een voorkeur in het voorkeuren dictionary."""
        self.preferences[key] = value
    
    def update_max_jobs(self, day):
        """Update het maximum aantal opdrachten voor een specifieke dag."""
        try:
            value = int(self.max_jobs_vars[day].get())
            self.preferences["max_jobs_weekday"][day] = value
        except ValueError:
            messagebox.showerror("Fout", "Voer een geldig getal in voor het maximum aantal opdrachten.")
            self.max_jobs_vars[day].set(str(self.preferences["max_jobs_weekday"][day]))
    
    def update_telegram_preference(self, key, value):
        """Update een Telegram voorkeur in het voorkeuren dictionary."""
        self.preferences["telegram"][key] = value
    
    def update_pushbullet_preference(self, key, value):
        """Update een Pushbullet voorkeur in het voorkeuren dictionary."""
        self.preferences["pushbullet"][key] = value
    
    def test_notification(self):
        """Test de notificatie-instellingen."""
        method = self.preferences["notification_method"]
        
        if method == "telegram":
            if not self.preferences["telegram"]["bot_token"] or not self.preferences["telegram"]["chat_id"]:
                messagebox.showerror("Fout", "Vul eerst de Telegram Bot Token en Chat ID in.")
                return
        elif method == "pushbullet":
            if not self.preferences["pushbullet"]["api_key"]:
                messagebox.showerror("Fout", "Vul eerst de Pushbullet API Key in.")
                return
        
        # In een echte implementatie zou hier de notificatie worden getest
        messagebox.showinfo("Test", f"Notificatie zou worden verzonden via {method}.\n"
                                   f"Dit is een simulatie, geen echte notificatie wordt verzonden.")

def main():
    root = tk.Tk()
    root.title("MrFix Opdracht Automatisering - Voorkeuren")
    root.geometry("800x600")
    app = MrFixPreferencesGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
