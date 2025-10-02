from __future__ import annotations
from typing import Any
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

# Use literals here to avoid import issues causing 'Invalid handler specified'
DOMAIN = "kasa_ke100_min"
CONF_HOST = "host"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            username = (user_input.get(CONF_USERNAME) or "").strip() or None
            password = (user_input.get(CONF_PASSWORD) or "").strip() or None
            return self.async_create_entry(
                title=f"KH100 ({host})",
                data={CONF_HOST: host, CONF_USERNAME: username, CONF_PASSWORD: password},
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_USERNAME): str,
                vol.Optional(CONF_PASSWORD): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)
