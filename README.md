# Kasa KE100 (minimal)

Minimal Home Assistant integration for **TP-Link KH100 Hub + KE100 TRVs** and **Tapo T110** contacts.

👉 Features:
- Exposes KE100 TRVs as `climate` entities
- Shows current temperature
- Allows setting target temperature (whole °C only, 5–30 °C)
- Exposes T110 as `binary_sensor` (door/contact)
- Nothing else (no presets, no boost, no extras)

## Installation (via HACS)
1. Add this repo as a Custom Repository in HACS (Integration).
2. Search for Kasa KE100 (minimal) in HACS and install.
3. Restart Home Assistant.
4. Add the integration via Settings → Devices & Services → Add Integration.
5. Enter the KH100 hub IP and optionally username/password.

## Usage
- `climate` entity per KE100
- `binary_sensor` entity per T110

## Debugging
Enable debug logging:
```yaml
logger:
  default: warning
  logs:
    custom_components.kasa_ke100_min: debug
```
