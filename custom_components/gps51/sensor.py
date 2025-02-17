import logging
import requests
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, API_URL, LAST_POSITION_ACTION, ATTR_SPEED, ATTR_STATUS

_LOGGER = logging.getLogger(__name__)

def get_device_status(token, device_id):
    """Fetch device status from GPS51 API."""
    payload = {
        "deviceids": [device_id],
        "lastquerypositiontime": 0
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{API_URL}?action={LAST_POSITION_ACTION}&token={token}", json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data.get("status") == 0 and "records" in data:
            record = data["records"][0]
            return {
                ATTR_SPEED: record["speed"],
                ATTR_STATUS: record["strstatus"]
            }
    return None

class GPS51Sensor(Entity):
    """Representation of a GPS51 sensor."""

    def __init__(self, hass, device_id):
        """Initialize the sensor."""
        self.hass = hass
        self.device_id = device_id
        self._attr_name = f"GPS51 {device_id} Speed"
        self._attr_state = None

    def update(self):
        """Fetch new state data for the sensor."""
        token = self.hass.data[DOMAIN].get("token")
        if not token:
            _LOGGER.error("No token available for GPS51 API.")
            return

        status = get_device_status(token, self.device_id)
        if status:
            self._attr_state = status[ATTR_SPEED]
