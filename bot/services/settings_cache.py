from cachetools import TTLCache

from bot.models import StudentSettings
from bot.services.api_client import ApiClient


class SettingsCache:
    def __init__(self, maxsize: int = 10_000, ttl: float = 600, unauthorized_ttl: float = 30) -> None:
        self._settings: TTLCache[int, StudentSettings] = TTLCache(maxsize=maxsize, ttl=ttl)
        self._unauthorized: TTLCache[int, bool] = TTLCache(maxsize=maxsize, ttl=unauthorized_ttl)

    def get(self, telegram_id: int) -> StudentSettings | None:
        return self._settings.get(telegram_id)

    def set(self, settings: StudentSettings) -> None:
        self._unauthorized.pop(settings.telegram_id, None)
        self._settings[settings.telegram_id] = settings

    def set_unauthorized(self, telegram_id: int) -> None:
        self._settings.pop(telegram_id, None)
        self._unauthorized[telegram_id] = True

    def is_unauthorized(self, telegram_id: int) -> bool:
        return telegram_id in self._unauthorized

    def invalidate(self, telegram_id: int) -> None:
        self._settings.pop(telegram_id, None)
        self._unauthorized.pop(telegram_id, None)

    async def load(self, api: ApiClient, telegram_id: int) -> StudentSettings | None:
        settings = self.get(telegram_id)
        if settings is not None:
            return settings

        if self.is_unauthorized(telegram_id):
            return None

        settings = await api.get_settings(telegram_id)

        if settings is None:
            self.set_unauthorized(telegram_id)
        else:
            self.set(settings)

        return settings
