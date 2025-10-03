# Kasa KE100 (KH100) — minimal Home Assistant Integration
**Version 0.2.5** · Custom integration for the **TP‑Link Tapo KH100** hub focusing on **KE100 TRV** and **T310/T315 sensors**.  
**Zweisprachig / Bilingual:** Deutsch & English

---

## 🇩🇪 Deutsch

### ✨ Funktionen
- **KE100 Thermostatventil (TRV)**
  - Als **`climate`**-Entität mit `heat`/`off`, **Solltemperatur**, **turn_on/turn_off**, **Ist-Temperatur**, HVAC-Action.
  - Genauigkeit **0,1 °C**, Bereich **5…30 °C**.
- **Tapo T310 / T315 (Temp/Feuchte)**
  - **Read‑only `climate`** für schöne **Climate‑Karten**, **ohne** Stellfunktionen.
  - **Keine Modus-Auswahl**; intern wird ein stabiler `hvac_mode=heat` gesetzt, damit die Entität **nicht „unknown“** ist.  
    Es gibt **keine** `hvac_action`‑Zeile.
  - Zeigt **Ist‑Temperatur** und (falls verfügbar) **Luftfeuchte** als Attribut (siehe „Humidity‑Bridging“).
- **Kontaktsensoren** am KH100 erscheinen als **`binary_sensor`** (`device_class: opening`), sofern vom Hub mit `is_open` gemeldet.
- **Clevere Klassifizierung**
  - Erkennung von KE100 vs. T310/T315 auch **ohne** zuverlässiges `model` des Hubs: numerisches `target_temp`, bekannte ID‑Präfixe etc.
  - Verhindert, dass T310 als TRV behandelt wird, selbst wenn der Hub `hvac_mode`/`hvac_action` liefert.
- **Humidity‑Bridging für T310/T315**
  1) Nutzt **Hub‑Wert** `humidity`, wenn vorhanden.  
  2) Sonst wird im **Geräte-/Entitäten‑Register** eine **Feuchte‑Sensor‑Entität desselben Geräts** gesucht (`device_class: humidity`) und deren Wert gespiegelt.  
  3) Fallback per Name: `sensor.<slug(name)>_luftfeuchtigkeit`, `sensor.<slug(name)>_luftfeuchte`, `sensor.<slug(name)>_humidity`.
- **Optionen**
  - **Scan‑Intervall** (Sekunden) über Integrations‑Optionen einstellbar.

### 📦 Installation
1. Ordner `custom_components/kasa_ke100_min/` in dein Home‑Assistant‑Config‑Verzeichnis kopieren.
2. Home Assistant neu starten.
3. **Einstellungen → Geräte & Dienste → Integration hinzufügen** → nach **„Kasa KE100 (min)“** suchen (Domain: `kasa_ke100_min`).

**Konfig-Felder**
- **Host** (IP/Hostname des **KH100** Hubs)
- **Benutzername / Passwort** (lokale Hub‑Zugangsdaten, falls erforderlich)
- **Scan‑Intervall** (Sekunden; optional/auch in Optionen)

### 🧩 Plattformen & Entitäten
**`climate` — KE100 TRV**
- `hvac_modes`: `heat`, `off`
- Features: `TARGET_TEMPERATURE`, `TURN_ON`, `TURN_OFF`
- Attribute: `current_temperature`, `target_temperature`, `hvac_action`

**`climate` — T310/T315 (Anzeige, read‑only)**
- **Keine** Bedienung, **keine** Modus‑Auswahl.
- Zeigt **Ist‑Temperatur**; `humidity` als Attribut (Hub oder Bridging).
- Intern fester `hvac_mode=heat`, `hvac_action` **nicht gesetzt** → keine Statuszeile.

**`binary_sensor` — Kontakte**
- Verwendet Hub‑Feld `is_open`, `device_class: opening`.

### 🧠 Details Humidity‑Bridging
1. Hub‑Wert `humidity` hat Vorrang.  
2. Sonst per **Geräte‑Registry**: Feuchte‑Sensor desselben Geräts mit `device_class: humidity`.  
3. Fallback per Name: `sensor.<slug(name)>_luftfeuchtigkeit` / `_luftfeuchte` / `_humidity`.  
> Es wird **nur gespiegelt** (read‑only) – es entstehen keine zusätzlichen Sensor‑Entitäten.

### 🧰 Optionen & Flow
- **Scan‑Intervall** in Sekunden über **Optionen** nach Einrichtung.
- **Reload** der Integration übernimmt Klassifizierungs‑/Entitäts‑Änderungen idR ohne Entfernen.

### 🧪 Dashboard‑Beispiele (Mushroom)
**Einfache 2‑Zeilen‑Karte**
```yaml
type: custom:mushroom-template-card
entity: climate.temp_heizung  # dein T310-Climate-Entity
primary: >
  {{ state_attr(entity, 'friendly_name') or 'Tapo T310' }}
secondary: >
  {{ state_attr(entity, 'current_temperature') | default('–') }} °C ·
  {{ state_attr(entity, 'humidity') | default('–') }} %
icon: mdi:thermometer
badge_icon: mdi:water-percent
badge_color: blue
multiline_secondary: true
tap_action:
  action: more-info
```

**Kompakt horizontal**
```yaml
type: custom:mushroom-template-card
entity: climate.temp_heizung
primary: >
  {{ state_attr(entity, 'current_temperature') | default('–') }} °C
secondary: >
  {{ state_attr(entity, 'humidity') | default('–') }} %
icon: mdi:thermometer
layout: horizontal
tap_action:
  action: more-info
```

### 🔎 Troubleshooting
- **T310 hat Controls / wird als TRV erkannt** → Update auf **v0.2.5** oder neuer.
- **Keine Luftfeuchte sichtbar** → sicherstellen, dass es eine Feuchte‑Entität mit `device_class: humidity` am **gleichen Gerät** gibt (oder Namens‑Fallback nutzen).
- **Entität „unknown“** → in **v0.2.5** gelöst (stabiler interner Modus für T310).
- **Alte/falsche Entitäten** → einmalig entfernen/ausblenden, danach korrekt neu anlegen.
- **Logging** → Integration kommt ohne Debug‑Spam; normales Logging per:
  ```yaml
  logger:
    default: info
    logs:
      custom_components.kasa_ke100_min: info
  ```

### 🗒️ Changelog
**0.2.5**
- T310/T315: read‑only Climate, **keine** Modi/Buttons; **keine** HVAC‑Action‑Zeile.
- „unknown“ vermieden; **Humidity‑Bridging** (Registry + Namens‑Fallback).
- Code bereinigt, Feature‑Sets HA‑konform.

### ⚠️ Hinweise
- KH100 liefert teils kein `model`; Heuristiken (z. B. numerisches `target_temp`, ID‑Präfixe) übernehmen die Klassifizierung.
- Minimaler, lokaler Ansatz – deckt **KE100/T310** + einfache Kontakte ab.

### 📄 Lizenz
MIT (oder gewünschte Lizenz). © Contributors.

---

## 🇬🇧 English

### ✨ Features
- **KE100 Thermostatic Radiator Valve (TRV)**
  - Exposes a **`climate`** entity with `heat`/`off`, **target temperature**, **turn_on/turn_off**, **current temperature**, HVAC action.
  - Precision **0.1 °C**, range **5…30 °C**.
- **Tapo T310 / T315 (Temp/Humidity)**
  - **Read‑only `climate`** for nice **climate cards**, **no** controls.
  - **No mode selection**; internally reports a stable `hvac_mode=heat` so the entity **never becomes `unknown`**.  
    There is **no** `hvac_action` line.
  - Shows **current temperature**, plus **humidity** attribute (see “Humidity bridging”).
- **Contact sensors** behind KH100 are exposed as **`binary_sensor`** (`device_class: opening`) when `is_open` is present.
- **Smart classification**
  - Detects KE100 vs. T310/T315 even **without** reliable hub `model`: numeric `target_temp`, known ID prefixes, etc.
  - Prevents T310 from being treated as a TRV even if the hub exposes `hvac_mode` / `hvac_action` for sensors.
- **Humidity bridging for T310/T315**
  1) Use **hub** `humidity` if available.  
  2) Otherwise look up a **humidity sensor on the same device** via **Device/Entity Registry** and mirror its value.  
  3) Fallback by name: `sensor.<slug(name)>_luftfeuchtigkeit`, `sensor.<slug(name)>_luftfeuchte`, `sensor.<slug(name)>_humidity`.
- **Options**
  - **Scan interval** (seconds) via Integration Options.

### 📦 Installation
1. Copy `custom_components/kasa_ke100_min/` into your Home Assistant config.
2. Restart Home Assistant.
3. **Settings → Devices & Services → Add Integration** → search **“Kasa KE100 (min)”** (domain: `kasa_ke100_min`).

**Config fields**
- **Host** (IP/hostname of the **KH100** hub)  
- **Username / Password** (local hub credentials if required)  
- **Scan interval** (seconds; optional/also via Options)

### 🧩 Platforms & Entities
**`climate` — KE100 TRV**
- `hvac_modes`: `heat`, `off`
- Features: `TARGET_TEMPERATURE`, `TURN_ON`, `TURN_OFF`
- Attributes: `current_temperature`, `target_temperature`, `hvac_action`

**`climate` — T310/T315 Display (read‑only)**
- **No** controls, **no** selectable modes.
- Shows **current temperature**; `humidity` attribute (hub or bridging).
- Internally fixed `hvac_mode=heat`; `hvac_action` **not set** (no status line).

**`binary_sensor` — Contact sensors**
- Uses `is_open` from hub data (`device_class: opening`).

### 🧠 Humidity Bridging Details
1. Hub‑provided `humidity` is preferred.  
2. Else, **Device Registry** is used to find a humidity sensor on the **same device** and mirror its value.  
3. Name fallback: `sensor.<slug(name)>_luftfeuchtigkeit` / `_luftfeuchte` / `_humidity`.  
> This is a **read‑only mirror** for UI convenience; it does not create additional sensors.

### 🧰 Options & Flow
- **Scan interval** in seconds via **Options** after setup.
- Reloading the integration usually picks up reclassification/entity changes without deletion.

### 🧪 Dashboard Examples (Mushroom)
**Simple two‑line card**
```yaml
type: custom:mushroom-template-card
entity: climate.temp_heizung  # your T310 climate entity
primary: >
  {{ state_attr(entity, 'friendly_name') or 'Tapo T310' }}
secondary: >
  {{ state_attr(entity, 'current_temperature') | default('–') }} °C ·
  {{ state_attr(entity, 'humidity') | default('–') }} %
icon: mdi:thermometer
badge_icon: mdi:water-percent
badge_color: blue
multiline_secondary: true
tap_action:
  action: more-info
```

**Compact horizontal variant**
```yaml
type: custom:mushroom-template-card
entity: climate.temp_heizung
primary: >
  {{ state_attr(entity, 'current_temperature') | default('–') }} °C
secondary: >
  {{ state_attr(entity, 'humidity') | default('–') }} %
icon: mdi:thermometer
layout: horizontal
tap_action:
  action: more-info
```

### 🔎 Troubleshooting
- **T310 shows controls / appears as TRV** → Update to **v0.2.5** or newer.
- **Humidity not visible** → ensure a humidity entity with `device_class: humidity` exists on the **same device** (or use name fallback).
- **Entity state “unknown”** → resolved in **v0.2.5** (stable internal mode for T310).
- **Old/wrong entities remain** → remove/disable once; they’ll be recreated correctly after reload.
- **Logging**
  ```yaml
  logger:
    default: info
    logs:
      custom_components.kasa_ke100_min: info
  ```

### 🗒️ Changelog
**0.2.5**
- T310/T315: read‑only climate entity, **no** modes/buttons; **no** HVAC action line.
- Avoid “unknown”; **humidity bridging** (registry + name fallback).
- Cleaned code & HA‑conform feature sets.

### ⚠️ Notes & Limitations
- KH100 sometimes omits `model`; classification uses **heuristics** (numeric `target_temp`, ID prefixes).  
- Minimal, local approach — covers **KE100/T310** + simple contact sensors.

### 📄 License
MIT (or your preferred license). © Contributors.
