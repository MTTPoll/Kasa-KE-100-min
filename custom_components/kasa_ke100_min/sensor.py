
from __future__ import annotations
from typing import Any, Dict
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfTemperature, PERCENTAGE
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, MANUFACTURER
from .coordinator import KasaKe100Coordinator

def _is_t310(raw: Dict[str, Any]) -> bool:
    model = (raw.get("model") or raw.get("device_model") or "").upper()
    return "T310" in model or "T315" in model

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: KasaKe100Coordinator = data["coordinator"]

    known = set()

    def _add():
        ents = []
        for dev_id, raw in (coordinator.data.get("devices") or {}).items():
            if dev_id in known or not _is_t310(raw):
                continue
            ents.append(T310TemperatureSensor(coordinator, dev_id))
            ents.append(T310HumiditySensor(coordinator, dev_id))
            if "battery" in raw:
                ents.append(T310BatterySensor(coordinator, dev_id))
            if "rssi" in raw or "signal" in raw:
                ents.append(T310SignalSensor(coordinator, dev_id))
            known.add(dev_id)
        if ents:
            async_add_entities(ents)

    _add()
    entry.async_on_unload(coordinator.async_add_listener(_add))

class _BaseT310(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator: KasaKe100Coordinator, device_id: str) -> None:
        super().__init__(coordinator)
        self._id = device_id
        self._attr_has_entity_name = True

    def _raw(self) -> Dict[str, Any]:
        return (self.coordinator.data.get("devices") or {}).get(self._id) or {}

    @property
    def device_info(self):
        raw = self._raw()
        name = raw.get("name") or f"Tapo T310 {self._id[-4:]}"
        model = raw.get("model") or "Tapo T310"
        return {
            "identifiers": {(DOMAIN, self._id)},
            "manufacturer": MANUFACTURER,
            "model": model,
            "name": name,
        }

    @property
    def available(self) -> bool:
        return self._raw().get("online", True)

class T310TemperatureSensor(_BaseT310):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    @property
    def unique_id(self) -> str:
        return f"{self._id}_t310_temperature"

    @property
    def name(self) -> str:
        base = (self._raw().get("name") or f"T310 {self._id[-4:]}")
        return f"{base} Temperatur"

    @property
    def native_value(self):
        return self._raw().get("current_temp")

class T310HumiditySensor(_BaseT310):
    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    @property
    def unique_id(self) -> str:
        return f"{self._id}_t310_humidity"

    @property
    def name(self) -> str:
        base = (self._raw().get("name") or f"T310 {self._id[-4:]}")
        return f"{base} Luftfeuchte"

    @property
    def native_value(self):
        return self._raw().get("humidity")

class T310BatterySensor(_BaseT310):
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_entity_category = "diagnostic"

    @property
    def unique_id(self) -> str:
        return f"{self._id}_t310_battery"

    @property
    def name(self) -> str:
        base = (self._raw().get("name") or f"T310 {self._id[-4:]}")
        return f"{base} Batterie"

    @property
    def native_value(self):
        return self._raw().get("battery")

class T310SignalSensor(_BaseT310):
    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "dBm"
    _attr_entity_category = "diagnostic"

    @property
    def unique_id(self) -> str:
        return f"{self._id}_t310_signal"

    @property
    def name(self) -> str:
        base = (self._raw().get("name") or f"T310 {self._id[-4:]}")
        return f"{base} Signal"

    @property
    def native_value(self):
        raw = self._raw()
        return raw.get("rssi", raw.get("signal"))
