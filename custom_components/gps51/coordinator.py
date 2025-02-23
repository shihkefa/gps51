import logging
import requests
import asyncio
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DOMAIN, API_URL, LOGIN_ACTION

_LOGGER = logging.getLogger(__name__)

class GPS51TokenCoordinator(DataUpdateCoordinator):
    """Coordinator to refresh GPS51 token every 12 hours."""

    def __init__(self, hass, username, password):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_token",
            update_interval=timedelta(hours=12),  # ✅ 每 12 小時更新一次 token
        )
        self.hass = hass
        self.username = username
        self.password = password
        self.token = None

    def get_token(self):
        """Login and get a new token from GPS51 API."""
        payload = {
            "type": "USER",
            "from": "web",
            "username": self.username,
            "password": self.password,
            "browser": "Chrome/104.0.0.0"
        }
        response = requests.post(f"{API_URL}?action={LOGIN_ACTION}", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == 0 and "token" in data:
                _LOGGER.info("GPS51 token updated successfully.")
                return data["token"]
        _LOGGER.error("Failed to update GPS51 token.")
        return None

    async def _async_update_data(self):
        """Fetch new token from API every 12 hours."""
        self.token = await self.hass.async_add_executor_job(self.get_token)
        return self.token
