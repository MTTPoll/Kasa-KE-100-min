from __future__ import annotations
from datetime import timedelta
from typing import Any, Dict, Optional
import logging, time
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from .api import KasaKe100Client

_LOGGER = logging.getLogger(__name__)

class KasaKe100Coordinator(DataUpdateCoordinator[Dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, client: KasaKe100Client, scan_interval_seconds: Optional[int] = None) -> None:
        self.client = client
        interval = timedelta(seconds=scan_interval_seconds) if scan_interval_seconds else DEFAULT_SCAN_INTERVAL
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_coordinator",
            update_interval=interval,
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        t0 = time.monotonic()
        try:
            data = await self.client.async_refresh()
        except Exception as err:
            raise UpdateFailed(err) from err

        # Pretty one-line summary for TRVs
        devs = data.get("devices", {})
        parts = []
        count = 0
        for dev_id, d in devs.items():
            if "target_temp" not in d:
                continue
            count += 1
            name = d.get("name") or dev_id
            cur = d.get("current_temp")
            tgt = d.get("target_temp")
            mode = d.get("hvac_mode")
            action = d.get("hvac_action")
            sfx = dev_id[-4:]
            parts.append(f"{name}({sfx}): {cur}→{tgt} {mode}/{action}")
        if parts:
            _LOGGER.debug("Polled %d devices. %s ...", count, ", ".join(parts[:10]))
        _LOGGER.debug("Finished fetching %s data in %.3f seconds (success: True)", self.name, time.monotonic() - t0)
        return data
