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
    await token_coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN] = token_coordinator  # ✅ 儲存 `token` 管理器

    # ✅ 這裡用 `await` 確保 `device_tracker` 先完成設定
    await hass.config_entries.async_forward_entry_setups(entry, ["device_tracker"])

    return True
