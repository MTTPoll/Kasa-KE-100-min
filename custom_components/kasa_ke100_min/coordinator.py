
from __future__ import annotations
from datetime import timedelta
from typing import Any, Dict, Optional
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from .api import KasaKe100Client

class KasaKe100Coordinator(DataUpdateCoordinator[Dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, client: KasaKe100Client, scan_interval_seconds: Optional[int] = None) -> None:
        self.client = client
        interval = timedelta(seconds=scan_interval_seconds) if scan_interval_seconds else DEFAULT_SCAN_INTERVAL
        super().__init__(
            hass,
            logging.getLogger(__name__),  # valid logger object
            name=f"{DOMAIN}_coordinator",
            update_interval=interval,
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        try:
            return await self.client.async_refresh()
        except Exception as err:
            raise UpdateFailed(err) from err
