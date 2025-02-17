import logging
import requests
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from .const import DOMAIN, API_URL, LAST_POSITION_ACTION

_LOGGER = logging.getLogger(__name__)

def get_device_location(token, deviceid):
    """Fetch latest GPS location from GPS51 API."""
    payload = {
        "deviceids": [deviceid],
        "lastquerypositiontime": 0
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{API_URL}?action={LAST_POSITION_ACTION}&token={token}", json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data.get("status") == 0 and "records" in data:
            return data["records"][0]
    return None

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up GPS51 device tracker based on a config entry."""
    token = hass.data[DOMAIN].get("token")
    deviceid = hass.data[DOMAIN].get("deviceid")

    if not token or not deviceid:
        _LOGGER.error("Missing token or device ID for GPS51")
        return

    tracker = GPS51DeviceTracker(hass, token, deviceid)
    async_add_entities([tracker], True)

class GPS51DeviceTracker(TrackerEntity):
    """Representation of GPS51 tracker."""

    def __init__(self, hass, token, device_id):
        """Initialize the GPS tracker."""
        self.hass = hass
        self.token = token
        self.device_id = device_id
        self._attr_unique_id = f"gps51_{device_id}"
        self._attr_name = f"GPS51 Tracker {device_id}"
        self._attr_latitude = None
        self._attr_longitude = None
        self._attr_speed = None
        self._attr_status = None  # 對應 `strstatusen`
        self._attr_scan_interval = 60  # 設定 60 秒更新一次

    @property
    def should_poll(self):
        """讓 Home Assistant 每 60 秒自動輪詢更新位置."""
        return True

    @property
    def scan_interval(self):
        """設定更新頻率（單位：秒）"""
        return self._attr_scan_interval

    @property
    def extra_state_attributes(self):
        """回傳額外屬性，修改名稱顯示"""
        return {
            "速度": self._attr_speed,  # 修改名稱為「速度」
            "車輛狀態": self._attr_status  # 修改名稱為「車輛狀態」
        }

    def update(self):
        """Fetch new state data for the sensor."""
        _LOGGER.info(f"Updating GPS51 Tracker: {self.device_id}")

        location = get_device_location(self.token, self.device_id)
        if location:
            self._attr_latitude = location["callat"]
            self._attr_longitude = location["callon"]
            self._attr_speed = location["speed"]  # 提取速度
            self._attr_status = location["strstatusen"]  # 提取 `strstatusen`
            _LOGGER.info(f"Updated GPS51 {self.device_id}: {self._attr_latitude}, {self._attr_longitude}, 速度: {self._attr_speed}, 車輛狀態: {self._attr_status}")
