from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from bot.services.api_client import ApiClient
from bot.services.settings_cache import SettingsCache


class StudentSettingsMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("event_from_user")
        api: ApiClient = data["api"]
        settings_cache: SettingsCache = data["settings_cache"]

        data["student_settings"] = None

        if user is not None and not user.is_bot:
            data["student_settings"] = await settings_cache.load(api, user.id)

        return await handler(event, data)
