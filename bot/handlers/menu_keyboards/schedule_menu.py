from datetime import date, datetime, timedelta

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.config import Config
from bot.filters.is_authorized import IsAuthorized
from bot.filters.localized_text import LocalizedText
from bot.models import StudentSettings
from bot.services.api_client import ApiClient
from bot.utilities.schedule_format import format_day_schedule, format_week_schedule

router = Router(name="schedule_menu")


def today(config: Config) -> date:
    return datetime.now(config.tz).date()


def week_start(day: date) -> date:
    return day - timedelta(days=day.weekday())


async def send_day_schedule(message: Message, api: ApiClient, settings: StudentSettings, day: date,
                            is_today: bool) -> None:
    schedule = await api.get_day_schedule(settings.telegram_id, day)
    await message.answer(format_day_schedule(schedule, day, is_today))


async def send_week_schedule(message: Message, api: ApiClient, settings: StudentSettings, day: date,
                             is_current: bool) -> None:
    schedule = await api.get_week_schedule(settings.telegram_id, day)
    await message.answer(format_week_schedule(schedule, is_current, settings.schedule_compact))


@router.message(Command("today"), IsAuthorized())
@router.message(LocalizedText("🕐 Сьогодні"), IsAuthorized())
async def send_today_schedule(message: Message, api: ApiClient, config: Config,
                              student_settings: StudentSettings) -> None:
    await send_day_schedule(message, api, student_settings, today(config), is_today=True)


@router.message(Command("tomorrow"), IsAuthorized())
@router.message(LocalizedText("🕑 Завтра"), IsAuthorized())
async def send_tomorrow_schedule(message: Message, api: ApiClient, config: Config,
                                 student_settings: StudentSettings) -> None:
    await send_day_schedule(message, api, student_settings, today(config) + timedelta(days=1), is_today=False)


@router.message(Command("this_week"), IsAuthorized())
@router.message(LocalizedText("🕐 Цей тиждень"), IsAuthorized())
async def send_this_week_schedule(message: Message, api: ApiClient, config: Config,
                                  student_settings: StudentSettings) -> None:
    await send_week_schedule(message, api, student_settings, week_start(today(config)), is_current=True)


@router.message(Command("next_week"), IsAuthorized())
@router.message(LocalizedText("🕑 Наступний тиждень"), IsAuthorized())
async def send_next_week_schedule(message: Message, api: ApiClient, config: Config,
                                  student_settings: StudentSettings) -> None:
    next_week = week_start(today(config)) + timedelta(days=7)
    await send_week_schedule(message, api, student_settings, next_week, is_current=False)
