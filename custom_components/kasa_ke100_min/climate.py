
from __future__ import annotations
from typing import Any, Dict, Set, Optional, List
import re
from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACMode, HVACAction
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature, PRECISION_TENTHS
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers import entity_registry as er
from .const import DOMAIN, MANUFACTURER, MODEL_KE100
from .coordinator import KasaKe100Coordinator

PARALLEL_UPDATES = 0

def _str_to_float(x):
    try:
        return float(x) if x is not None else None
    except (TypeError, ValueError):
        return None

def _slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s-]+", "_", s).strip("_")
    return s

def _is_t310(dev_id: str, raw: Dict[str, Any]) -> bool:
    if not isinstance(raw, dict):
        return False
    if "is_open" in raw:
        return False  # contact sensor
    has_temp = raw.get("current_temp") is not None
    tgt = _str_to_float(raw.get("target_temp"))
    model = (raw.get("model") or raw.get("device_model") or "").upper()
    if "T310" in model or "T315" in model:
        return True
    if dev_id.startswith("802E") and has_temp and tgt is None:
        return True
    if ("humidity" in raw) and tgt is None:
        return True
    return False

def _is_ke100(dev_id: str, raw: Dict[str, Any]) -> bool:
    model = raw.get("model") or raw.get("device_model")
    if model == MODEL_KE100:
        return True
    tgt = _str_to_float(raw.get("target_temp"))
    if tgt is not None:
        return True
    if dev_id.startswith("8035"):
        return True
    return False

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: KasaKe100Coordinator = data["coordinator"]

    known: set[str] = set()

    def _check_devices():
        ents = []
        devices = (coordinator.data.get("devices") or {})
        for dev_id, raw in devices.items():
            if dev_id in known:
                continue
            raw = raw or {}
            if _is_ke100(dev_id, raw) and not _is_t310(dev_id, raw):
                ents.append(Ke100ClimateEntity(coordinator, dev_id))
                known.add(dev_id)
                continue
            if _is_t310(dev_id, raw):
                ents.append(T310ClimateDisplayEntity(coordinator, dev_id))
                known.add(dev_id)
                continue
        if ents:
            async_add_entities(ents)

    _check_devices()
    entry.async_on_unload(coordinator.async_add_listener(_check_devices))

# ---- KE100 TRV (steuerbar) ----
class Ke100ClimateEntity(CoordinatorEntity, ClimateEntity):
    _attr_supported_features: Set[ClimateEntityFeature] = {
        ClimateEntityFeature.TARGET_TEMPERATURE,
        ClimateEntityFeature.TURN_ON,
        ClimateEntityFeature.TURN_OFF,
    }
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_precision = PRECISION_TENTHS
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_min_temp = 5
    _attr_max_temp = 30

    def __init__(self, coordinator: KasaKe100Coordinator, device_id: str) -> None:
        super().__init__(coordinator)
        self._id = device_id
        self._attr_unique_id = device_id

    @property
    def _st(self):
        return (self.coordinator.data.get("devices") or {}).get(self._id) or {}

    @property
    def name(self) -> str:
        return self._st.get("name") or f"KE100 {self._id}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._id)},
            "manufacturer": MANUFACTURER,
            "model": MODEL_KE100,
            "name": self.name,
        }

    @property
    def current_temperature(self) -> float | None:
        return _str_to_float(self._st.get("current_temp"))

    @property
    def target_temperature(self) -> float | None:
        return _str_to_float(self._st.get("target_temp"))

    @property
    def hvac_mode(self) -> HVACMode | None:
        return HVACMode.HEAT if self._st.get("hvac_mode") == "heat" else HVACMode.OFF

    @property
    def hvac_action(self) -> HVACAction | None:
        s = (self._st.get("hvac_action") or "").lower()
        if s == "heating":
            return HVACAction.HEATING
        if s == "idle":
            return HVACAction.IDLE
        if s == "off":
            return HVACAction.OFF
        return None

    async def async_set_temperature(self, **kwargs: Any) -> None:
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is None:
            return
        await self.coordinator.client.async_set_target_temp(self._id, float(temp))
        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        await self.coordinator.client.async_set_state(self._id, hvac_mode != HVACMode.OFF)
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        await self.async_set_hvac_mode(HVACMode.HEAT)

    async def async_turn_off(self) -> None:
        await self.async_set_hvac_mode(HVACMode.OFF)

# ---- T310 als "Climate-Display" (nur Anzeige) ----
class T310ClimateDisplayEntity(CoordinatorEntity, ClimateEntity):
    # Keine Steuerfunktionen; keine auswählbaren Modi
    _attr_supported_features: Set[ClimateEntityFeature] = set()
    _attr_hvac_modes: list[HVACMode] = []
    _attr_precision = PRECISION_TENTHS
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_min_temp = 0
    _attr_max_temp = 0

    def __init__(self, coordinator: KasaKe100Coordinator, device_id: str) -> None:
        super().__init__(coordinator)
        self._id = device_id
        self._attr_unique_id = f"{device_id}_t310_display"

    @property
    def _st(self):
        return (self.coordinator.data.get("devices") or {}).get(self._id) or {}

    @property
    def name(self) -> str:
        return self._st.get("name") or f"Tapo T310 {self._id[-4:]}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._id)},
            "manufacturer": MANUFACTURER,
            "model": "Tapo T310",
            "name": self.name,
        }

    # ---- humidity bridging ----
    def _humidity_from_same_device(self) -> Optional[float]:
        try:
            er_reg = er.async_get(self.hass)
            ent_entry = er_reg.async_get(self.entity_id)
            if not ent_entry or not ent_entry.device_id:
                return None
            dev_id = ent_entry.device_id
            for e in er_reg.entities.values():
                if e.device_id != dev_id or e.domain != "sensor":
                    continue
                st = self.hass.states.get(e.entity_id)
                if not st or st.state in (None, "", "unknown", "unavailable"):
                    continue
                if st.attributes.get("device_class") == "humidity":
                    try:
                        return float(st.state)
                    except (TypeError, ValueError):
                        continue
            return None
        except Exception:
            return None

    def _humidity_from_named_sensor(self) -> Optional[float]:
        base = _slugify(self.name)
        for ent_id in (f"sensor.{base}_luftfeuchtigkeit", f"sensor.{base}_luftfeuchte", f"sensor.{base}_humidity"):
            st = self.hass.states.get(ent_id)
            if st and st.state not in (None, "", "unknown", "unavailable"):
                try:
                    return float(st.state)
                except (TypeError, ValueError):
                    continue
        return None

    def _find_humidity_value(self) -> Optional[float]:
        hum = self._st.get("humidity")
        if hum is not None:
            try:
                return float(hum)
            except (TypeError, ValueError):
                pass
        return self._humidity_from_same_device() or self._humidity_from_named_sensor()

    # ---- climate interface (read-only) ----
    @property
    def current_temperature(self) -> float | None:
        return _str_to_float(self._st.get("current_temp"))

    @property
    def target_temperature(self) -> float | None:
        return None

    @property
    def hvac_mode(self) -> HVACMode | None:
        # Report a stable state to avoid "unknown" while keeping selector hidden
        return HVACMode.HEAT

    @property
    def hvac_action(self) -> Optional[HVACAction]:
        # No action shown
        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        attrs: Dict[str, Any] = {}
        hum = self._find_humidity_value()
        if hum is not None:
            attrs["humidity"] = hum
        if "battery" in self._st:
            attrs["battery"] = self._st.get("battery")
        if "rssi" in self._st:
            attrs["rssi"] = self._st.get("rssi")
        if "signal" in self._st:
            attrs["signal"] = self._st.get("signal")
        return attrs
