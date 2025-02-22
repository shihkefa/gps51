import logging
import requests
import asyncio
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, API_URL, LOGIN_ACTION, LAST_POSITION_ACTION

_LOGGER = logging.getLogger(__name__)

class GPS51Coordinator(DataUpdateCoordinator):
    """Coordinator to fetch GPS51 data."""

    def __init__(self, hass, username, password, deviceid):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=1),  # 每 1 分鐘更新設備位置
        )
        self.hass = hass
        self.username = username
        self.password = password
        self.deviceid = deviceid
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
                return data["token"]
        return None

    def get_device_location(self):
        """Fetch latest GPS location from GPS51 API."""
        if not self.token:
            self.token = self.get_token()

        payload = {
            "deviceids": [self.deviceid],
            "lastquerypositiontime": 0
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{API_URL}?action={LAST_POSITION_ACTION}&token={self.token}", json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == 0 and "records" in data:
                return data["records"][0]
            elif data.get("status") == 9903:  # Token 過期
                _LOGGER.warning("GPS51 token expired, refreshing token...")
                self.token = self.get_token()
                return self.get_device_location()  # 重新查詢設備位置
        return None

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            return await self.hass.async_add_executor_job(self.get_device_location)
        except Exception as err:
            raise UpdateFailed(f"Error updating GPS51 data: {err}")
