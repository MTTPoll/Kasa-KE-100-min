from __future__ import annotations
from datetime import timedelta
from typing import Any

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import HVACMode, ClimateEntityFeature
from homeassistant.const import TEMP_CELSIUS, ATTR_TEMPERATURE

from .const import DOMAIN, MANUFACTURER, MODEL_KE100

SCAN_INTERVAL = timedelta(seconds=30)  # Entity pollt alle 30 s

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    hub = data["hub"]

    devices = await hub.async_fetch_devices()
    entities = []
    for dev_id, dev in devices.items():
        if dev.get("type") == "climate":
            entities.append(Ke100Climate(hub, dev_id, dev))
    async_add_entities(entities)

class Ke100Climate(ClimateEntity):
    _attr_has_entity_name = True
    _attr_temperature_unit = TEMP_CELSIUS
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_min_temp = 5
    _attr_max_temp = 30
    _attr_target_temperature_step = 1.0

    def __init__(self, hub, device_id: str, dev: dict) -> None:
        self._hub = hub
        self._id = device_id
        self._attr_name = dev.get("name", "KE100")
        self._unique = dev.get("unique", device_id)
        self._sw = dev.get("sw")

        # Startwerte
        self._current_temp = dev.get("current_temp")
        self._target_temp = dev.get("target_temp")
        self._hvac_action = dev.get("hvac_action")

    @property
    def unique_id(self) -> str:
        return f"{self._unique}-climate"

    @property
    def device_info(self) -> dict[str, Any]:
        return {
            "identifiers": {(DOMAIN, self._unique)},
            "manufacturer": MANUFACTURER,
            "model": MODEL_KE100,
            "name": self.name,
            "sw_version": self._sw,
        }

    @property
    def current_temperature(self) -> float | None:
        return self._current_temp

    @property
    def target_temperature(self) -> float | None:
        return self._target_temp

    @property
    def hvac_mode(self) -> HVACMode:
        return HVACMode.OFF if self._hvac_action == "off" else HVACMode.HEAT

    @property
    def hvac_action(self):
        return self._hvac_action

    async def async_update(self) -> None:
        devices = await self._hub.async_fetch_devices()
        dev = devices.get(self._id, {})
        self._current_temp = dev.get("current_temp")
        self._target_temp = dev.get("target_temp")
        self._hvac_action = dev.get("hvac_action")

    async def async_set_temperature(self, **kwargs):
        if (temp := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        temp = round(float(temp))
        await self._hub.async_set_target_temperature(self._id, temp)
        self._target_temp = temp
        self.async_write_ha_state()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        await self._hub.async_set_hvac_mode(self._id, hvac_mode)
        self._hvac_action = "off" if hvac_mode == HVACMode.OFF else "heating"
        self.async_write_ha_state()
