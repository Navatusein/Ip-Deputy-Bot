import logging
import uuid

import httpx
from aiogram import F, Router
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import ErrorEvent, Message
from aiogram.utils.i18n import gettext as _

from bot.utilities.text import quote

router = Router(name="exceptions")
logger = logging.getLogger(__name__)


@router.error(ExceptionTypeFilter(httpx.TransportError), F.update.message.as_("message"))
async def handle_api_unavailable(event: ErrorEvent, message: Message) -> None:
    logger.error("API is unavailable: %s", type(event.exception).__name__)
    await message.answer(_("Упс, не можу під'єднатись до сервера!\nВикликайте фіксиків!"))


@router.error(F.update.message.as_("message"))
async def handle_unexpected_error(event: ErrorEvent, message: Message) -> None:
    code = uuid.uuid4().hex[:10]
    logger.error("[%s] Unhandled error: %s", code, event.exception, exc_info=event.exception)
    await message.answer(
        _("Упс, щось пішло не так.\nКод помилки: {code}").format(code=f"<code>{quote(code)}</code>")
    )


@router.error()
async def log_unexpected_error(event: ErrorEvent) -> None:
    logger.error("Unhandled error in update %s: %s", event.update.update_id, event.exception,
                 exc_info=event.exception)
