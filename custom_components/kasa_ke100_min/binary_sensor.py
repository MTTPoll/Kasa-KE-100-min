from __future__ import annotations
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, MANUFACTURER, MODEL_T110
from .coordinator import KasaKe100Coordinator

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: KasaKe100Coordinator = data["coordinator"]
    known = set()

    def _check_devices():
        ents = []
        for dev_id, raw in coordinator.data.get("devices", {}).items():
            # Contacts erkennen am Vorhandensein von 'is_open'
            if dev_id in known or "is_open" not in raw:
                continue
            ents.append(TapoContactEntity(coordinator, dev_id))
            known.add(dev_id)
        if ents:
            async_add_entities(ents)

    _check_devices()
    entry.async_on_unload(coordinator.async_add_listener(_check_devices))

class TapoContactEntity(CoordinatorEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.DOOR

    def __init__(self, coordinator: KasaKe100Coordinator, device_id: str) -> None:
        super().__init__(coordinator)
        self._id = device_id
        self._attr_unique_id = device_id

    @property
    def is_on(self) -> bool:
        st = self.coordinator.data.get("devices", {}).get(self._id) or {}
        return bool(st.get("is_open", False))

    @property
    def name(self) -> str:
        st = self.coordinator.data.get("devices", {}).get(self._id) or {}
        return st.get("name", f"T110 {self._id}")

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._id)},
            "manufacturer": MANUFACTURER,
            "model": MODEL_T110,
            "name": self.name,
        }
