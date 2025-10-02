# KASA KE100 Thermostat – HA Integration (Entity-Polling)

Diese Variante pollt **jede Entität** alle 30 Sekunden (über `SCAN_INTERVAL`) und holt sich die Werte aus einem zentralen Hub-Client mit Dedupe/Throttle. So siehst du Änderungen regelmäßig, auch ohne DataUpdateCoordinator.

## Installation
1. Diesen Ordner in `custom_components/kasa_ke100_min` legen.
2. Home Assistant neu starten.
3. Integration hinzufügen → Hub-IP eintragen.

## Hinweise
- Das echte Auslesen des KH100 ist in `helpers/hub.py -> async_fetch_devices()` mit `# TODO` markiert. Ersetze die Demo-Logik durch deine reale Hub-Abfrage.
- Log aktivieren (optional):
  ```yaml
  logger:
    default: warning
    logs:
      custom_components.kasa_ke100_min: debug
  ```
