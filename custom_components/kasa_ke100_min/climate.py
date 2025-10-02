from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import HVACMode, ClimateEntityFeature
from homeassistant.const import UnitOfTemperature, ATTR_TEMPERATURE
from .const import DOMAIN

class KE100Climate(ClimateEntity):
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_min_temp = 5
    _attr_max_temp = 30

    def __init__(self, name, api):
        self._attr_name = name
        self._api = api
        self._attr_hvac_mode = HVACMode.OFF
        self._attr_target_temperature = 20
        self._attr_current_temperature = 20

    async def async_set_temperature(self, **kwargs):
        if (temp := kwargs.get(ATTR_TEMPERATURE)) is not None:
            await self._api.set_target_temperature(int(temp))
            self._attr_target_temperature = int(temp)
            self.async_write_ha_state()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode):
        self._attr_hvac_mode = hvac_mode
        self.async_write_ha_state()

    async def async_update(self):
        self._attr_current_temperature = await self._api.get_current_temperature()
