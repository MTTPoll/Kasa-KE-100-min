
from __future__ import annotations
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from .const import DOMAIN, CONF_HOST, CONF_USERNAME, CONF_PASSWORD, CONF_SCAN_INTERVAL
from .api import KasaKe100Client
from .coordinator import KasaKe100Coordinator

_LOGGER = logging.getLogger(__name__)

# Add 'sensor' so T310 are set up as sensors alongside existing platforms
PLATFORMS: list[str] = ["climate", "sensor", "binary_sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    host = entry.data.get(CONF_HOST)
    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)
    scan_seconds = entry.options.get(CONF_SCAN_INTERVAL) or entry.data.get(CONF_SCAN_INTERVAL)

    client = KasaKe100Client(host, username, password)
    try:
        await client.async_connect()
    except Exception as err:
        _LOGGER.error("Failed to connect to KH100 hub at %s: %s", host, err)
        raise ConfigEntryNotReady(err) from err

    coordinator = KasaKe100Coordinator(
        hass,
        client,
        scan_interval_seconds=scan_seconds,
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "client": client,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    data = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if data and (client := data.get("client")):
        await client.async_close()
    return unload_ok
