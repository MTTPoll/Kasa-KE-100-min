from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

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

def _to_float(val: Any) -> float | None:
    try:
        if val is None:
            return None
        return float(val)
    except Exception:
        return None

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
                # Robust extraction for current & target temperature
                cur = _to_float(getattr(thermo, "current_temperature", None))
                if cur is None:
                    cur = _to_float(getattr(thermo, "temperature", None))
                if cur is None and getattr(child, "features", None):
                    for feat in child.features.values():
                        fid = str(getattr(feat, "id", "")).lower()
                        fname = str(getattr(feat, "name", "")).lower()
                        if "temperature" in fid or "temperature" in fname:
                            cur = _to_float(getattr(feat, "value", None))
                            if cur is not None:
                                break

                tgt = _to_float(getattr(thermo, "target_temperature", None))
                if tgt is None:
                    tgt = _to_float(getattr(thermo, "setpoint", None))
                if tgt is None and getattr(child, "features", None):
                    for feat in child.features.values():
                        fid = str(getattr(feat, "id", "")).lower()
                        fname = str(getattr(feat, "name", "")).lower()
                        if any(k in fid or k in fname for k in ("target_temperature","setpoint","targettemp","desired_temp")):
                            tgt = _to_float(getattr(feat, "value", None))
                            if tgt is not None:
                                break

                self._trvs[devid] = TRV(devid, name, cur, tgt)
                continue

            # Contact sensor
            contact_mod = None
            try:
                contact_mod = child.modules.get(getattr(Module, "ContactSensor", None)) if getattr(child, "modules", None) else None
            except Exception:
                contact_mod = None
            if contact_mod is not None:
                is_open = bool(getattr(contact_mod, "is_open", False))
                self._contacts[devid] = Contact(devid, name, is_open)
                continue

            # Fallback features for contacts
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
                            pass\n            except Exception:\n                pass\n            if is_open_val is not None:\n                self._contacts[devid] = Contact(devid, name, is_open_val)\n\n    async def async_list_trvs(self) -> List[TRV]:\n        await self._refresh_children()\n        return list(self._trvs.values())\n\n    async def async_get_trv(self, device_id: str) -> Optional[TRV]:\n        await self._refresh_children()\n        return self._trvs.get(device_id)\n\n    async def async_set_target_temperature(self, device_id: str, temperature: float) -> None:\n        if self._hub is None:\n            return\n        t_int = int(round(float(temperature)))\n        target_child = None\n        try:\n            for child in (self._hub.children or []):\n                cid = getattr(child, \"device_id\", getattr(child, \"mac\", getattr(child, \"alias\", \"\")))\n                if cid == device_id:\n                    target_child = child\n                    break\n        except Exception:\n            target_child = None\n\n        if target_child is None:\n            await self._refresh_children()\n            try:\n                for child in (self._hub.children or []):\n                    cid = getattr(child, \"device_id\", getattr(child, \"mac\", getattr(child, \"alias\", \"\")))\n                    if cid == device_id:\n                        target_child = child\n                        break\n            except Exception:\n                target_child = None\n\n        if target_child is None:\n            return\n\n        thermo = None\n        try:\n            thermo = target_child.modules.get(Module.Thermostat) if getattr(target_child, \"modules\", None) else None\n        except Exception:\n            thermo = None\n        if thermo is None:\n            return\n\n        if hasattr(thermo, \"set_target_temperature\"):\n            await thermo.set_target_temperature(t_int)\n        elif hasattr(thermo, \"set_temperature\"):\n            await thermo.set_temperature(t_int)\n\n        try:\n            await target_child.update()\n        except Exception:\n            pass\n        await self._refresh_children()\n\n    async def async_list_contacts(self) -> List[Contact]:\n        await self._refresh_children()\n        return list(self._contacts.values())\n\n    async def async_get_contact(self, device_id: str) -> Optional[Contact]:\n        await self._refresh_children()\n        return self._contacts.get(device_id)\n