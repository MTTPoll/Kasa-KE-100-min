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
        if self._hub is None:
            self._connected = False
            return
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
        if self._hub is None:
            return
        children = []
        try:
            if getattr(self._hub, "children", None):
                children = self._hub.children
        except Exception:
            children = []

        for child in children or []:
            try:
                await child.update()
            except Exception:
                continue
            devid = getattr(child, "device_id", getattr(child, "mac", getattr(child, "alias", "unknown")))
            name = getattr(child, "alias", devid)

            thermo = None
            try:
                thermo = child.modules.get(Module.Thermostat) if getattr(child, "modules", None) else None
            except Exception:
                thermo = None

            if thermo is not None:
                cur = getattr(thermo, "current_temperature", None)
                tgt = getattr(thermo, "target_temperature", None)
                self._trvs[devid] = TRV(devid, name, cur, tgt)
                continue

            contact_mod = None
            try:
                contact_mod = child.modules.get(getattr(Module, "ContactSensor", None)) if getattr(child, "modules", None) else None
            except Exception:
                contact_mod = None
            if contact_mod is not None:
                is_open = bool(getattr(contact_mod, "is_open", False))
                self._contacts[devid] = Contact(devid, name, is_open)
                continue

            # Fallback features
            is_open_val: Optional[bool] = None
            try:
                for feat in (child.features or {}).values():
                    fid = str(getattr(feat, "id", "")).lower()
                    fname = str(getattr(feat, "name", "")).lower()
                    if any(k in fid or k in fname for k in ("contact", "open", "door", "window")):
                        try:
                            is_open_val = bool(getattr(feat, "value"))
                            break
                        except Exception:
                            pass
            except Exception:
                pass
            if is_open_val is not None:
                self._contacts[devid] = Contact(devid, name, is_open_val)

    async def async_list_trvs(self) -> List[TRV]:
        await self._refresh_children()
        return list(self._trvs.values())

    async def async_get_trv(self, device_id: str) -> Optional[TRV]:
        await self._refresh_children()
        return self._trvs.get(device_id)

    async def async_set_target_temperature(self, device_id: str, temperature: float) -> None:
        if self._hub is None:
            return
        t_int = int(round(float(temperature)))
        target_child = None
        try:
            for child in (self._hub.children or []):
                cid = getattr(child, "device_id", getattr(child, "mac", getattr(child, "alias", "")))
                if cid == device_id:
                    target_child = child
                    break
        except Exception:
            target_child = None

        if target_child is None:
            await self._refresh_children()
            try:
                for child in (self._hub.children or []):
                    cid = getattr(child, "device_id", getattr(child, "mac", getattr(child, "alias", "")))
                    if cid == device_id:
                        target_child = child
                        break
            except Exception:
                target_child = None

        if target_child is None:
            return

        thermo = None
        try:
            thermo = target_child.modules.get(Module.Thermostat) if getattr(target_child, "modules", None) else None
        except Exception:
            thermo = None
        if thermo is None:
            return

        if hasattr(thermo, "set_target_temperature"):
            await thermo.set_target_temperature(t_int)
        elif hasattr(thermo, "set_temperature"):
            await thermo.set_temperature(t_int)

        try:
            await target_child.update()
        except Exception:
            pass
        await self._refresh_children()

    async def async_list_contacts(self) -> List[Contact]:
        await self._refresh_children()
        return list(self._contacts.values())

    async def async_get_contact(self, device_id: str) -> Optional[Contact]:
        await self._refresh_children()
        return self._contacts.get(device_id)
