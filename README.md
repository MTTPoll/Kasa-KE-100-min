# Kasa KE100 (minimal)

Minimal Home Assistant integration for **TP-Link KH100 Hub + KE100 TRVs** and **Tapo T110** contacts.

## Features
- Exposes KE100 as `climate` entities (current temp + target temp)
- **Whole °C only** (step 1.0, 5–30 °C)
- Exposes T110 as `binary_sensor` (door/contact)
- HACS-ready, UI config flow (host + optional username/password)

## Installation (via HACS)
1. Add this repo as a Custom Repository in HACS (Integration).
2. Search for **Kasa KE100 (minimal)** in HACS and install.
3. Restart Home Assistant.
4. Add the integration via **Settings → Devices & Services → Add Integration** and enter your KH100 IP.

## Debugging
Enable debug logging:
```yaml
logger:
  default: warning
  logs:
    custom_components.kasa_ke100_min: debug
    kasa: debug
```
