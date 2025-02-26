import logging
import requests
from datetime import time
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_change
from .const import DOMAIN, API_URL, LOGIN_ACTION

_LOGGER = logging.getLogger(__name__)

class GPS51TokenCoordinator:
    """Coordinator to refresh GPS51 token at fixed intervals."""

    def __init__(self, hass: HomeAssistant, username: str, password: str):
        """Initialize the coordinator."""
        self.hass = hass
        self.username = username
        self.password = password
        self.token = None

        async_track_time_change(
            self.hass,
            self._schedule_token_refresh,
            hour=[0, 4, 8, 12, 16, 20],
            minute=0,
            second=0,
        )

    @callback
    def _schedule_token_refresh(self, now):
        """Callback triggered to refresh token."""
        self.hass.async_create_task(self._async_update_token())

    async def _async_update_token(self):
        """Asynchronously update the token."""
        new_token = await self.hass.async_add_executor_job(self._fetch_token)
        if new_token:
            self.token = new_token

    def _fetch_token(self):
        """Synchronously fetch a new token."""
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
            return data["token"] if data.get("status") == 0 else None
        except Exception as e:
            _LOGGER.error("Exception during token update: %s", e)
        return None
