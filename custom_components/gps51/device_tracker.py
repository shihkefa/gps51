import logging
import aiohttp
from datetime import timedelta
from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, API_URL, LAST_POSITION_ACTION

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)  # ✅ 讓 HA 每 60 秒自動更新

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up GPS51 device tracker from a config entry."""
    deviceid = entry.data["deviceid"]
    token_coordinator = hass.data[DOMAIN][entry.entry_id]

    tracker = GPS51DeviceTracker(deviceid, token_coordinator)
    async_add_entities([tracker], True)

class GPS51DeviceTracker(TrackerEntity):
    """Representation of GPS51 tracker."""

    def __init__(self, deviceid, token_coordinator):
        """Initialize the GPS tracker."""
        self._deviceid = deviceid
        self._token_coordinator = token_coordinator
        self._attr_unique_id = f"gps51_tracker_{deviceid}"
        self._attr_name = f"GPS51 Tracker {deviceid}"
        self._attr_latitude = None
        self._attr_longitude = None
        self._attr_speed = None
        self._attr_status = None
        self.session = aiohttp.ClientSession()

    @property
    def should_poll(self):
        """Return True because we need polling."""
        return True  # ✅ 讓 HA 主動輪詢更新

    @property
    def extra_state_attributes(self):
        """Return additional attributes like speed & vehicle status."""
        return {
            "速度": self._attr_speed,
            "車輛狀態": self._attr_status
        }

    async def async_update(self):
        """Fetch new state data for the tracker."""
        token = self._token_coordinator.token
        if not token:
            _LOGGER.warning("GPS51 token is missing, skipping update.")
            return

        url = f"{API_URL}?action={LAST_POSITION_ACTION}&token={token}"
        payload = {"deviceids": [self._deviceid], "lastquerypositiontime": 0}
        headers = {"Content-Type": "application/json"}

        try:
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status != 200:
                    _LOGGER.warning(f"GPS51 API 請求失敗: {response.status}")
                    return

                data = await response.json()
                if data.get("status") != 0 or "records" not in data:
                    _LOGGER.warning("GPS51 API 回應無效: %s", data)
                    return

                records = data.get("records", [])
                if not records:
                    _LOGGER.warning("未找到 GPS 位置數據")
                    return

                record = records[0]
                self._attr_latitude = record.get("callat")
                self._attr_longitude = record.get("callon")
                self._attr_speed = record.get("speed", 0)
                self._attr_status = record.get("strstatusen", "未知")

                _LOGGER.info(f"Updated GPS51: 緯度: {self._attr_latitude}, 經度: {self._attr_longitude}, 速度: {self._attr_speed}, 車輛狀態: {self._attr_status}")

        except Exception as e:
            _LOGGER.error(f"GPS51 API 請求失敗: {e}")

    async def async_will_remove_from_hass(self):
        """Clean up session when entity is removed."""
        await self.session.close()
