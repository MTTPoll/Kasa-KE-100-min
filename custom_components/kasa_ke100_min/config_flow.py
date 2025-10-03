from __future__ import annotations
from typing import Any
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD
from .const import DOMAIN, MIN_SCAN_INTERVAL_S, MAX_SCAN_INTERVAL_S

CONF_SCAN_INTERVAL = "scan_interval"  # Sekunden

class KasaKe100ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            username = (user_input.get(CONF_USERNAME) or "").strip() or None
            password = (user_input.get(CONF_PASSWORD) or "").strip() or None
            scan_interval = int(user_input.get(CONF_SCAN_INTERVAL) or 5)
            if scan_interval < MIN_SCAN_INTERVAL_S:
                scan_interval = MIN_SCAN_INTERVAL_S
            if scan_interval > MAX_SCAN_INTERVAL_S:
                scan_interval = MAX_SCAN_INTERVAL_S

            return self.async_create_entry(
                title=f"KH100 ({host})",
                data={
                    CONF_HOST: host,
                    CONF_USERNAME: username,
                    CONF_PASSWORD: password,
                    CONF_SCAN_INTERVAL: scan_interval,
                },
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_USERNAME): str,
                vol.Optional(CONF_PASSWORD): str,
                vol.Optional(CONF_SCAN_INTERVAL, default=5): vol.All(int, vol.Range(min=MIN_SCAN_INTERVAL_S, max=MAX_SCAN_INTERVAL_S)),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)
