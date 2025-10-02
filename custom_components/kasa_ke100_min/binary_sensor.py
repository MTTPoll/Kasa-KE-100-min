from __future__ import annotations
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL_T110

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    hub = data["hub"]

    devices = await hub.async_refresh()
    entities = []
    for dev_id, dev in devices.items():
        if dev.get("type") == "binary_sensor":
            entities.append(T110Binary(coordinator, dev_id, dev))
    async_add_entities(entities)

class T110Binary(CoordinatorEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.DOOR
    _attr_has_entity_name = True

    def __init__(self, coordinator, device_id: str, dev: dict) -> None:
        super().__init__(coordinator)
        self._id = device_id
        self._unique = dev.get("unique", device_id)
        self._attr_name = dev.get("name", "T110")

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
        return bool(self.coordinator.data[self._id].get("is_open"))
