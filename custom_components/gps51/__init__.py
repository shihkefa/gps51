import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .coordinator import GPS51Coordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up GPS51 from a config entry."""
    username = entry.data["username"]
    password = entry.data["password"]
    deviceid = entry.data["deviceid"]

    coordinator = GPS51Coordinator(hass, username, password, deviceid)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN] = coordinator

    # 註冊 `device_tracker`
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "device_tracker")
    )

    return True
