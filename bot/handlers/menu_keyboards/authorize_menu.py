import logging

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.i18n import I18n
from aiogram.utils.i18n import gettext as _

from bot.filters.is_authorized import IsAuthorized
from bot.i18n import locale_from_telegram, set_chat_commands
from bot.keyboards.reply import main_menu_keyboard
from bot.models import StudentContact
from bot.services.api_client import ApiClient, AuthorizationStatus
from bot.services.settings_cache import SettingsCache
from bot.utilities.text import quote

router = Router(name="authorize_menu")
logger = logging.getLogger(__name__)


@router.message(F.contact, ~IsAuthorized())
async def authorize_by_contact(message: Message, state: FSMContext, bot: Bot, i18n: I18n, api: ApiClient,
                               settings_cache: SettingsCache) -> None:
    user = message.from_user

    if message.contact.user_id != user.id:
        await message.answer(_("Це не ваш контакт!"))
        logger.warning("Authorization rejected: foreign contact was sent")
        return

    phone = "".join(symbol for symbol in message.contact.phone_number if symbol.isdigit())
    result = await api.authorize(StudentContact(telegram_id=user.id, phone=phone))

    if result.status is AuthorizationStatus.NOT_FOUND:
        logger.warning("Authorization failed [%s]: student not found", result.error_code)
        await message.answer(
            _("Вас немає у базі даних!\nНапишіть @Navatusein, код помилки: {code}").format(
                code=f"<code>{quote(result.error_code)}</code>"
            )
        )
        return

    if result.status is AuthorizationStatus.ALREADY_LINKED:
        logger.warning("Authorization failed: student is already linked to another account")
        await message.answer(
            _("Цей номер телефону вже прив'язаний до іншого Telegram-акаунта.\n"
              "Якщо це помилка, напишіть @Navatusein.")
        )
        return

    settings_cache.invalidate(user.id)
    settings = await api.get_settings(user.id)

    if settings is None:
        raise RuntimeError("Student settings are missing after successful authorization")

    preferred_language = locale_from_telegram(user.language_code)
    if settings.language != preferred_language:
        settings = await api.update_settings(settings.model_copy(update={"language": preferred_language}))

    settings_cache.set(settings)
    await state.clear()
    logger.info("Student authorized")

    with i18n.use_locale(settings.language):
        await message.answer(_("Авторизація виконана успішно!"), reply_markup=main_menu_keyboard())

    await set_chat_commands(bot, i18n, message.chat.id, settings.language)
