
from __future__ import annotations
from typing import Any
from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACMode, HVACAction
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature, PRECISION_TENTHS
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import callback
from .const import DOMAIN, MANUFACTURER, MODEL_KE100
from .coordinator import KasaKe100Coordinator

PARALLEL_UPDATES = 0

STATE_TO_ACTION = {
    "idle": HVACAction.IDLE,
    "heating": HVACAction.HEATING,
    "off": HVACAction.OFF,
}
STATE_TO_MODE = {
    "heat": HVACMode.HEAT,
    "off": HVACMode.OFF,
}

def _is_valid_trv(raw: dict) -> bool:
    # Prefer explicit model check if present
    model = raw.get("model") or raw.get("device_model")
    if model is not None and model != MODEL_KE100:
        return False
    # Require a numeric target temperature and a known hvac_mode
    tgt = raw.get("target_temp")
    hvac_mode = raw.get("hvac_mode")
    if not isinstance(tgt, (int, float)):
        return False
    if hvac_mode not in ("heat", "off"):
        return False
    return True

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: KasaKe100Coordinator = data["coordinator"]

    known = set()
    def _check_devices():
        ents = []
        for dev_id, raw in coordinator.data.get("devices", {}).items():
            if dev_id in known or not _is_valid_trv(raw):
                continue
            ents.append(Ke100ClimateEntity(coordinator, dev_id))
            known.add(dev_id)
        if ents:
            async_add_entities(ents)
    _check_devices()
    entry.async_on_unload(coordinator.async_add_listener(_check_devices))

class Ke100ClimateEntity(CoordinatorEntity, ClimateEntity):
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_precision = PRECISION_TENTHS
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_min_temp = 5
    _attr_max_temp = 30

    def __init__(self, coordinator: KasaKe100Coordinator, device_id: str) -> None:
        super().__init__(coordinator)
        self._id = device_id
        self._attr_unique_id = device_id

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_write_ha_state()

    @property
    def _st(self):
        return self.coordinator.data.get("devices", {}).get(self._id) or {}

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
        return self._st.get("current_temp")

    @property
    def target_temperature(self) -> float | None:
        return self._st.get("target_temp")

    @property
    def hvac_mode(self) -> HVACMode:
        return STATE_TO_MODE.get(self._st.get("hvac_mode"), HVACMode.OFF)

    @property
    def hvac_action(self) -> HVACAction:
        return STATE_TO_ACTION.get(self._st.get("hvac_action"), HVACAction.OFF)

    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()

    async def async_update(self) -> None:
        return

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
