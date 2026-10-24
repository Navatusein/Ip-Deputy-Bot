from typing import Any

from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.i18n import I18n
from aiogram.utils.i18n import gettext as _

from bot.filters.is_authorized import IsAuthorized
from bot.filters.localized_text import LocalizedText
from bot.i18n import set_chat_commands
from bot.keyboards.reply import list_keyboard, settings_menu_keyboard
from bot.models import StudentSettings
from bot.services.api_client import ApiClient
from bot.services.settings_cache import SettingsCache
from bot.states import SettingsStates

router = Router(name="settings_menu")

LANGUAGE_OPTIONS: tuple[tuple[str, str], ...] = (
    ("🇺🇦 Українська", "uk"),
    ("🇷🇺 Русский", "ru"),
    ("🇬🇧 English", "en"),
)


def schedule_format_options() -> tuple[tuple[str, bool], ...]:
    return (
        (_("➡️⬅️ Компактний"), True),
        (_("⬅️➡️ Повноцінний"), False),
    )


def find_label(options: tuple[tuple[str, Any], ...], value: Any) -> str:
    return next((label for label, option in options if option == value), str(value))


def find_value(options: tuple[tuple[str, Any], ...], text: str | None) -> tuple[bool, Any]:
    for label, value in options:
        if label == text:
            return True, value
    return False, None


async def show_options(message: Message, state: FSMContext, target_state: Any,
                       options: tuple[tuple[str, Any], ...], current: Any) -> None:
    await state.clear()
    await state.set_state(target_state)
    await message.answer(
        _("Поточне значення: {value}").format(value=find_label(options, current)),
        reply_markup=list_keyboard([label for label, _value in options], back=True),
    )


async def save_settings(api: ApiClient, settings_cache: SettingsCache, settings: StudentSettings,
                        **changes: Any) -> StudentSettings:
    updated = await api.update_settings(settings.model_copy(update=changes))
    settings_cache.set(updated)
    return updated


@router.message(LocalizedText("🌍 Мова"), IsAuthorized())
async def show_language_options(message: Message, state: FSMContext, student_settings: StudentSettings) -> None:
    await show_options(message, state, SettingsStates.language, LANGUAGE_OPTIONS, student_settings.language)


@router.message(SettingsStates.language, IsAuthorized())
async def change_language(message: Message, state: FSMContext, bot: Bot, i18n: I18n, api: ApiClient,
                          settings_cache: SettingsCache, student_settings: StudentSettings) -> None:
    found, language = find_value(LANGUAGE_OPTIONS, message.text)

    if not found:
        await message.answer(_("Не коректне введення!"))
        return

    updated = await save_settings(api, settings_cache, student_settings, language=language)
    await state.clear()

    with i18n.use_locale(updated.language):
        await message.answer(
            _("Значення змінено на: {value}").format(value=find_label(LANGUAGE_OPTIONS, updated.language)),
            reply_markup=settings_menu_keyboard(),
        )

    await set_chat_commands(bot, i18n, message.chat.id, updated.language)


@router.message(LocalizedText("🗓 Формат розкладу"), IsAuthorized())
async def show_schedule_format_options(message: Message, state: FSMContext,
                                       student_settings: StudentSettings) -> None:
    await show_options(message, state, SettingsStates.schedule_format, schedule_format_options(),
                       student_settings.schedule_compact)


@router.message(SettingsStates.schedule_format, IsAuthorized())
async def change_schedule_format(message: Message, state: FSMContext, api: ApiClient,
                                 settings_cache: SettingsCache, student_settings: StudentSettings) -> None:
    options = schedule_format_options()
    found, compact = find_value(options, message.text)

    if not found:
        await message.answer(_("Не коректне введення!"))
        return

    updated = await save_settings(api, settings_cache, student_settings, schedule_compact=compact)
    await state.clear()
    await message.answer(
        _("Значення змінено на: {value}").format(value=find_label(options, updated.schedule_compact)),
        reply_markup=settings_menu_keyboard(),
    )
