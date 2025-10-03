# Kasa KE100 (minimal) — v0.3.0

Home Assistant Custom Integration für **TP-Link Kasa KE100** Thermostate (via KH100 Hub).  
Fokus: **stabiles lokales Polling**, schlanker Code, Climate-Entity mit korrekten Min/Max-Grenzen (5–30°C).

## Features
- Lokales Polling des KH100 Hubs (über `python-kasa`)
- Automatische Erkennung von:
  - **Thermostat (TRV)** → `climate` Entitäten
  - **Kontakt-/Fenstersensor** (falls vorhanden) → `binary_sensor` Entitäten
- Climate:
  - `hvac_mode` & `hvac_action` aus dem Gerätemodus gemappt (`heating/idle/off`)
  - **Min 5°C / Max 30°C** (wie in der offiziellen TP-Link-Integration)
  - Setzen der Zieltemperatur
- Konfigurierbares **Polling-Intervall** (Optionsflow)

## Installation
1. Repository als ZIP herunterladen und in `config/custom_components/kasa_ke100_min/` entpacken.
2. Home Assistant neu starten.
3. In **Einstellungen → Geräte & Dienste → Integration hinzufügen** nach *Kasa KE100 (minimal)* suchen.

## Konfiguration
Beim Einrichten werden abgefragt:
- **Host** (IP des KH100 Hubs)
- **Username/Password** (falls am Hub erforderlich)
- **Polling-Intervall** (Optional, Standard 10s – kann später in den **Optionen** angepasst werden)

## Hinweise
- Die Climate-Entitäten lesen `current_temperature`, `target_temperature`, `hvac_mode` und `hvac_action` **live** aus dem Coordinator-Cache und schreiben ihren Zustand bei jedem Poll neu. So werden Ist-Werte zuverlässig aktualisiert.
- Für TRVs werden die vom Gerät gemeldeten Grenzen ignoriert (falls 7–35°C), stattdessen **immer 5–30°C** verwendet.

## Changelog
### 0.3.0
- **Fix:** `current_temperature` wird nun zuverlässig bei jedem Poll aktualisiert (Live-Properties + State-Write on Update).
- **Change:** Debug-Logs aus API/Coordinator/Climate entfernt (saubere Logs).
- **Feature:** Optionsflow für konfigurierbares Polling-Intervall.
- **Feature:** Binary Sensor für mögliche Kontaktsensor-Kinder.
- **Improvement:** Stabileres Mapping von `thermo.mode` → `hvac_mode`/`hvac_action`.

## Troubleshooting
- Wenn sich Werte nicht aktualisieren: Integration neu laden oder HA neu starten.
- Prüfe, ob `python-kasa` installiert und kompatibel ist (`requirements` in `manifest.json`).

---
Mit ❤️ gebaut. Feedback & Issues: GitHub Issues im Repo.
