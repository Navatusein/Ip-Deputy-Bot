from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.i18n import gettext as _


def web_app_keyboard(frontend_url: str, path: str) -> InlineKeyboardMarkup:
    web_app = WebAppInfo(url=f"{frontend_url}/bot-web-app{path}")
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=_("Відкрити інтерфейс"), web_app=web_app)]])


def link_keyboard(text: str, url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=text, url=url)]])
