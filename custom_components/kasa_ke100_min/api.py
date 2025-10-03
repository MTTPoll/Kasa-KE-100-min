from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Optional, Any
import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

# ---- Datenmodelle ----

@dataclass
class TRVState:
    device_id: str
    name: str
    current_temp: float | None
    target_temp: float | None
    hvac_action: str  # "heating" | "idle" | "off"
    battery: int | None
    online: bool = True

@dataclass
class ContactState:
    device_id: str
    name: str
    is_open: bool
    battery: int | None
    online: bool = True

class KasaKe100Client:
    """Client kapselt KH100 Hub-Kommunikation über python-kasa (lazy import)."""

    def __init__(self, host: str, username: str | None = None, password: str | None = None) -> None:
        self._host = host
        self._username = username
        self._password = password
        self._lock = asyncio.Lock()
        self._hub = None
        self._connected = False
        self._devices: Dict[str, TRVState | ContactState] = {}
        self._child_by_id: Dict[str, Any] = {}
        self._Module = None  # wird nach lazy-import gesetzt

    # -------- Verbindung --------

    async def async_connect(self) -> None:
        async with self._lock:
            if self._connected and self._hub is not None:
                return
            # Lazy import, damit Requirements bereits installiert sind
            try:
                from kasa import Discover, Module  # type: ignore
            except Exception as e:
                raise RuntimeError("python-kasa ist nicht installiert oder fehlerhaft.") from e
            self._Module = Module

            self._hub = await Discover.discover_single(
                self._host,
                username=self._username,
                password=self._password,
            )
            if self._hub is None:
                raise RuntimeError(f"Cannot discover KH100 hub at {self._host}")
            self._connected = True
            _LOGGER.debug("Connected to KH100 hub at %s", self._host)

    async def async_close(self) -> None:
        async with self._lock:
            self._connected = False
            self._hub = None
            self._child_by_id.clear()

    # -------- Hilfen --------

    @staticmethod
    def _derive_device_id(dev) -> str:
        for attr in ("device_id", "id", "mac", "alias", "host"):
            val = getattr(dev, attr, None)
            if val:
                return str(val)
        return hex(id(dev))

    @staticmethod
    def _derive_hvac_action(thermo) -> str:
        heating = getattr(thermo, "heating", None)
        if isinstance(heating, bool):
            return "heating" if heating else "idle"
        cur = getattr(thermo, "current_temperature", None)
        tgt = getattr(thermo, "target_temperature", None)
        if cur is None or tgt is None:
            return "idle"
        try:
            return "heating" if float(cur) < float(tgt) else "idle"
        except Exception:
            return "idle"

    # -------- Poll --------

    async def async_refresh(self) -> Dict[str, Dict[str, Any]]:
        await self.async_connect()
        async with self._lock:
            await self._hub.update()

            devices: Dict[str, TRVState | ContactState] = {}
            self._child_by_id.clear()

            for child in getattr(self._hub, "children", []):
                try:
                    await child.update()
                except Exception as e:
                    _LOGGER.warning("Child update failed: %s", e)

                dev_id = self._derive_device_id(child)
                self._child_by_id[dev_id] = child
                name = getattr(child, "alias", None) or getattr(child, "name", None) or f"Device {dev_id}"

                modules = getattr(child, "modules", {}) or {}
                # Thermostat / TRV
                thermo = modules.get(self._Module.Thermostat) if isinstance(modules, dict) else None
                if thermo is not None:
                    cur = getattr(thermo, "current_temperature", None)
                    tgt = getattr(thermo, "target_temperature", None)
                    hvac_action = self._derive_hvac_action(thermo)
                    battery = getattr(child, "battery", None) or getattr(thermo, "battery", None)
                    devices[dev_id] = TRVState(
                        device_id=dev_id,
                        name=name,
                        current_temp=cur,
                        target_temp=tgt,
                        hvac_action=hvac_action,
                        battery=battery,
                        online=True,
                    )
                    continue

                # Contact Sensor (T110)
                contact_cls = getattr(self._Module, "ContactSensor", None)
                contact = modules.get(contact_cls) if isinstance(modules, dict) and contact_cls else None
                if contact is not None:
                    is_open = bool(getattr(contact, "is_open", False))
                    battery = getattr(child, "battery", None) or getattr(contact, "battery", None)
                    devices[dev_id] = ContactState(
                        device_id=dev_id,
                        name=name,
                        is_open=is_open,
                        battery=battery,
                        online=True,
                    )
                    continue

                _LOGGER.debug("Unknown child modules for %s: %s", dev_id, list(modules) if isinstance(modules, dict) else modules)

            self._devices = devices
            out: Dict[str, Any] = {"devices": {}}
            for dev_id, st in self._devices.items():
                out["devices"][dev_id] = asdict(st)
            return out

    # -------- Write-APIs --------

    def _get_child(self, device_id: str):
        dev = self._child_by_id.get(device_id)
        if dev is None and self._hub is not None:
            for child in getattr(self._hub, "children", []):
                if self._derive_device_id(child) == device_id:
                    self._child_by_id[device_id] = child
                    return child
        return dev

    async def async_set_target_temp(self, device_id: str, temperature: float) -> None:
        async with self._lock:
            child = self._get_child(device_id)
            if child is None:
                raise ValueError(f"Device {device_id} not found")
            modules = getattr(child, "modules", {}) or {}
            thermo = modules.get(self._Module.Thermostat) if isinstance(modules, dict) else None
            if thermo is None:
                raise ValueError(f"Device {device_id} is not a TRV")
            setter = getattr(thermo, "set_target_temperature", None) or getattr(thermo, "set_temperature", None)
            if setter is None:
                raise RuntimeError("Thermostat module has no setter for target temperature")
            await setter(float(temperature))

    async def async_set_state(self, device_id: str, on: bool) -> None:
        async with self._lock:
            child = self._get_child(device_id)
            if child is None:
                raise ValueError(f"Device {device_id} not found")
            modules = getattr(child, "modules", {}) or {}
            thermo = modules.get(self._Module.Thermostat) if isinstance(modules, dict) else None
            if thermo is None:
                raise ValueError(f"Device {device_id} is not a TRV")
            if hasattr(thermo, "set_power"):
                await thermo.set_power(on)
            elif hasattr(thermo, "set_mode"):
                await thermo.set_mode("heat" if on else "off")
            else:
                raise RuntimeError("Thermostat module has no power/mode setter; implement device-specific handling")
