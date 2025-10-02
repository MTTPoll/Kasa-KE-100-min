from homeassistant.components.binary_sensor import BinarySensorEntity
from .const import DOMAIN

class T110Sensor(BinarySensorEntity):
    def __init__(self, name, api):
        self._attr_name = name
        self._api = api
        self._attr_is_on = False

    async def async_update(self):
        self._attr_is_on = await self._api.is_open()
