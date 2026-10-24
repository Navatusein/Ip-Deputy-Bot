import logging
from pathlib import Path

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat
from aiogram.utils.i18n import I18n

SOURCE_LOCALE = "uk"
SUPPORTED_LOCALES = ("uk", "ru", "en")
LOCALES_PATH = Path(__file__).resolve().parent.parent / "locales"
DOMAIN = "default"

logger = logging.getLogger(__name__)


def N_(text: str) -> str:
    return text


BOT_COMMANDS = (
    ("start", N_("Показати головне меню")),
    ("today", N_("Розклад на сьогодні")),
    ("tomorrow", N_("Розклад на завтра")),
    ("this_week", N_("Розклад на цей тиждень")),
    ("next_week", N_("Розклад на наступний тиждень")),
)


def create_i18n() -> I18n:
    return I18n(path=LOCALES_PATH, default_locale=SOURCE_LOCALE, domain=DOMAIN)


def normalize_locale(code: str | None) -> str | None:
    if not code:
        return None

    language = code.lower().replace("_", "-").split("-")[0]
    return language if language in SUPPORTED_LOCALES else None


def locale_from_telegram(code: str | None) -> str:
    return normalize_locale(code) or SOURCE_LOCALE


def translations_of(i18n: I18n, msgid: str) -> set[str]:
    return {i18n.gettext(msgid, locale=locale) for locale in SUPPORTED_LOCALES}


def bot_commands(i18n: I18n, locale: str) -> list[BotCommand]:
    return [
        BotCommand(command=command, description=i18n.gettext(description, locale=locale))
        for command, description in BOT_COMMANDS
    ]


async def setup_bot_commands(bot: Bot, i18n: I18n) -> None:
    await bot.set_my_commands(bot_commands(i18n, SOURCE_LOCALE))

    for locale in SUPPORTED_LOCALES:
        await bot.set_my_commands(bot_commands(i18n, locale), language_code=locale)


async def set_chat_commands(bot: Bot, i18n: I18n, chat_id: int, locale: str) -> None:
    try:
        await bot.set_my_commands(bot_commands(i18n, locale), scope=BotCommandScopeChat(chat_id=chat_id))
    except Exception as error:
        logger.warning("Failed to set chat commands: %s", type(error).__name__)
