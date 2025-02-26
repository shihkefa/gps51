import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .coordinator import GPS51TokenCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up GPS51 from a config entry."""
    username = entry.data["username"]
    password = entry.data["password"]

    token_coordinator = GPS51TokenCoordinator(hass, username, password)
    await token_coordinator._async_update_token()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = token_coordinator  # ✅ 每個設備獨立 Token

    await hass.config_entries.async_forward_entry_setups(entry, ["device_tracker"])  # ❌ 移除 "sensor"

    return True
