from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_CLIMATE, CONF_CONTACTS

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        if user_input is not None:
            title = "KASA KE100 (Matter Proxy)"
            return self.async_create_entry(title=title, data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_CLIMATE): str,            # z.B. climate.kh100_radiator
            vol.Optional(CONF_CONTACTS, default=""): str, # CSV: binary_sensor.bad_fenster,binary_sensor.balkon_tuer
        })
        return self.async_show_form(step_id="user", data_schema=schema)
