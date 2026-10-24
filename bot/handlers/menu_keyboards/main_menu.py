from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from bot.filters.is_authorized import IsAuthorized
from bot.filters.localized_text import LocalizedText
from bot.keyboards.reply import (
    information_menu_keyboard,
    main_menu_keyboard,
    schedule_menu_keyboard,
    settings_menu_keyboard,
    submission_menu_keyboard,
)
from bot.states import SettingsStates

router = Router(name="main_menu")


@router.message(LocalizedText("📋 Головне меню"), IsAuthorized())
@router.message(StateFilter(None), LocalizedText("↩ Назад"), IsAuthorized())
async def open_main_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(_("📋 Головне меню"), reply_markup=main_menu_keyboard())


@router.message(LocalizedText("🗓 Розклад"), IsAuthorized())
async def open_schedule_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(_("🗓 Розклад"), reply_markup=schedule_menu_keyboard())


@router.message(LocalizedText("🗒 Інформація"), IsAuthorized())
async def open_information_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(_("🗒 Інформація"), reply_markup=information_menu_keyboard())


@router.message(StateFilter(SettingsStates), LocalizedText("↩ Назад"), IsAuthorized())
@router.message(LocalizedText("⚙ Налаштування"), IsAuthorized())
async def open_settings_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(_("⚙ Налаштування"), reply_markup=settings_menu_keyboard())


@router.message(LocalizedText("🧾 Захист робіт"), IsAuthorized())
async def open_submission_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(_("🧾 Захист робіт"), reply_markup=submission_menu_keyboard())
