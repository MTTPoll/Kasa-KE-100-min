from __future__ import annotations
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, DEFAULT_POLL_INTERVAL, PLATFORMS
from .helpers.hub import KasaMatterProxyHub

_LOGGER = logging.getLogger(__name__)

def _poll_delta(entry: ConfigEntry) -> timedelta:
    seconds = entry.options.get("poll_interval", DEFAULT_POLL_INTERVAL)
    return timedelta(seconds=seconds)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Matter-Proxy: Wir docken an bestehende Matter-Entities in HA an
    hub = KasaMatterProxyHub(hass, entry, DOMAIN)

    await hub.async_connect()
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_coordinator",
        update_method=hub.async_refresh,
        update_interval=_poll_delta(entry),
    )
    await coordinator.async_config_entry_first_refresh()

    @callback
    def _on_hub_event(updated_devices: dict):
        coordinator.async_set_updated_data(updated_devices)

    hub.add_listener(_on_hub_event)
    await hub.async_start_event_listener()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "hub": hub,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    data = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if data:
        await data["hub"].async_stop_event_listener()
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if data:
        await data["hub"].async_disconnect()
    return unload_ok
