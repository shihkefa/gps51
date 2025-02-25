# custom_components/gps51/coordinator.py

import logging
import requests
from datetime import time
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_change
from .const import DOMAIN, API_URL, LOGIN_ACTION

_LOGGER = logging.getLogger(__name__)

class GPS51TokenCoordinator:
    """Coordinator to refresh GPS51 token at 12:00 AM and 12:00 PM."""

    def __init__(self, hass: HomeAssistant, username: str, password: str):
        """Initialize the coordinator."""
        self.hass = hass
        self.username = username
        self.password = password
        self.token = None

        # 固定在每天的 00:00 和 12:00 触发 token 刷新
        async_track_time_change(
            self.hass,
            self._schedule_token_refresh,
            hour=[0, 4, 8, 12, 16, 20],
            minute=0,
            second=0,
        )
        _LOGGER.info("GPS51TokenCoordinator initialized. Scheduled token refresh at 00:00 and 12:00.")

    @callback
    def _schedule_token_refresh(self, now):
        """Callback triggered at scheduled times to refresh token."""
        _LOGGER.info("Scheduled token refresh triggered at %s", now)
        self.hass.async_create_task(self._async_update_token())

    async def _async_update_token(self):
        """Asynchronously update the token using an executor job."""
        new_token = await self.hass.async_add_executor_job(self._fetch_token)
        if new_token:
            self.token = new_token
            _LOGGER.info("GPS51 token updated successfully: %s", new_token)
        else:
            _LOGGER.error("GPS51 token update failed at scheduled time.")

    def _fetch_token(self):
        """Synchronously fetch a new token from the GPS51 API."""
        payload = {
            "type": "USER",
            "from": "web",
            "username": self.username,
            "password": self.password,
            "browser": "Chrome/104.0.0.0"
        }
        try:
            response = requests.post(f"{API_URL}?action={LOGIN_ACTION}", json=payload)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == 0 and "token" in data:
                return data["token"]
            else:
                _LOGGER.error("Failed to update token. Response JSON: %s", data)
        except Exception as e:
            _LOGGER.error("Exception during token update: %s", e)
        return None
