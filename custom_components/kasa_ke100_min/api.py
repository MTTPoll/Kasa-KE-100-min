from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional

from kasa import Discover, Module  # python-kasa

@dataclass
class TRV:
    device_id: str
    name: str
    current_temperature: float | None
    target_temperature: float | None

@dataclass
class Contact:
    device_id: str
    name: str
    is_open: bool

class KH100Client:
    def __init__(self, host: str, username: str | None = None, password: str | None = None) -> None:
        self._host = host
        self._username = username
        self._password = password
        self._connected = False
        self._hub = None
        self._trvs: Dict[str, TRV] = {}
        self._contacts: Dict[str, Contact] = {}

    async def async_connect(self) -> None:
        self._hub = await Discover.discover_single(
            self._host,
            username=self._username,
            password=self._password,
        )
        await self._hub.update()
        self._connected = True
        await self._refresh_children()

    async def async_close(self) -> None:
        self._connected = False
        self._hub = None

    @property
    def connected(self) -> bool:
        return self._connected

    async def _refresh_children(self) -> None:
        self._trvs.clear()
        self._contacts.clear()
        children = []
        if hasattr(self._hub, "children") and self._hub.children:
            children = self._hub.children
        for child in children:
            await child.update()
            devid = getattr(child, "device_id", getattr(child, "mac", child.alias))
            name = getattr(child, "alias", devid)
            thermo = child.modules.get(Module.Thermostat)
            if thermo is not None:
                cur = getattr(thermo, "current_temperature", None)
                tgt = getattr(thermo, "target_temperature", None)
                self._trvs[devid] = TRV(devid, name, cur, tgt)
                continue
            contact_mod = child.modules.get(getattr(Module, "ContactSensor", None))
            if contact_mod is not None:
                is_open = bool(getattr(contact_mod, "is_open", False))
                self._contacts[devid] = Contact(devid, name, is_open)

    async def async_list_trvs(self) -> List[TRV]:
        await self._refresh_children()
        return list(self._trvs.values())

    async def async_get_trv(self, device_id: str) -> Optional[TRV]:
        await self._refresh_children()
        return self._trvs.get(device_id)

    async def async_set_target_temperature(self, device_id: str, temperature: float) -> None:
        t_int = int(round(float(temperature)))
        for child in (self._hub.children or []):
            cid = getattr(child, "device_id", getattr(child, "mac", child.alias))
            if cid == device_id:
                thermo = child.modules.get(Module.Thermostat)
                if thermo:
                    if hasattr(thermo, "set_target_temperature"):
                        await thermo.set_target_temperature(t_int)
                    elif hasattr(thermo, "set_temperature"):
                        await thermo.set_temperature(t_int)
                await child.update()
        await self._refresh_children()

    async def async_list_contacts(self) -> List[Contact]:
        await self._refresh_children()
        return list(self._contacts.values())

    async def async_get_contact(self, device_id: str) -> Optional[Contact]:
        await self._refresh_children()
        return self._contacts.get(device_id)
