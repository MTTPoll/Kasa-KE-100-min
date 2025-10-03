# Kasa KE100 Minimal Integration

Eine minimalistische **Home Assistant Custom Integration** für den **TP-Link Kasa KE100 Heizkörperthermostat** über den KH100 Hub.

---

## Features
- Anbindung an KH100 Hub (lokal)
- Polling des Status inkl. **Ist-Temperatur** und **Soll-Temperatur**
- Setzen von Zieltemperaturen und Modus (heat/off)
- Polling-Intervall frei konfigurierbar
- Unterstützt mehrere Thermostate pro Hub
- Minimale, schnelle Implementierung ohne Cloud

---

## Installation

### 1. Manuell
1. Lade das ZIP-Archiv aus den [Releases](https://github.com/deinuser/homeassistant-kasa-ke100-min/releases) herunter.
2. Entpacke es und kopiere den Ordner  
   `custom_components/kasa_ke100_min/`  
   nach:  
   ```
   <HA config>/custom_components/kasa_ke100_min/
   ```
3. Home Assistant neu starten.

---

### 2. Über HACS (Home Assistant Community Store)
1. Öffne in HA: **HACS → Integrationen → Benutzerdefinierte Repositories**.
2. Füge folgendes Repository hinzu (Typ: **Integration**):  
   ```
   https://github.com/deinuser/homeassistant-kasa-ke100-min
   ```
3. Suche in HACS nach **Kasa KE100 Minimal** und installiere es.
4. Home Assistant neu starten.

---

## Einrichtung
1. Nach dem Neustart von Home Assistant:  
   → **Einstellungen → Geräte & Dienste → Integration hinzufügen → Kasa KE100 Minimal**
2. Host, Benutzername, Passwort eingeben.
3. Polling-Intervall in Sekunden einstellen.

---

## Bekannte Einschränkungen
- Keine Fenster-Offen-Erkennung (vorerst).
- Minimale Gerätetyp-Unterstützung (TRV).
- Sensoren wie Batterie oder Feuchtigkeit nur teilweise implementiert.

---

## Changelog

### 0.3.0
- Ist-Temperatur wird jetzt korrekt gepollt und aktualisiert.
- Feste Minimal-/Maximaltemperatur auf 5–30 °C.
- Debug-Ausgaben entfernt (API, Coordinator, Climate).
- Polling-Intervall konfigurierbar über Optionsflow.
- README.md erweitert (inkl. HACS-Installation mit Repository-Link).
