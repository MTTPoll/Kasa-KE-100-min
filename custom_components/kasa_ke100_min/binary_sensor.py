from __future__ import annotations
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, MANUFACTURER, MODEL_KE100
from .coordinator import KasaKe100Coordinator

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: KasaKe100Coordinator = data["coordinator"]

    known = set()
    def _check_devices():
        ents = []
        for dev_id, raw in coordinator.data.get("devices", {}).items():
            if dev_id in known or "is_open" not in raw:
                continue
            ents.append(KeContactEntity(coordinator, dev_id))
            known.add(dev_id)
        if ents:
            async_add_entities(ents)
    _check_devices()
    entry.async_on_unload(coordinator.async_add_listener(_check_devices))

class KeContactEntity(CoordinatorEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.WINDOW

    def __init__(self, coordinator: KasaKe100Coordinator, device_id: str) -> None:
        super().__init__(coordinator)
        self._id = device_id
        self._attr_unique_id = f"{device_id}_contact"

    @property
    def _st(self):
        return self.coordinator.data.get("devices", {}).get(self._id) or {}

    @property
    def name(self) -> str:
        return self._st.get("name") or f"KE100 Contact {self._id}"

    @property
    def is_on(self) -> bool | None:
        val = self._st.get("is_open")
        return bool(val) if val is not None else None

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._id)},
            "manufacturer": MANUFACTURER,
            "model": MODEL_KE100,
            "name": self.name,
        }

    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()
