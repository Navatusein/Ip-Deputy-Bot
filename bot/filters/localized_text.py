from aiogram.filters import Filter
from aiogram.types import Message
from aiogram.utils.i18n import I18n

from bot.i18n import translations_of


class LocalizedText(Filter):
    def __init__(self, msgid: str) -> None:
        self.msgid = msgid

    async def __call__(self, message: Message, i18n: I18n) -> bool:
        return message.text is not None and message.text in translations_of(i18n, self.msgid)
