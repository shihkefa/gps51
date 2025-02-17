import logging
import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class GPS51ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GPS51."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title=user_input["username"], data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required("username"): str,
                vol.Required("password"): str,
                vol.Required("deviceid"): str,  # 讓使用者輸入 device ID
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
