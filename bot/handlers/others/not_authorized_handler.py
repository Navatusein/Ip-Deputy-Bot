from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from bot.filters.is_authorized import IsAuthorized
from bot.keyboards.reply import login_menu_keyboard

router = Router(name="not_authorized")


@router.message(~IsAuthorized())
async def request_authorization(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(_("Необхідно авторизуватися!"), reply_markup=login_menu_keyboard())
