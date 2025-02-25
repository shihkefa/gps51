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
    # 呼叫初始更新方法，讓 token 先獲取一次
    await token_coordinator._async_update_token()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN] = token_coordinator  # 儲存 token 管理器

    # 使用新的 async_forward_entry_setups 載入 device_tracker
    await hass.config_entries.async_forward_entry_setups(entry, ["device_tracker"])

    return True
