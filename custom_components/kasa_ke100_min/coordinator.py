from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

class KasaCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api):
        super().__init__(hass, logger=None, name="KasaCoordinator", update_interval=None)
        self.api = api

    async def _async_update_data(self):
        return await self.api.get_current_temperature()
