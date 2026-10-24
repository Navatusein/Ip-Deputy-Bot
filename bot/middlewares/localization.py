from typing import Any

from aiogram.types import TelegramObject, User
from aiogram.utils.i18n import I18nMiddleware

from bot.i18n import SUPPORTED_LOCALES, locale_from_telegram
from bot.models import StudentSettings


class Localization(I18nMiddleware):
    async def get_locale(self, event: TelegramObject, data: dict[str, Any]) -> str:
        settings: StudentSettings | None = data.get("student_settings")

        if settings is not None and settings.language in SUPPORTED_LOCALES:
            return settings.language

        user: User | None = data.get("event_from_user")
        return locale_from_telegram(user.language_code if user else None)
