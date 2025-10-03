from __future__ import annotations
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, PLATFORMS
from .coordinator import KasaKe100Coordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    host = entry.data.get("host")
    username = entry.data.get("username")
    password = entry.data.get("password")
    scan_interval = entry.data.get("scan_interval")  # Sekunden (int) oder None

    client = KasaKe100Client(host, username, password)
    coordinator = KasaKe100Coordinator(hass, client, scan_interval_seconds=scan_interval)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "client": client,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    stored = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if stored:
        await stored["client"].async_close()
    return ok
