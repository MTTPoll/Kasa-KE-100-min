# Kasa KE100 (KH100) — minimal Home Assistant Integration

> Version **0.2.5** · Custom integration for the **TP‑Link Tapo KH100** hub focusing on the **KE100 TRV** and **T310/T315 temperature sensors**.  
> Lightweight, no cloud, built for simple, reliable entities.

---

## ✨ Features

- **KE100 Thermostatic Radiator Valve (TRV)**
  - Exposes a standard **`climate`** entity.
  - Supported: `heat`/`off`, **target temperature**, **turn_on/turn_off**, **current temperature**, HVAC action.
  - Temperature precision: **0.1°C**, min/max: **5…30°C**.

- **Tapo T310 / T315 (Temperature/Humidity Sensor)**
  - Shows up as a **read‑only `climate`** entity so you can use **climate cards** on dashboards.
  - No controls, **no fake setpoint**.
  - **HVAC status is hidden**; the card won’t show “aus/Leerlauf”. The entity reports a stable `heat` label internally to avoid “unknown” state.
  - Attributes include **temperature** and **humidity** (see “Humidity bridging” below).

- **Contact sensors** (e.g., window/door) behind the KH100 are exposed as **`binary_sensor`** with `device_class: opening` (via coordinator data using `is_open`).

- **Smart classification**
  - KE100 vs. T310 is detected without reliable `model` info from the hub by using multiple signals (numeric `target_temp`, known ID prefixes, etc.).
  - Prevents T310 from being treated like a TRV even if the hub reports `hvac_mode`/`hvac_action` for sensors.

- **Humidity bridging for T310**
  1) Uses **hub‑provided** `humidity` when available.  
  2) Otherwise finds a **humidity sensor on the same device** (via the **Device/Entity Registry**) and mirrors its value as a `humidity` attribute on the climate entity.  
  3) As a fallback, looks for name‑based entities like `sensor.<slug(name)>_luftfeuchtigkeit`, `sensor.<slug(name)>_luftfeuchte`, or `sensor.<slug(name)>_humidity`.

- **Options**
  - **Scan interval** (seconds) configurable via Integration Options.

---

## 📦 Installation

1. Copy the folder `custom_components/kasa_ke100_min/` into your Home Assistant config directory.
2. Restart Home Assistant.
3. Go to **Settings → Devices & Services → Add Integration** and search for **“Kasa KE100 (min)”** (domain: `kasa_ke100_min`).

> **Config fields**
> - **Host** (IP/hostname of the **KH100** hub)
> - **Username / Password** (your local credentials for the hub if required)
> - **Scan interval** (in seconds; optional, also available in Options)

---

## 🧩 Platforms & Entities

### `climate` — KE100 TRV
- `hvac_modes`: `heat`, `off`
- Supported features: `TARGET_TEMPERATURE`, `TURN_ON`, `TURN_OFF`
- Attributes: `current_temperature`, `target_temperature`, `hvac_action`

### `climate` — T310/T315 Display (read‑only)
- **No controls**, **no selectable modes**.
- Shows **current temperature**.
- Adds `humidity` attribute (from hub or bridged sensor).
- Internally reports a stable `hvac_mode=heat` to avoid the “unknown” entity state.  
  `hvac_action` is not shown.

### `binary_sensor` — Contact sensors
- Uses `is_open` from the hub data.
- Exposed with appropriate `device_class`.

---

## 🧠 Humidity Bridging Details (T310/T315)

The integration tries—non‑destructively—to display humidity next to temperature on the T310 climate entity:

1. **Direct from hub**: If the KH100 provides `humidity`, it’s used as is.  
2. **Same device**: The integration looks up the **Device Registry** and searches for a `sensor` entity with `device_class: humidity` **on the same device**; if found, its numeric state is mirrored as `humidity`.  
3. **Name fallback**: If there’s no such device‑bound sensor, the following names are tried (where `<slug(name)>` is the friendly name lowercased with underscores):  
   - `sensor.<slug(name)>_luftfeuchtigkeit`  
   - `sensor.<slug(name)>_luftfeuchte`  
   - `sensor.<slug(name)>_humidity`

> This is a *read‑only mirror* for UI convenience; it does not modify or create any native sensor entities.

---

## 🧰 Options & Configuration Flow

- **Scan interval**: set in seconds via **Options** after adding the integration.  
- Re‑loading the integration picks up entity/classification changes without removing devices.

---

## 🧪 Dashboard Examples (Mushroom)

If you prefer a very clean T310 display without any HVAC text, use **Mushroom**’s template card.  
Below are two ready‑to‑use snippets you can paste into your dashboard YAML.

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

> Replace `climate.temp_heizung` with the actual entity ID of your T310 climate entity (e.g., `climate.temp_wr`).

---

## 🔎 Troubleshooting

- **T310 appears with controls / as TRV**  
  Update to **v0.2.5** or newer. The classification prevents sensors from being treated as TRVs even if the hub reports `hvac_mode` for them.

- **Humidity not visible on T310**  
  Ensure there is a humidity sensor entity for the same device (`device_class: humidity`).  
  If not, create one (e.g., via a template or the native integration that exposes the humidity), or name the humidity entity using one of the fallback patterns listed above.

- **Entity shows “unknown”**  
  Fixed in **v0.2.5** by reporting a stable internal `hvac_mode` for T310 while hiding actions/modes from the UI.

- **Old/fake entities remain**  
  Remove or disable the old entities once; they will be recreated correctly after reloading the integration.

- **Logs**  
  The integration ships **without verbose debug logs**. You can still enable normal logging:
  ```yaml
  logger:
    default: info
    logs:
      custom_components.kasa_ke100_min: info
  ```

---

## 🗒️ Changelog

**0.2.5**
- T310/T315: read‑only climate entity, **no controls**, no HVAC action line, no mode chips.
- Avoid “unknown” by providing a stable internal mode; **humidity bridging** via device registry + name fallback.
- Cleaned up code & removed debug logging; features use **feature sets** (HA‑conform).

(Older versions: internal/testing only.)

---

## ⚠️ Notes & Limitations

- The KH100 hub sometimes omits `model` info; this integration uses **heuristics** (e.g., numeric `target_temp`, known ID prefixes) to classify devices.
- This project aims to be **minimal and local**. It doesn’t implement every KH100 feature—only what’s needed for KE100/T310 + basic contact sensors.

---

## 📄 License

MIT (or your preferred license). © Contributors.

