import os
import json
import logging
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

# Probeer de andere componenten te importeren
try:
    from website_monitor import MrFixMonitor
    from job_filter import get_job_filter
    from calendar_integration import get_calendar_integration
    from notification import send_notification
except ImportError:
    # Dummy imports voor testen
    MrFixMonitor = None
    get_job_filter = None
    get_calendar_integration = None
    send_notification = None

# Configuratie
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_PATH = os.path.join(LOG_DIR, 'app.log')
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

class MrFixApp:
    def __init__(self, root):
        """Initialiseer de hoofdapplicatie."""
        self.root = root
        self.root.title("MrFix Opdracht Automatisering")
        self.root.geometry("900x700")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Maak een notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Maak tabs
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.preferences_frame = ttk.Frame(self.notebook)
        self.logs_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self.notebook.add(self.preferences_frame, text="Voorkeuren")
        self.notebook.add(self.logs_frame, text="Logboek")
        
        # Vul de tabs
        self.create_dashboard_tab()
        self.create_preferences_tab()
        self.create_logs_tab()
        
        # Initialiseer de monitoring thread
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Laad voorkeuren
        self.load_preferences()
        
        logging.info("MrFix App geïnitialiseerd")

    def create_dashboard_tab(self):
        """Maak de dashboard tab."""
        frame = ttk.Frame(self.dashboard_frame, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Status sectie
        status_frame = ttk.LabelFrame(frame, text="Status")
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(status_frame, text="Monitoring status:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.status_label = ttk.Label(status_frame, text="Gestopt", foreground="red")
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.start_button = ttk.Button(status_frame, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.grid(row=0, column=2, padx=5, pady=5)
        
        self.stop_button = ttk.Button(status_frame, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=3, padx=5, pady=5)
        
        # Statistieken sectie
        stats_frame = ttk.LabelFrame(frame, text="Statistieken")
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(stats_frame, text="Gemonitorde opdrachten:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.monitored_jobs_label = ttk.Label(stats_frame, text="0")
        self.monitored_jobs_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(stats_frame, text="Geaccepteerde opdrachten:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.accepted_jobs_label = ttk.Label(stats_frame, text="0")
        self.accepted_jobs_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(stats_frame, text="Laatste controle:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.last_check_label = ttk.Label(stats_frame, text="-")
        self.last_check_label.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Recente opdrachten sectie
        recent_frame = ttk.LabelFrame(frame, text="Recente Opdrachten")
        recent_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview voor recente opdrachten
        columns = ("titel", "locatie", "datum", "status")
        self.recent_jobs_tree = ttk.Treeview(recent_frame, columns=columns, show="headings")
        
        # Definieer kolomkoppen
        self.recent_jobs_tree.heading("titel", text="Titel")
        self.recent_jobs_tree.heading("locatie", text="Locatie")
        self.recent_jobs_tree.heading("datum", text="Datum")
        self.recent_jobs_tree.heading("status", text="Status")
        
        # Definieer kolombreedte
        self.recent_jobs_tree.column("titel", width=300)
        self.recent_jobs_tree.column("locatie", width=150)
        self.recent_jobs_tree.column("datum", width=150)
        self.recent_jobs_tree.column("status", width=100)
        
        # Voeg scrollbar toe
        scrollbar = ttk.Scrollbar(recent_frame, orient=tk.VERTICAL, command=self.recent_jobs_tree.yview)
        self.recent_jobs_tree.configure(yscroll=scrollbar.set)
        
        # Plaats de treeview en scrollbar
        self.recent_jobs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Voeg wat voorbeeldgegevens toe
        for i in range(5):
            self.recent_jobs_tree.insert("", tk.END, values=(f"Voorbeeld opdracht {i+1}", "Amsterdam", "2025-03-25", "Verwerkt"))

    def create_preferences_tab(self):
        """Maak de voorkeuren tab."""
        # Maak een instantie van de GUI klasse voor voorkeuren
        from gui import MrFixPreferencesGUI
        self.preferences_gui = MrFixPreferencesGUI(self.preferences_frame)

    def create_logs_tab(self):
        """Maak de logboek tab."""
        frame = ttk.Frame(self.logs_frame, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Log weergave
        log_frame = ttk.LabelFrame(frame, text="Logboek")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Text widget voor logs
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, width=80, height=20)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Knoppen
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        refresh_button = ttk.Button(button_frame, text="Vernieuwen", command=self.refresh_logs)
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = ttk.Button(button_frame, text="Wissen", command=self.clear_logs)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Laad initiële logs
        self.refresh_logs()

    def load_preferences(self):
        """Laad gebruikersvoorkeuren uit het configuratiebestand."""
        try:
            if os.path.exists(PREFERENCES_FILE):
                with open(PREFERENCES_FILE, 'r') as f:
                    self.preferences = json.load(f)
                    logging.info(f"Voorkeuren geladen uit {PREFERENCES_FILE}")
            else:
                logging.warning(f"Voorkeuren bestand niet gevonden: {PREFERENCES_FILE}")
                self.preferences = {}
        except Exception as e:
            logging.error(f"Fout bij laden van voorkeuren: {e}")
            self.preferences = {}

    def save_preferences(self):
        """Sla gebruikersvoorkeuren op in het configuratiebestand."""
        try:
            with open(PREFERENCES_FILE, 'w') as f:
                json.dump(self.preferences, f, indent=4)
            logging.info(f"Voorkeuren opgeslagen in {PREFERENCES_FILE}")
        except Exception as e:
            logging.error(f"Fout bij opslaan van voorkeuren: {e}")
            messagebox.showerror("Fout", f"Fout bij opslaan van voorkeuren: {e}")

    def start_monitoring(self):
        """Start de monitoring thread."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self.monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        self.status_label.config(text="Actief", foreground="green")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        logging.info("Monitoring gestart")
        self.update_log("Monitoring gestart")

    def stop_monitoring(self):
        """Stop de monitoring thread."""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1.0)
        
        self.status_label.config(text="Gestopt", foreground="red")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        logging.info("Monitoring gestopt")
        self.update_log("Monitoring gestopt")

    def monitoring_loop(self):
        """De hoofdlus voor monitoring."""
        try:
            # Initialiseer de monitor
            if MrFixMonitor:
                monitor = MrFixMonitor()
            else:
                # Dummy monitor voor testen
                class DummyMonitor:
                    def monitor_website(self):
                        time.sleep(5)  # Simuleer verwerking
                        return []
                    def cleanup(self):
                        pass
                monitor = DummyMonitor()
            
            while self.monitoring_active:
                try:
                    # Update de UI
                    self.root.after(0, self.update_last_check_label)
                    
                    # Monitor de website
                    new_jobs = monitor.monitor_website()
                    
                    # Update de UI met nieuwe opdrachten
                    if new_jobs:
                        self.root.after(0, lambda: self.update_jobs_count(len(new_jobs)))
                        self.root.after(0, lambda: self.update_log(f"{len(new_jobs)} nieuwe opdrachten gevonden"))
                        
                        # Voeg nieuwe opdrachten toe aan de treeview
                        for job in new_jobs:
                            self.root.after(0, lambda j=job: self.add_job_to_treeview(j))
                    
                    # Wacht voor de volgende controle
                    # In een echte implementatie zou dit de monitoring_interval uit de voorkeuren gebruiken
                    interval = 300  # 5 minuten in seconden
                    if hasattr(monitor, 'preferences') and 'monitoring_interval' in monitor.preferences:
                        interval = monitor.preferences['monitoring_interval']
                    
                    # Wacht in kleine stappen zodat we snel kunnen stoppen als dat nodig is
                    for _ in range(interval):
                        if not self.monitoring_active:
                            break
                        time.sleep(1)
                        
                except Exception as e:
                    logging.error(f"Fout in monitoring loop: {e}")
                    self.root.after(0, lambda: self.update_log(f"Fout: {e}"))
                    time.sleep(10)  # Wacht even voordat we het opnieuw proberen
            
            # Ruim resources op
            monitor.cleanup()
            
        except Exception as e:
            logging.error(f"Onverwachte fout in monitoring thread: {e}")
            self.root.after(0, lambda: messagebox.showerror("Fout", f"Onverwachte fout: {e}"))
            self.root.after(0, self.stop_monitoring)

    def update_last_check_label(self):
        """Update het label met de tijd van de laatste controle."""
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        self.last_check_label.config(text=now)

    def update_jobs_count(self, new_jobs_count):
        """Update de tellers voor gemonitorde en geaccepteerde opdrachten."""
        current_count = int(self.monitored_jobs_label.cget("text"))
        self.monitored_jobs_label.config(text=str(current_count + new_jobs_count))

    def add_job_to_treeview(self, job):
        """Voeg een opdracht toe aan de treeview."""
        self.recent_jobs_tree.insert("", 0, values=(
            job['title'],
            job['location'],
            job['date_posted'],
            "Verwerkt"
        ))
        
        # Beperk het aantal items in de treeview
        items = self.recent_jobs_tree.get_children()
        if len(items) > 20:
            self.recent_jobs_tree.delete(items[-1])

    def refresh_logs(self):
        """Vernieuw de logboek weergave."""
        try:
            self.log_text.delete(1.0, tk.END)
            
            if os.path.exists(LOG_PATH):
                with open(LOG_PATH, 'r') as f:
                    # Lees de laatste 100 regels
                    lines = f.readlines()[-100:]
                    for line in lines:
                        self.log_text.insert(tk.END, line)
                
                # Scroll naar het einde
                self.log_text.see(tk.END)
        except Exception as e:
            logging.error(f"Fout bij vernieuwen van logboek: {e}")
            messagebox.showerror("Fout", f"Fout bij vernieuwen van logboek: {e}")

    def clear_logs(self):
        """Wis de logboek weergave."""
        self.log_text.delete(1.0, tk.END)

    def update_log(self, message):
        """Voeg een bericht toe aan de logboek weergave."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"{timestamp} - INFO - {message}\n")
        self.log_text.see(tk.END)

    def on_closing(self):
        """Handler voor het sluiten van de applicatie."""
        if self.monitoring_active:
            if messagebox.askyesno("Afsluiten", "Monitoring is actief. Weet u zeker dat u wilt afsluiten?"):
                self.stop_monitoring()
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    """Start de applicatie."""
    root = tk.Tk()
    app = MrFixApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
