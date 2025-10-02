# KASA KE100 Thermostat – HA Integration (Entity-Polling + Auth)

Diese Variante pollt **jede Entität** alle 30 Sekunden (über `SCAN_INTERVAL`) und nutzt **Benutzername/Passwort** für den Hub-Login. Ein zentraler Hub-Client dedupliziert/ throttelt die Abfragen. Ersetze in `helpers/hub.py -> async_fetch_devices()` die Demo-Logik durch deine reale KH100-Abfrage.

## Installation
1. Diesen Ordner in `custom_components/kasa_ke100_min` legen.
2. Home Assistant neu starten.
3. Integration hinzufügen → IP, Benutzername, Passwort eintragen.

## Hinweise
- Log aktivieren (optional):
  ```yaml
  logger:
    default: warning
    logs:
      custom_components.kasa_ke100_min: debug
  ```
