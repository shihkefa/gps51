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
            # ✅ 自動將密碼轉換為 MD5（32 位元小寫）
            md5_password = hashlib.md5(user_input["password"].encode()).hexdigest()
            user_input["password"] = md5_password  # 使用加密後的密碼

            _LOGGER.info(f"使用者輸入的密碼已轉換為 MD5: {md5_password}")

            return self.async_create_entry(title=user_input["username"], data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required("username"): str,
                vol.Required("password"): str,
                vol.Required("deviceid"): str,  # 讓使用者輸入 device ID
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
