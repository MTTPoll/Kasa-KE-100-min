from __future__ import annotations
from datetime import timedelta
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass

from .const import DOMAIN, MANUFACTURER, MODEL_T110

SCAN_INTERVAL = timedelta(seconds=30)  # Entity pollt alle 30 s

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    hub = data["hub"]

    devices = await hub.async_fetch_devices()
    entities = []
    for dev_id, dev in devices.items():
        if dev.get("type") == "binary_sensor":
            entities.append(T110Binary(hub, dev_id, dev))
    async_add_entities(entities)

class T110Binary(BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.DOOR
    _attr_has_entity_name = True

    def __init__(self, hub, device_id: str, dev: dict) -> None:
        self._hub = hub
        self._id = device_id
        self._unique = dev.get("unique", device_id)
        self._attr_name = dev.get("name", "T110")
        self._is_open = dev.get("is_open", False)

    @property
    def unique_id(self) -> str:
        return f"{self._unique}-door"

    @property
    def device_info(self) -> dict[str, Any]:
        return {
            "identifiers": {(DOMAIN, self._unique)},
            "manufacturer": MANUFACTURER,
            "model": MODEL_T110,
            "name": self.name,
        }

    @property
    def is_on(self) -> bool | None:
        return bool(self._is_open)

    async def async_update(self) -> None:
        devices = await self._hub.async_fetch_devices()
        dev = devices.get(self._id, {})
        self._is_open = bool(dev.get("is_open"))
