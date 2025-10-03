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
    hvac_mode: str           # "heat" | "off"
    hvac_action: str         # "heating" | "idle" | "off"
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
    def _get_attr_any(obj, names: list[str], default=None):
        for n in names:
            if hasattr(obj, n):
                try:
                    return getattr(obj, n)
                except Exception:
                    continue
        return default

    @staticmethod
    def _norm_power(*candidates: Any) -> Optional[bool]:
        """Normalisiert Power/Modus-Infos aus mehreren Quellen.
        - Modus-Strings 'off' → False
        - Strings 'off/false/0/disabled' → False
        - Bool/Int → bool
        - Nichts verwertbares → None
        """
        for val in candidates:
            if val is None:
                continue
            # mode strings
            if isinstance(val, str):
                s = val.strip().lower()
                if s == "off":
                    return False
                if s in ("on", "heat", "heating", "manual", "auto", "schedule"):
                    return True
                if s in ("false", "0", "disabled", "standby"):
                    return False
                # unbekannt → weiter
                continue
            if isinstance(val, (bool, int)):
                return bool(val)
        return None

    @staticmethod
    def _derive_actions(cur: float | None, tgt: float | None, explicit_heating: Optional[bool], power_on: Optional[bool]) -> tuple[str,str]:
        """Ermittelt (hvac_mode, hvac_action) ohne Fenster-Logik.
        Konservativ: Nur 'heating', wenn explizites Flag True ist.
        """
        if power_on is False:
            return ("off", "off")
        if explicit_heating is True:
            return ("heat", "heating")
        if explicit_heating is False:
            return ("heat", "idle")
        if power_on is True:
            return ("heat", "idle")
        # Unbekannt → konservativ
        return ("heat", "idle")

    @staticmethod
    def _get_module(modules: Any, key: Any, alt_key: Optional[str] = None):
        if not modules:
            return None
        if hasattr(modules, "get"):
            mod = modules.get(key)
            if mod is not None:
                return mod
            if alt_key is not None:
                mod = modules.get(alt_key)
                if mod is not None:
                    return mod
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
                try:
                    mod_keys = list(modules.keys()) if hasattr(modules, "keys") else str(type(modules))
                    _LOGGER.debug("Child %s modules: %s", dev_id, mod_keys)
                except Exception:
                    pass

                # Module
                thermo = self._get_module(modules, getattr(self._Module, "Thermostat", None), "Thermostat")
                temp_mod = self._get_module(modules, getattr(self._Module, "TemperatureSensor", None), "TemperatureSensor")
                device_mod = self._get_module(modules, getattr(self._Module, "DeviceModule", None), "DeviceModule")
                contact = self._get_module(modules, getattr(self._Module, "ContactSensor", None), "ContactSensor")

                if thermo is not None or temp_mod is not None:
                    # Ist-Temp
                    cur = self._get_attr_any(thermo, ["current_temperature", "temperature"]) if thermo is not None else None
                    if cur is None:
                        cur = self._get_attr_any(temp_mod, ["current_temperature", "temperature"]) if temp_mod is not None else None

                    # Soll-Temp
                    tgt = self._get_attr_any(thermo, ["target_temperature", "setpoint"]) if thermo is not None else None
                    if tgt is None:
                        tgt = self._get_attr_any(child, ["target_temperature", "setpoint", "target_temp"])

                    # Power / Mode / explicit heating (ohne Fensterlogik)
                    power_on = self._norm_power(
                        self._get_attr_any(thermo, ["is_on", "power", "enabled", "active", "on"]),
                        self._get_attr_any(thermo, ["mode"]),
                        self._get_attr_any(device_mod, ["is_on", "power", "enabled", "active", "on"]),
                        self._get_attr_any(device_mod, ["mode"]),
                        self._get_attr_any(child, ["is_on", "power", "enabled", "active", "on", "mode"]),
                    )

                    explicit_heating = self._get_attr_any(thermo, ["heating", "is_heating", "heating_active", "heat_on"])

                    hvac_mode, hvac_action = self._derive_actions(cur, tgt, explicit_heating, power_on)

                    battery = self._get_attr_any(child, ["battery"])
                    if battery is None and thermo is not None:
                        battery = self._get_attr_any(thermo, ["battery"])
                    if battery is None and temp_mod is not None:
                        battery = self._get_attr_any(temp_mod, ["battery"])

                    devices[dev_id] = TRVState(
                        device_id=dev_id,
                        name=name,
                        current_temp=cur,
                        target_temp=tgt,
                        hvac_mode=hvac_mode,
                        hvac_action=hvac_action,
                        battery=battery,
                        online=True,
                    )
                    continue

                if contact is not None:
                    is_open = bool(self._get_attr_any(contact, ["is_open"], False))
                    battery = self._get_attr_any(child, ["battery"]) or self._get_attr_any(contact, ["battery"])
                    devices[dev_id] = ContactState(
                        device_id=dev_id,
                        name=name,
                        is_open=is_open,
                        battery=battery,
                        online=True,
                    )
                    continue

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
            # Bevorzugt Thermostat
            thermo = self._get_module(modules, getattr(self._Module, "Thermostat", None), "Thermostat")

            if thermo is not None:
                setter = getattr(thermo, "set_target_temperature", None) or getattr(thermo, "set_temperature", None)
                if setter is None:
                    raise RuntimeError("Thermostat module has no setter for target temperature")
                await setter(float(temperature))
                return

            # Fallback
            if hasattr(child, "set_target_temperature"):
                await child.set_target_temperature(float(temperature))
                return
            raise RuntimeError("No way to set target temperature on this device")
