from __future__ import annotations
from typing import Any
import logging

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import HVACMode, ClimateEntityFeature
from homeassistant.const import TEMP_CELSIUS, ATTR_TEMPERATURE
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL_KE100

_LOGGER = logging.getLogger(__name__)

HVAC_MODES = [HVACMode.HEAT, HVACMode.OFF]

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    hub = data["hub"]
    coordinator = data["coordinator"]

    devices = await hub.async_refresh()
    entities = []
    for dev_id, dev in devices.items():
        if dev.get("type") == "climate":
            entities.append(Ke100Climate(coordinator, hub, dev_id))
    async_add_entities(entities)

class Ke100Climate(CoordinatorEntity, ClimateEntity):
    _attr_has_entity_name = True
    _attr_temperature_unit = TEMP_CELSIUS
    _attr_hvac_modes = HVAC_MODES
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_min_temp = 5
    _attr_max_temp = 30
    _attr_target_temperature_step = 1.0

    def __init__(self, coordinator, hub, device_id: str) -> None:
        super().__init__(coordinator)
        self._hub = hub
        self._id = device_id
        dev = coordinator.data.get(device_id, {})
        self._attr_name = dev.get("name", "KE100")
        self._unique = dev.get("unique", device_id)
        self._sw = dev.get("sw")

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
    def available(self) -> bool:
        return True

    @property
    def current_temperature(self) -> float | None:
        return self.coordinator.data[self._id].get("current_temp")

    @property
    def target_temperature(self) -> float | None:
        return self.coordinator.data[self._id].get("target_temp")

    @property
    def hvac_mode(self) -> HVACMode:
        action = self.coordinator.data[self._id].get("hvac_action")
        return HVACMode.OFF if action == "off" else HVACMode.HEAT

    @property
    def hvac_action(self):
        return self.coordinator.data[self._id].get("hvac_action")

    async def async_set_temperature(self, **kwargs):
        if (temp := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        temp = round(float(temp))
        await self._hub.async_set_target_temperature(self._id, temp)
        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        await self._hub.async_set_hvac_mode(self._id, hvac_mode)
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()
