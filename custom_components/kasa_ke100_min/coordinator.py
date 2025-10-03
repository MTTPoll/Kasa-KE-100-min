from __future__ import annotations
from datetime import timedelta
import logging
from typing import Any, Dict
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from .api import KasaKe100Client

_LOGGER = logging.getLogger(__name__)

class KasaKe100Coordinator(DataUpdateCoordinator[Dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, client: KasaKe100Client, scan_interval_seconds: int | None = None) -> None:
        self.client = client
        interval = timedelta(seconds=scan_interval_seconds) if scan_interval_seconds else DEFAULT_SCAN_INTERVAL
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_coordinator",
            update_interval=interval,
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        try:
            data = await self.client.async_refresh()
            # Schlanker Debug: Anzahl Geräte + kurze Liste (id:name ist->soll hvac)
            if _LOGGER.isEnabledFor(logging.DEBUG):
                devs = data.get("devices", {})
                summary = ", ".join(
                    f"{v.get('name','?')}({k[-4:]}): {v.get('current_temp')}→{v.get('target_temp')} {v.get('hvac_mode')}/{v.get('hvac_action')}"
                    for k, v in list(devs.items())[:10]
                )
                _LOGGER.debug("Polled %d devices. %s%s",
                              len(devs),
                              summary,
                              " ..." if len(devs) > 10 else "")
            return data
        except Exception as err:
            raise UpdateFailed(err) from err
