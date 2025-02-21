import logging
import requests
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, API_URL, LOGIN_ACTION

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up GPS51 from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    username = entry.data.get("username")
    password = entry.data.get("password")
    deviceid = entry.data.get("deviceid")

    def get_token():
        """Login and get a new token from GPS51 API."""
        payload = {
            "type": "USER",
            "from": "web",
            "username": username,
            "password": password,
            "browser": "Chrome/104.0.0.0"
        }
        response = requests.post(f"{API_URL}?action=login", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == 0 and "token" in data:
                return data["token"]
        return None

    async def refresh_token():
        """定時更新 `token`，避免過期"""
        while True:
            await hass.async_add_executor_job(get_token)
            _LOGGER.info("GPS51 token 已更新")
            await asyncio.sleep(1800)  # 每 30 分鐘更新一次

    token = await hass.async_add_executor_job(get_token)

    if not token:
        _LOGGER.error("GPS51 login failed, please check username and password.")
        return False

    hass.data[DOMAIN]["token"] = token
    hass.data[DOMAIN]["deviceid"] = deviceid
    _LOGGER.info(f"GPS51 login successful, token received: {token}")

    # 啟動 token 自動更新
    hass.loop.create_task(refresh_token())

    # 註冊 `device_tracker`
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "device_tracker")
    )

    return True
