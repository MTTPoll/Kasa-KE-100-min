from __future__ import annotations
from typing import Any
import logging
from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACMode, HVACAction
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature, PRECISION_TENTHS
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import callback
from .const import DOMAIN, MANUFACTURER, MODEL_KE100
from .coordinator import KasaKe100Coordinator

_LOGGER = logging.getLogger(__name__)

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

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: KasaKe100Coordinator = data["coordinator"]

    known = set()

    def _check_devices():
        ents = []
        for dev_id, raw in coordinator.data.get("devices", {}).items():
            if dev_id in known or "target_temp" not in raw:
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
    _attr_hvac_mode = HVACMode.OFF
    _attr_hvac_action = HVACAction.OFF
    _attr_min_temp = 5
    _attr_max_temp = 30

    def __init__(self, coordinator: KasaKe100Coordinator, device_id: str) -> None:
        super().__init__(coordinator)
        self._id = device_id
        self._attr_unique_id = device_id

    async def async_added_to_hass(self) -> None:
        # WICHTIG: Registrierung beim Coordinator, sonst kommen keine Updates!
        await super().async_added_to_hass()
        self._async_update_attrs()

    @property
    def _st(self):
        return self.coordinator.data.get("devices", {}).get(self._id)

    @property
    def name(self) -> str:
        st = self._st
        return st.get("name") if st else f"KE100 {self._id}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._id)},
            "manufacturer": MANUFACTURER,
            "model": MODEL_KE100,
            "name": self.name,
        }

    @callback
    def _async_update_attrs(self) -> None:
        st = self._st or {}
        self._attr_current_temperature = st.get("current_temp")
        self._attr_target_temperature = st.get("target_temp")
        hvac_action = st.get("hvac_action", "off")
        hvac_mode = st.get("hvac_mode", "off")
        self._attr_hvac_action = STATE_TO_ACTION.get(hvac_action, HVACAction.OFF)
        self._attr_hvac_mode = STATE_TO_MODE.get(hvac_mode, HVACMode.OFF)

    @callback
    def _handle_coordinator_update(self) -> None:
        self._async_update_attrs()
        super()._handle_coordinator_update()

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
