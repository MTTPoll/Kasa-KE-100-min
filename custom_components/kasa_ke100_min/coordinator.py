from __future__ import annotations
import logging
from typing import Dict, Any, Optional
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

class KasaKe100Coordinator(DataUpdateCoordinator[Dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, client: KasaKe100Client, scan_interval_seconds: Optional[int] = None) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_coordinator",
            update_interval=timedelta(seconds=scan_interval_seconds) if scan_interval_seconds else DEFAULT_SCAN_INTERVAL,
        )
        self.client = client

    async def _async_update_data(self) -> Dict[str, Any]:
        try:
            data = await self.client.async_refresh()
            if not isinstance(data, dict) or "devices" not in data:
                raise UpdateFailed("Invalid data from hub")
            return data
        except Exception as err:
            raise UpdateFailed(f"Error updating from hub: {err}") from err
