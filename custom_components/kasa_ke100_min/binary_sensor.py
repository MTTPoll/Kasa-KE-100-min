from __future__ import annotations
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, MANUFACTURER, MODEL_T110
from .coordinator import KasaCoordinator

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: KasaCoordinator = data["coordinator"]
    entities = [T110BinarySensor(coordinator, dev_id) for dev_id in coordinator.data["contacts"]]
    async_add_entities(entities)

class T110BinarySensor(CoordinatorEntity[KasaCoordinator], BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.DOOR
    _attr_has_entity_name = True
    _attr_icon = "mdi:window-closed-variant"

    def __init__(self, coordinator: KasaCoordinator, device_id: str) -> None:
        super().__init__(coordinator)
        self._id = device_id
        self._attr_unique_id = f"{device_id}_contact"

    @property
    def name(self) -> str | None:
        contact = self.coordinator.data["contacts"].get(self._id)
        return contact.name if contact else None

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data["contacts"][self._id].is_open

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(identifiers={(DOMAIN, self._id)}, manufacturer=MANUFACTURER, model=MODEL_T110, name=self.name)
