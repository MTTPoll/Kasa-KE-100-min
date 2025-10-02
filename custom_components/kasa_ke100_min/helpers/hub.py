from __future__ import annotations
import asyncio
from typing import Any, Callable, Dict, List

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.components.climate import DOMAIN as CLIMATE_DOMAIN

from ..const import CONF_CLIMATE, CONF_CONTACTS

EventCallback = Callable[[Dict[str, Any]], None]

class KasaMatterProxyHub:
    """Proxy-Hub, der an HA-Matter-Entities andockt und pushend spiegelt."""

    def __init__(self, hass: HomeAssistant, entry, domain: str) -> None:
        self.hass = hass
        self.entry = entry
        self.domain = domain
        self._devices: Dict[str, Any] = {}
        self._listeners: List[EventCallback] = []
        self._unsub = None
        self._climate_eid: str | None = None
        self._contact_eids: list[str] = []

    # ---- Lifecycle ----
    async def async_connect(self) -> None:
        await asyncio.sleep(0)

    async def async_disconnect(self) -> None:
        await asyncio.sleep(0)

    def add_listener(self, cb: EventCallback) -> None:
        self._listeners.append(cb)

    async def async_start_event_listener(self) -> None:
        # Entity-IDs aus ConfigEntry laden
        self._climate_eid = self.entry.data.get(CONF_CLIMATE)
        contacts = self.entry.data.get(CONF_CONTACTS, "")
        self._contact_eids = [e.strip() for e in contacts.split(",") if e.strip()]

        # Initiale Spiegel-Daten
        await self._prime_state()

        # State-Events abonnieren
        entity_ids = [e for e in [self._climate_eid, *self._contact_eids] if e]
        if entity_ids:
            self._unsub = async_track_state_change_event(
                self.hass, entity_ids, self._handle_state_event
            )

    async def async_stop_event_listener(self) -> None:
        if self._unsub:
            self._unsub()
            self._unsub = None

    async def async_refresh(self) -> Dict[str, Any]:
        # Für den Coordinator: liefere aktuellen Snapshot
        return self._devices

    # ---- Writes an Matter-Entity ----
    async def async_set_target_temperature(self, device_id: str, temp: float) -> None:
        if not self._climate_eid:
            return
        await self.hass.services.async_call(
            CLIMATE_DOMAIN,
            "set_temperature",
            { "entity_id": self._climate_eid, ATTR_TEMPERATURE: float(round(temp)) },
            blocking=True,
        )

    async def async_set_hvac_mode(self, device_id: str, mode: str) -> None:
        if not self._climate_eid:
            return
        await self.hass.services.async_call(
            CLIMATE_DOMAIN,
            "set_hvac_mode",
            { "entity_id": self._climate_eid, "hvac_mode": mode },
            blocking=True,
        )

    # ---- Helpers ----
    async def _prime_state(self) -> None:
        # Climate
        if self._climate_eid:
            st = self.hass.states.get(self._climate_eid)
            if st:
                dev_id = "ke100_proxy"
                self._devices[dev_id] = {
                    "type": "climate",
                    "name": st.attributes.get("friendly_name", "KE100"),
                    "current_temp": st.attributes.get("current_temperature"),
                    "target_temp": st.attributes.get("temperature"),
                    "hvac_action": st.attributes.get("hvac_action"),  # heating/idle/off
                    "unique": self._climate_eid,
                    "sw": None,
                }
        # Contacts
        for idx, eid in enumerate(self._contact_eids, start=1):
            st = self.hass.states.get(eid)
            if st:
                dev_id = f"t110_proxy_{idx}"
                self._devices[dev_id] = {
                    "type": "binary_sensor",
                    "name": st.attributes.get("friendly_name", f"Contact {idx}"),
                    "is_open": st.state == "on",  # binary_sensor on=open
                    "unique": eid,
                    "sw": None,
                }

    @callback
    def _handle_state_event(self, event) -> None:
        new_state = event.data.get("new_state")
        if not new_state:
            return
        eid = new_state.entity_id

        updated = False
        # Climate?
        if eid == self._climate_eid and "ke100_proxy" in self._devices:
            d = self._devices["ke100_proxy"]
            d["current_temp"] = new_state.attributes.get("current_temperature")
            d["target_temp"]  = new_state.attributes.get("temperature")
            d["hvac_action"]  = new_state.attributes.get("hvac_action")
            updated = True

        # Contacts?
        for dev_id, dev in self._devices.items():
            if dev.get("type") == "binary_sensor" and dev.get("unique") == eid:
                dev["is_open"] = new_state.state == "on"
                updated = True

        if updated:
            for cb in self._listeners:
                cb(self._devices)
