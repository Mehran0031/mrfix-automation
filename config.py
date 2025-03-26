# Configuratie-instellingen voor de MrFix app

# Monitoring instellingen
MONITORING_INTERVAL = 1  # Controle-interval in seconden

# Notificatie instellingen
NOTIFICATION_METHODS = {
    "telegram": True,
    "pushbullet": True,
    "email": True,
    "pushover": True,
    "safari_web_push": True
}

# Opdracht voorkeuren
MIN_HOURLY_RATE = 79  # Minimum uurloon in euro
PREFER_IKEA = True
PREFER_ELECTRICAL = True
PREFER_INTERNET = True
PREFER_URGENT = True

# Locatie voorkeuren
PREFER_AMSTERDAM = True
MAX_DISTANCE = 20  # km

# Planning voorkeuren
AVAILABLE_FROM_DATE = "2025-04-04"  # Beschikbaar vanaf deze datum
MAX_JOBS_PER_DAY = {
    "0": 3,  # Zondag: max 3
    "1": 5,  # Maandag: max 5
    "2": 2,  # Dinsdag: max 2
    "3": 5,  # Woensdag: max 5
    "4": 2,  # Donderdag: max 2
    "5": 2,  # Vrijdag: max 2
    "6": 3,  # Zaterdag: max 3
}
