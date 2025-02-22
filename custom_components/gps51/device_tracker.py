import logging
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up GPS51 device tracker based on a config entry."""
    coordinator = hass.data[DOMAIN]

    async_add_entities([GPS51DeviceTracker(coordinator)], True)

class GPS51DeviceTracker(TrackerEntity):
    """Representation of GPS51 tracker."""

    def __init__(self, coordinator):
        """Initialize the GPS tracker."""
        self.coordinator = coordinator
        self._attr_unique_id = f"gps51_{coordinator.deviceid}"
        self._attr_name = f"GPS51 Tracker {coordinator.deviceid}"
        self._attr_latitude = None
        self._attr_longitude = None

    @property
    def should_poll(self):
        """讓 Home Assistant 每 1 分鐘自動更新 GPS 位置."""
        return False  # 我們用 `DataUpdateCoordinator` 來更新

    async def async_update(self):
        """Fetch new state data for the sensor."""
        await self.coordinator.async_request_refresh()
        data = self.coordinator.data
        if data:
            self._attr_latitude = data["callat"]
            self._attr_longitude = data["callon"]
            _LOGGER.info(f"Updated GPS51: {self._attr_latitude}, {self._attr_longitude}")
