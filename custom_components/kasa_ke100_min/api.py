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
    def _derive_hvac_action(cur: float | None, tgt: float | None, explicit_heating: Optional[bool] = None) -> str:
        if isinstance(explicit_heating, bool):
            return "heating" if explicit_heating else "idle"
        if cur is None or tgt is None:
            return "idle"
        try:
            return "heating" if float(cur) < float(tgt) else "idle"
        except Exception:
            return "idle"

    @staticmethod
    def _get_module(modules: Any, key: Any, alt_key: Optional[str] = None):
        """Robuster Zugriff: Module können per Enum-Schlüssel oder per String benannt sein."""
        if not modules:
            return None
        # Dict-artig?
        if hasattr(modules, "get"):
            # 1) direkter key (Enum)
            mod = modules.get(key)
            if mod is not None:
                return mod
            # 2) alternativer String-Name
            if alt_key is not None:
                mod = modules.get(alt_key)
                if mod is not None:
                    return mod
            # 3) string keys (fallback): vergleiche Name-case-insensitiv
            try:
                for k, v in modules.items():
                    ks = str(k).lower()
                    if alt_key and ks == alt_key.lower():
                        return v
                    if hasattr(key, "name") and ks == str(key.name).lower():
                        return v
            except Exception:
                pass
        return None

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
                # Debug: zeige Modulnamen (einmalig pro Gerät)
                try:
                    mod_keys = list(modules.keys()) if hasattr(modules, "keys") else str(type(modules))
                    _LOGGER.debug("Child %s modules: %s", dev_id, mod_keys)
                except Exception:
                    pass

                # 1) Thermostat / TRV (Enum oder String)
                thermo = self._get_module(modules, getattr(self._Module, "Thermostat", None), "Thermostat")
                # 2) TemperatureSensor als Fallback für current_temp
                temp_mod = self._get_module(modules, getattr(self._Module, "TemperatureSensor", None), "TemperatureSensor")
                # 3) ContactSensor
                contact = self._get_module(modules, getattr(self._Module, "ContactSensor", None), "ContactSensor")

                if thermo is not None or temp_mod is not None:
                    # Current Temperature
                    cur = None
                    if thermo is not None:
                        cur = getattr(thermo, "current_temperature", None)
                        if cur is None:
                            cur = getattr(thermo, "temperature", None)
                    if cur is None and temp_mod is not None:
                        cur = getattr(temp_mod, "current_temperature", None) or getattr(temp_mod, "temperature", None)

                    # Target Temperature
                    tgt = None
                    if thermo is not None:
                        tgt = getattr(thermo, "target_temperature", None) or getattr(thermo, "setpoint", None)
                    if tgt is None:
                        # Manche Firmwares exposen das Setpoint am Child selbst
                        for attr in ("target_temperature", "setpoint", "target_temp"):
                            tgt = getattr(child, attr, None)
                            if tgt is not None:
                                break

                    # HVAC Action
                    explicit_heating = getattr(thermo, "heating", None) if thermo is not None else None
                    hvac_action = self._derive_hvac_action(cur, tgt, explicit_heating)

                    # Battery (best effort)
                    battery = getattr(child, "battery", None)
                    if battery is None and thermo is not None:
                        battery = getattr(thermo, "battery", None)
                    if battery is None and temp_mod is not None:
                        battery = getattr(temp_mod, "battery", None)

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

                # Unbekannt – loggen
                _LOGGER.debug("Unknown child modules for %s: %s", dev_id, list(modules) if hasattr(modules, "keys") else modules)

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
            thermo = self._get_module(modules, getattr(self._Module, "Thermostat", None), "Thermostat")

            if thermo is not None:
                setter = getattr(thermo, "set_target_temperature", None) or getattr(thermo, "set_temperature", None)
                if setter is None:
                    raise RuntimeError("Thermostat module has no setter for target temperature")
                await setter(float(temperature))
                return

            # Fallback: falls kein Thermostat-Modul existiert, versuche generisch
            if hasattr(child, "set_target_temperature"):
                await child.set_target_temperature(float(temperature))
                return
            raise RuntimeError("No way to set target temperature on this device")
