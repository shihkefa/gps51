import logging
import voluptuous as vol
import hashlib
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
            md5_password = hashlib.md5(user_input["password"].encode()).hexdigest()
            user_input["password"] = md5_password  

            await self.async_set_unique_id(user_input["deviceid"])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(title=user_input["username"], data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required("username"): str,
                vol.Required("password"): str,
                vol.Required("deviceid"): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
