import logging
import requests
import time
from datetime import timedelta, time
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_change, async_track_time_interval
from .const import DOMAIN, API_URL, LOGIN_ACTION

_LOGGER = logging.getLogger(__name__)

TIMEOUT = 10  # ✅ 設定 API 超時為 10 秒
MAX_RETRIES = 3  # ✅ 最多重試 3 次
LOGIN_INTERVAL = timedelta(hours=6)  # ✅ 每 6 小時執行一次登入

class GPS51TokenCoordinator:
    """Coordinator to refresh GPS51 token at fixed intervals."""

    def __init__(self, hass: HomeAssistant, username: str, password: str):
        """Initialize the coordinator."""
        self.hass = hass
        self.username = username
        self.password = password
        self.token = None

        # ✅ 檢查 Token 刷新是否有啟動
        _LOGGER.info("GPS51TokenCoordinator initialized. Will refresh token at 0, 4, 8, 12, 16, 20 and trigger login every 6 hours.")

        # ✅ 在 0, 4, 8, 12, 16, 20 固定時間點更新 Token
        async_track_time_change(
            self.hass,
            self._schedule_token_refresh,
            hour=[0, 4, 8, 12, 16, 20],
            minute=0,
            second=0,
        )

        # ✅ 每 6 小時執行一次登入動作，但不影響 Token
        async_track_time_interval(self.hass, self._schedule_login_refresh, LOGIN_INTERVAL)

    @callback
    def _schedule_token_refresh(self, now):
        """Callback triggered to refresh token."""
        _LOGGER.info("Scheduled token refresh started.")  # ✅ 紀錄 Token 刷新
        self.hass.async_create_task(self._async_update_token())

    async def _async_update_token(self):
        """Asynchronously update the token."""
        new_token = await self.hass.async_add_executor_job(self._fetch_token)
        if new_token:
            self.token = new_token
            _LOGGER.info("GPS51 token updated successfully.")
        else:
            _LOGGER.error("Failed to update GPS51 token after retries.")

    def _fetch_token(self):
        """Synchronously fetch a new token with retries."""
        payload = {
            "type": "USER",
            "from": "web",
            "username": self.username,
            "password": self.password,
            "browser": "Chrome/104.0.0.0"
        }

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                _LOGGER.info(f"Attempt {attempt}: Requesting new token...")
                response = requests.post(f"{API_URL}?action={LOGIN_ACTION}", json=payload, timeout=TIMEOUT)
                response.raise_for_status()
                data = response.json()

                if data.get("status") == 0 and "token" in data:
                    _LOGGER.info(f"Token received successfully on attempt {attempt}.")
                    return data["token"]

                _LOGGER.warning(f"Attempt {attempt}: Token request failed. Response: {data}")

            except requests.Timeout:
                _LOGGER.warning(f"Attempt {attempt}: API request timed out after {TIMEOUT} seconds.")
            except requests.RequestException as e:
                _LOGGER.error(f"Attempt {attempt}: Exception during token update: {e}")

            time.sleep(5)  # ✅ 等待 5 秒後再試
        
        _LOGGER.error("All token update attempts failed.")
        return None  # ❌ 如果所有重試都失敗，回傳 None

    @callback
    def _schedule_login_refresh(self, now):
        """Callback triggered every 6 hours to send login request."""
        _LOGGER.info("Scheduled login request started.")
        self.hass.async_create_task(self._async_login_request())

    async def _async_login_request(self):
        """Asynchronously send login request."""
        success = await self.hass.async_add_executor_job(self._send_login_request)
        if success:
            _LOGGER.info("GPS51 login request completed successfully.")
        else:
            _LOGGER.error("GPS51 login request failed after retries.")

    def _send_login_request(self):
        """Synchronously send login request with retries."""
        payload = {
            "type": "USER",
            "from": "web",
            "username": self.username,
            "password": self.password,
            "browser": "Chrome/104.0.0.0"
        }

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                _LOGGER.info(f"Attempt {attempt}: Sending login request to keep session active...")
                response = requests.post(f"{API_URL}?action={LOGIN_ACTION}", json=payload, timeout=TIMEOUT)
                response.raise_for_status()
                data = response.json()

                if data.get("status") == 0:
                    _LOGGER.info(f"Login request succeeded on attempt {attempt}.")
                    return True  # ✅ 成功
                else:
                    _LOGGER.warning(f"Attempt {attempt}: Login request failed. Response: {data}")

            except requests.Timeout:
                _LOGGER.warning(f"Attempt {attempt}: Login request timed out after {TIMEOUT} seconds.")
            except requests.RequestException as e:
                _LOGGER.error(f"Attempt {attempt}: Exception during login request: {e}")

            time.sleep(5)  # ✅ 等待 5 秒後再試
        
        _LOGGER.error("All login request attempts failed.")
        return False  # ❌ 如果所有重試都失敗，回傳 False
