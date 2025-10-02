from __future__ import annotations
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

_LOGGER = logging.getLogger(__name__)

class KasaHubClient:
    """Minimaler Hub-Client mit Dedupe/Throttle, geeignet für Entity-basiertes Polling."""

    def __init__(self, host: str):
        self._host = host
        self._devices: dict[str, Any] = {}
        self._lock = asyncio.Lock()
        self._last_fetch: datetime | None = None
        self._min_interval = timedelta(seconds=1)  # innerhalb 1 s keine zweite Hub-Abfrage

    async def async_connect(self) -> None:
        # TODO: echte Verbindung herstellen
        await asyncio.sleep(0)
        # Demo-Geräte (Beispiel)
        self._devices = {
            "ke100_1": {
                "type": "climate",
                "name": "Livingroom Radiator",
                "current_temp": 21.5,
                "target_temp": 22.0,
                "hvac_action": "idle",  # idle/heating/off
                "unique": "kh100-abcdef-ke100-1",
                "sw": "1.0.0",
            },
            "t110_1": {
                "type": "binary_sensor",
                "name": "Balcony Door",
                "is_open": False,
                "unique": "kh100-abcdef-t110-1",
                "sw": "1.2.3",
            },
        }

    async def async_disconnect(self) -> None:
        await asyncio.sleep(0)

    async def async_fetch_devices(self) -> dict[str, Any]:
        """Einmal pro Aufrufrunde die echten Werte vom Hub holen (dedupliziert)."""
        async with self._lock:
            now = datetime.now()
            if self._last_fetch and (now - self._last_fetch) < self._min_interval:
                return self._devices

            # TODO: >>> HIER echte Hub-Abfrage einbauen <<<
            # Demo: Temperatur leicht driften lassen, um Änderungen zu sehen
            dev = self._devices["ke100_1"]
            dev["current_temp"] = round(float(dev["current_temp"]) + 0.1, 1)

            self._last_fetch = now
            _LOGGER.debug("Polled KH100 @ %s (last_fetch=%s)", self._host, self._last_fetch.isoformat())
            return self._devices

    # Schreib-Operationen
    async def async_set_target_temperature(self, device_id: str, temp: float) -> None:
        # TODO: echten Hub-Call
        self._devices[device_id]["target_temp"] = temp

    async def async_set_hvac_mode(self, device_id: str, mode: str) -> None:
        # TODO: echten Hub-Call
        self._devices[device_id]["hvac_action"] = "heating" if mode == "heat" else "off"
