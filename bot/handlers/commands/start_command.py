from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from bot.filters.is_authorized import IsAuthorized
from bot.keyboards.reply import main_menu_keyboard

router = Router(name="start_command")


@router.message(CommandStart(), IsAuthorized())
async def show_main_menu_on_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(_("📋 Головне меню"), reply_markup=main_menu_keyboard())
