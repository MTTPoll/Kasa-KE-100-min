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

---

### 1. Über HACS (Home Assistant Community Store)
1. Öffne in HA: **HACS → Integrationen → Benutzerdefinierte Repositories**.
2. Füge folgendes Repository hinzu (Typ: **Integration**):  
   ```
   https://github.com/MTTPoll/Kasa-KE-100-min
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
- Minimale Gerätetyp-Unterstützung (TRV).
- Sensoren wie Batterie oder Feuchtigkeit nur teilweise implementiert.

---

## Changelog

### 0.3.0
- Ist-Temperatur wird jetzt korrekt gepollt und aktualisiert.
- Feste Minimal-/Maximaltemperatur auf 5–30 °C.
- Polling-Intervall konfigurierbar über Optionsflow.
- README.md erweitert (inkl. HACS-Installation mit Repository-Link).
