from __future__ import annotations
import logging
from datetime import timedelta
from typing import Dict, TypedDict
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .api import KH100Client, TRV, Contact
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

class HubData(TypedDict):
    trvs: Dict[str, TRV]
    contacts: Dict[str, Contact]

class KasaCoordinator(DataUpdateCoordinator[HubData]):
    def __init__(self, hass: HomeAssistant, client: KH100Client) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name=f"{DOMAIN}_coordinator",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.client = client

    async def _async_update_data(self) -> HubData:
        trvs = await self.client.async_list_trvs()
        contacts = await self.client.async_list_contacts()
        return {
            "trvs": {t.device_id: t for t in trvs},
            "contacts": {c.device_id: c for c in contacts},
        }
