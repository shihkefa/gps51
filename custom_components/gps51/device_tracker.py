import logging
import requests
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from .const import DOMAIN, API_URL, LAST_POSITION_ACTION

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up GPS51 device tracker based on a config entry."""
    token_coordinator = hass.data[DOMAIN]  # ✅ 只取 `token`
    deviceid = entry.data["deviceid"]

    async_add_entities([GPS51DeviceTracker(token_coordinator, deviceid)], True)

class GPS51DeviceTracker(TrackerEntity):
    """Representation of GPS51 tracker."""

    def __init__(self, token_coordinator, deviceid):
        """Initialize the GPS tracker."""
        self.token_coordinator = token_coordinator
        self.deviceid = deviceid
        self._attr_unique_id = f"gps51_{deviceid}"
        self._attr_name = f"GPS51 Tracker {deviceid}"
        self._attr_latitude = None
        self._attr_longitude = None
        self._attr_speed = None
        self._attr_status = None

    @property
    def should_poll(self):
        """讓 Home Assistant 自動輪詢更新 GPS 位置."""
        return True  # ✅ 讓 HA 自己管理更新頻率

    @property
    def extra_state_attributes(self):
        """回傳額外屬性（速度 & 車輛狀態）"""
        return {
            "速度": self._attr_speed,
            "車輛狀態": self._attr_status
        }

    def update(self):
        """Fetch new state data for the sensor."""
        token = self.token_coordinator.token  # ✅ 直接取用最新 token
        if not token:
            _LOGGER.warning("GPS51 token is missing, skipping update.")
            return

        payload = {
            "deviceids": [self.deviceid],
            "lastquerypositiontime": 0
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{API_URL}?action={LAST_POSITION_ACTION}&token={token}", json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == 0 and "records" in data:
                record = data["records"][0]
                self._attr_latitude = record["callat"]
                self._attr_longitude = record["callon"]
                self._attr_speed = record.get("speed", 0)
                self._attr_status = record.get("strstatusen", "未知")
                _LOGGER.info(f"Updated GPS51: 緯度: {self._attr_latitude}, 經度: {self._attr_longitude}, 速度: {self._attr_speed}, 車輛狀態: {self._attr_status}")
