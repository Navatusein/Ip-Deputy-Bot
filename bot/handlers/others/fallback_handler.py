from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from bot.filters.is_authorized import IsAuthorized
from bot.keyboards.reply import main_menu_keyboard

router = Router(name="fallback")


@router.message(IsAuthorized())
async def handle_unknown_message(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(_("Не розумію 🤔 Скористайтеся меню нижче 👇"), reply_markup=main_menu_keyboard())
