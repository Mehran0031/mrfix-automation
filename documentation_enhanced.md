# MrFix Automatiseringssysteem - Documentatie

## Inhoudsopgave
1. [Introductie](#introductie)
2. [Installatie](#installatie)
3. [Configuratie](#configuratie)
4. [Notificatiemethoden](#notificatiemethoden)
   - [Telegram](#telegram)
   - [Email (Gmail)](#email-gmail)
   - [Pushover (iOS)](#pushover-ios)
   - [Safari Web Push](#safari-web-push)
   - [Pushbullet](#pushbullet)
5. [Google Agenda Integratie](#google-agenda-integratie)
6. [Gebruik van de Applicatie](#gebruik-van-de-applicatie)
7. [Probleemoplossing](#probleemoplossing)

## Introductie

Het MrFix Automatiseringssysteem is een Python-applicatie met een gebruiksvriendelijke GUI die automatisch de MrFix website monitort op nieuwe opdrachten, deze filtert volgens uw voorkeuren, controleert of u beschikbaar bent in uw Google Agenda, en u notificaties stuurt via verschillende methoden.

De applicatie biedt de volgende functionaliteiten:
- Monitoren van de MrFix website op nieuwe opdrachten
- Filteren van opdrachten op basis van type, uurloon en locatie
- Integratie met Google Agenda om beschikbaarheid te controleren
- Automatisch accepteren van geschikte opdrachten
- Notificaties via verschillende methoden (Telegram, Email, Pushover, Safari Web Push, Pushbullet)
- Gebruiksvriendelijke GUI om alle instellingen aan te passen

## Installatie

### Vereisten
- Python 3.8 of hoger
- pip (Python package manager)
- VS Code (aanbevolen, maar niet vereist)

### Stappen
1. Download en pak het ZIP-bestand uit
2. Open een terminal of command prompt
3. Navigeer naar de uitgepakte directory
4. Installeer de vereiste packages:
   ```
   pip install -r requirements.txt
   ```

## Configuratie

### Eerste configuratie
1. Start de applicatie:
   ```
   python app.py
   ```
2. De applicatie opent met een tabbed interface
3. Ga naar de "Voorkeuren" tab om uw instellingen te configureren
4. Configureer de verschillende secties volgens uw voorkeuren
5. Klik op "Opslaan" om uw instellingen op te slaan

### Opdrachttypes voorkeuren
- **IKEA-gerelateerde opdrachten**: Schakel in om voorrang te geven aan IKEA-gerelateerde opdrachten
- **Elektriciteitsklussen**: Schakel in om voorrang te geven aan elektriciteitsklussen
- **Internet-gerelateerde opdrachten**: Schakel in om voorrang te geven aan internet-gerelateerde opdrachten
- **Urgente opdrachten**: Schakel in om voorrang te geven aan urgente opdrachten
- **Minimum uurloon**: Stel het minimum uurloon in voor opdrachten (standaard €79)

### Planningsvoorkeuren
- **Maximum aantal opdrachten per dag**: Stel het maximum aantal opdrachten in voor elke dag van de week
  - Maandag: Standaard 5 opdrachten
  - Dinsdag: Standaard 2 opdrachten
  - Woensdag: Standaard 5 opdrachten
  - Donderdag: Standaard 2 opdrachten
  - Vrijdag: Standaard 2 opdrachten
  - Zaterdag: Standaard 3 opdrachten
  - Zondag: Standaard 3 opdrachten

### Locatievoorkeuren
- **Voorrang voor Amsterdam**: Schakel in om voorrang te geven aan opdrachten in Amsterdam
- **Maximale afstand zonder toestemming**: Stel de maximale afstand in (in km) voor opdrachten waarvoor geen toestemming nodig is
- **Reistijd tussen opdrachten**: Stel de benodigde reistijd in (in minuten) tussen opdrachten

### Monitoring instellingen
- **Controle-interval**: Stel in hoe vaak (in minuten) de MrFix website wordt gecontroleerd
- **Automatisch accepteren**: Schakel in om geschikte opdrachten automatisch te accepteren

## Notificatiemethoden

Het systeem ondersteunt verschillende notificatiemethoden. U kunt kiezen welke methode u wilt gebruiken in de "Notificaties" tab.

### Telegram

Telegram is een berichtendienst die werkt op alle platforms (iOS, Android, Windows, macOS, Linux).

#### Configuratie
1. Maak een Telegram bot aan via de BotFather:
   - Open Telegram en zoek naar @BotFather
   - Stuur het commando `/newbot`
   - Volg de instructies om een nieuwe bot aan te maken
   - Noteer de bot token die je ontvangt
2. Vind je chat ID:
   - Stuur een bericht naar je nieuwe bot
   - Open in je browser: `https://api.telegram.org/bot<YourBOTToken>/getUpdates`
   - Zoek naar `"chat":{"id":123456789}` en noteer het ID nummer
3. Vul in de applicatie de volgende velden in:
   - Bot token: De token die je van BotFather hebt ontvangen
   - Chat ID: Je chat ID nummer

### Email (Gmail)

Email notificaties worden verzonden via Gmail SMTP.

#### Configuratie
1. Maak een app-specifiek wachtwoord aan voor je Gmail account:
   - Ga naar je Google Account instellingen
   - Ga naar Beveiliging > Inloggen bij Google > App-wachtwoorden
   - Selecteer "App" en kies "Overige (aangepaste naam)"
   - Voer een naam in (bijv. "MrFix Automatisering")
   - Klik op "Genereren" en noteer het gegenereerde wachtwoord
2. Vul in de applicatie de volgende velden in:
   - Gmail gebruikersnaam: Je volledige Gmail adres
   - App-wachtwoord: Het gegenereerde app-specifieke wachtwoord
   - Ontvanger e-mail: Het e-mailadres waar je de notificaties wilt ontvangen

### Pushover (iOS)

Pushover is een dienst die native push notificaties naar iOS-apparaten stuurt.

#### Configuratie
1. Maak een Pushover account aan op [pushover.net](https://pushover.net/)
2. Download de Pushover app op je iPhone
3. Log in op de Pushover website en noteer je User Key
4. Maak een nieuwe applicatie aan:
   - Ga naar "Your Applications" op de Pushover website
   - Klik op "Create a New Application/API Token"
   - Vul de details in en noteer de API Token
5. Vul in de applicatie de volgende velden in:
   - API token: De API Token van je Pushover applicatie
   - User key: Je Pushover User Key

### Safari Web Push

Safari Web Push notificaties worden verzonden via de browser en werken op macOS en iOS.

#### Configuratie
Safari Web Push vereist een webserver en client-side JavaScript. De applicatie bevat een vereenvoudigde implementatie die lokaal werkt, maar voor volledige functionaliteit moet u:

1. Een webserver opzetten met HTTPS
2. De Web Push API implementeren
3. Een service worker registreren
4. VAPID keys genereren

Gedetailleerde instructies voor het opzetten van Safari Web Push zijn beschikbaar in de [Apple Developer Documentation](https://developer.apple.com/documentation/usernotifications/sending-web-push-notifications-in-web-apps-and-browsers).

### Pushbullet

Pushbullet is een dienst die notificaties naar verschillende apparaten kan sturen.

#### Configuratie
1. Maak een Pushbullet account aan op [pushbullet.com](https://www.pushbullet.com/)
2. Download de Pushbullet app op je apparaten
3. Ga naar je account instellingen en klik op "Create Access Token"
4. Noteer de gegenereerde API key
5. Vul in de applicatie het volgende veld in:
   - API key: De gegenereerde Pushbullet API key

## Google Agenda Integratie

De applicatie kan integreren met Google Agenda om uw beschikbaarheid te controleren en opdrachten in te plannen.

### Configuratie
1. Ga naar de [Google Cloud Console](https://console.cloud.google.com/)
2. Maak een nieuw project aan
3. Schakel de Google Calendar API in:
   - Ga naar "APIs & Services" > "Library"
   - Zoek naar "Google Calendar API" en schakel deze in
4. Maak OAuth 2.0 credentials aan:
   - Ga naar "APIs & Services" > "Credentials"
   - Klik op "Create Credentials" > "OAuth client ID"
   - Selecteer "Desktop app" als applicatietype
   - Geef een naam en klik op "Create"
5. Download het credentials.json bestand
6. Plaats het bestand in de 'data' map van de applicatie
7. Vul in de applicatie het volgende veld in:
   - Agenda ID: Gebruik 'primary' voor je hoofdagenda, of een specifiek agenda ID
   - Automatisch inplannen: Schakel in om opdrachten automatisch in te plannen

## Gebruik van de Applicatie

### Starten van de applicatie
```
python app.py
```

### Dashboard
Het dashboard toont een overzicht van:
- Actieve monitoring status
- Recente opdrachten
- Geaccepteerde opdrachten
- Notificatie log

### Voorkeuren
De voorkeuren tab stelt u in staat om alle instellingen aan te passen:
- Opdrachttypes voorkeuren
- Planningsvoorkeuren
- Locatievoorkeuren
- Notificatie-instellingen
- Google Agenda instellingen

### Logboek
Het logboek tab toont gedetailleerde logs van de applicatie, inclusief:
- Monitoring activiteit
- Gedetecteerde opdrachten
- Acceptatie beslissingen
- Notificaties
- Fouten

## Probleemoplossing

### Algemene problemen

**Probleem**: De applicatie start niet
**Oplossing**: 
- Controleer of Python correct is geïnstalleerd
- Controleer of alle vereiste packages zijn geïnstalleerd met `pip install -r requirements.txt`
- Controleer de logs in de 'logs' map voor specifieke foutmeldingen

**Probleem**: De applicatie detecteert geen opdrachten
**Oplossing**:
- Controleer of het controle-interval niet te lang is
- Controleer of de MrFix website URL correct is
- Controleer of er internetverbinding is
- Controleer de logs voor specifieke foutmeldingen

### Notificatieproblemen

**Probleem**: Telegram notificaties werken niet
**Oplossing**:
- Controleer of de bot token en chat ID correct zijn
- Controleer of je een bericht hebt gestuurd naar de bot
- Controleer of de bot niet is geblokkeerd

**Probleem**: Email notificaties werken niet
**Oplossing**:
- Controleer of het Gmail adres en app-wachtwoord correct zijn
- Controleer of "Minder veilige apps" is ingeschakeld in je Google account
- Controleer of er geen beveiligingswaarschuwingen zijn in je Gmail account

**Probleem**: Pushover notificaties werken niet
**Oplossing**:
- Controleer of de API token en user key correct zijn
- Controleer of de Pushover app is geïnstalleerd en ingelogd
- Controleer of je het dagelijkse limiet van notificaties niet hebt bereikt

**Probleem**: Safari Web Push notificaties werken niet
**Oplossing**:
- Controleer of je Safari browser notificaties heeft ingeschakeld
- Controleer of je de website hebt toegevoegd aan je startscherm
- Controleer of je de juiste VAPID keys hebt geconfigureerd

**Probleem**: Pushbullet notificaties werken niet
**Oplossing**:
- Controleer of de API key correct is
- Controleer of de Pushbullet app is geïnstalleerd en ingelogd
- Controleer of je apparaat is verbonden met je Pushbullet account

### Google Agenda problemen

**Probleem**: Google Agenda integratie werkt niet
**Oplossing**:
- Controleer of het credentials.json bestand correct is geplaatst
- Controleer of je de Google Calendar API hebt ingeschakeld
- Controleer of je de juiste toestemmingen hebt gegeven tijdens de OAuth flow
- Controleer of het agenda ID correct is
