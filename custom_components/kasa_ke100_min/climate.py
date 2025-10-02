from __future__ import annotations
from typing import Any
from homeassistant.components.climate import ClimateEntity, HVACMode, ClimateEntityFeature, HVACAction
from homeassistant.const import UnitOfTemperature, ATTR_TEMPERATURE
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, MANUFACTURER, MODEL_KE100
from .coordinator import KasaCoordinator

PARALLEL_UPDATES = 0

MIN_C = 5.0
MAX_C = 30.0
STEP_C = 1.0

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: KasaCoordinator = data["coordinator"]
    entities: list[ClimateEntity] = [KE100Climate(coordinator, dev_id) for dev_id in coordinator.data["trvs"]]
    async_add_entities(entities)

class KE100Climate(CoordinatorEntity[KasaCoordinator], ClimateEntity):
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.HEAT]
    _attr_hvac_mode = HVACMode.HEAT
    _attr_has_entity_name = True
    _attr_target_temperature_step = STEP_C
    _attr_min_temp = MIN_C
    _attr_max_temp = MAX_C
    _attr_icon = "mdi:thermostat"

    def __init__(self, coordinator: KasaCoordinator, device_id: str) -> None:
        super().__init__(coordinator)
        self._id = device_id
        self._attr_unique_id = device_id

    @property
    def name(self) -> str | None:
        trv = self.coordinator.data["trvs"].get(self._id)
        return trv.name if trv else None

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(identifiers={(DOMAIN, self._id)}, manufacturer=MANUFACTURER, model=MODEL_KE100, name=self.name)

    @property
    def current_temperature(self) -> float | None:
        return self.coordinator.data["trvs"][self._id].current_temperature

    @property
    def target_temperature(self) -> float | None:
        return self.coordinator.data["trvs"][self._id].target_temperature

    @property
    def hvac_action(self) -> HVACAction | None:
        if getattr(self, "_attr_hvac_mode", None) == HVACMode.OFF:
            return HVACAction.OFF
        trv = self.coordinator.data["trvs"].get(self._id)
        if not trv:
            return None
        cur = trv.current_temperature
        tgt = trv.target_temperature
        if cur is None or tgt is None:
            return None
        if (tgt - cur) > 0.2:
            return HVACAction.HEATING
        return HVACAction.IDLE

    async def async_set_temperature(self, **kwargs: Any) -> None:
        temp_any = kwargs.get(ATTR_TEMPERATURE)
        if temp_any is None:
            return
        temp = round(float(temp_any))
        if temp < MIN_C:
            temp = int(MIN_C)
        if temp > MAX_C:
            temp = int(MAX_C)
        await self.coordinator.client.async_set_target_temperature(self._id, float(temp))
        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            if HVACMode.OFF not in self._attr_hvac_modes:
                self._attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
            self._attr_hvac_mode = HVACMode.OFF
        else:
            if HVACMode.OFF in self._attr_hvac_modes:
                self._attr_hvac_modes = [HVACMode.HEAT]
            self._attr_hvac_mode = HVACMode.HEAT
        await self.coordinator.async_request_refresh()
