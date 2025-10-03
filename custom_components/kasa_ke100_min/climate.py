# climate.py
from homeassistant.components.climate import ClimateEntity

class Ke100ClimateEntity(ClimateEntity):
    _attr_min_temp = 5
    _attr_max_temp = 30
