from collections.abc import Iterable

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.i18n import gettext as _


def _markup(rows: list[list[str]]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=text) for text in row] for row in rows],
        resize_keyboard=True,
    )


def list_keyboard(items: Iterable[str], *, main_menu: bool = False, back: bool = False) -> ReplyKeyboardMarkup:
    rows: list[list[str]] = []

    if main_menu:
        rows.append([_("📋 Головне меню")])

    if back:
        rows.append([_("↩ Назад")])

    rows.extend([item] for item in items)
    return _markup(rows)


def back_main_keyboard() -> ReplyKeyboardMarkup:
    return _markup([[_("📋 Головне меню")], [_("↩ Назад")]])


def login_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=_("🔐 Авторизуватися"), request_contact=True)]],
        resize_keyboard=True,
    )


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return _markup([
        [_("🗓 Розклад"), _("🧾 Захист робіт")],
        [_("🗒 Інформація")],
        [_("⚙ Налаштування")],
    ])


def schedule_menu_keyboard() -> ReplyKeyboardMarkup:
    return _markup([
        [_("📋 Головне меню")],
        [_("🕐 Сьогодні"), _("🕑 Завтра")],
        [_("🕐 Цей тиждень"), _("🕑 Наступний тиждень")],
    ])


def information_menu_keyboard() -> ReplyKeyboardMarkup:
    return _markup([
        [_("📋 Головне меню")],
        [_("🧑‍🎓 Студенти"), _("🧑🏻‍🏫 Викладачі")],
        [_("📖 Предмети"), _("🌐 Посилання")],
    ])


def settings_menu_keyboard() -> ReplyKeyboardMarkup:
    return _markup([
        [_("📋 Головне меню")],
        [_("🌍 Мова")],
        [_("🗓 Формат розкладу")],
    ])


def submission_menu_keyboard() -> ReplyKeyboardMarkup:
    return _markup([
        [_("📋 Головне меню")],
        [_("➕ Записатись"), _("🧾 Мої записи")],
        [_("🗳 Отримати список")],
    ])
