from __future__ import annotations
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD

from .const import DOMAIN, PLATFORMS
from .helpers.hub import KasaHubClient

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    host = entry.data.get(CONF_HOST)
    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)
    if not host or not username or not password:
        raise ConfigEntryNotReady("Missing host/username/password")

    hub = KasaHubClient(host, username, password)
    await hub.async_connect()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"hub": hub}
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    data = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if data:
        await data["hub"].async_disconnect()
    return unload_ok
