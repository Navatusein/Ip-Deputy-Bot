import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from cachetools import TTLCache

from bot.models import StudentSettings
from bot.services.api_client import ApiClient

logger = logging.getLogger(__name__)


class LastActivityMiddleware(BaseMiddleware):
    def __init__(self, interval: float = 300, maxsize: int = 10_000) -> None:
        self._recent: TTLCache[int, bool] = TTLCache(maxsize=maxsize, ttl=interval)
        self._tasks: set[asyncio.Task[None]] = set()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        settings: StudentSettings | None = data.get("student_settings")

        if settings is not None and settings.telegram_id not in self._recent:
            self._recent[settings.telegram_id] = True
            task = asyncio.create_task(self._update(data["api"], settings.telegram_id))
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)

        return await handler(event, data)

    @staticmethod
    async def _update(api: ApiClient, telegram_id: int) -> None:
        try:
            await api.update_last_activity(telegram_id)
        except Exception as error:
            logger.warning("Failed to update last activity: %s", error)
