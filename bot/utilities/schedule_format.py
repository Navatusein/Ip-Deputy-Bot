from datetime import date

from aiogram.utils.i18n import get_i18n
from aiogram.utils.i18n import gettext as _
from babel.dates import get_day_names

from bot.models import CoupleData, ScheduleDay, ScheduleWeek
from bot.utilities.text import link, number_emoji, quote


def weekday_name(day: date) -> str:
    return get_day_names("wide", locale=get_i18n().current_locale)[day.weekday()]


def format_day_schedule(schedule: ScheduleDay, day: date, is_today: bool) -> str:
    if is_today:
        title = _("<b>📅 Розклад на сьогодні — {weekday}, {date}:</b>")
    else:
        title = _("<b>📅 Розклад на завтра — {weekday}, {date}:</b>")

    header = title.format(weekday=weekday_name(day), date=quote(schedule.date))
    return f"{header}\n{format_couples(schedule)}"


def format_week_schedule(schedule: ScheduleWeek, is_current: bool, compact: bool) -> str:
    if is_current:
        parts = [_("<b>📅 Розклад на цей тиждень:</b>"), ""]
    else:
        parts = [_("<b>📅 Розклад на наступний тиждень:</b>"), ""]

    if compact and schedule.couple_times:
        parts.append(_("<b>Час пар:</b>"))
        parts.extend(f"{number_emoji(index + 1)} {quote(value)}" for index, value in enumerate(schedule.couple_times))
        parts.append("")

    day_names = get_day_names("wide", locale=get_i18n().current_locale)

    for index, schedule_day in enumerate(schedule.schedule_days):
        name = day_names[index % 7].upper()
        parts.append(f"<b>{quote(name)} ({quote(schedule_day.date)}):</b>")
        parts.append(format_couples(schedule_day, show_time=not compact))

    return "\n".join(parts)


def format_couples(schedule: ScheduleDay, show_time: bool = True) -> str:
    if not schedule.couples:
        return _("🛌 Пар немає, відпочивай!") + "\n"

    lines = [format_couple(couple, show_time) for couple in schedule.couples if couple.is_my_subgroup]
    other = [couple for couple in schedule.couples if not couple.is_my_subgroup]

    if other:
        lines.append("")
        lines.append(_("🚷 <i>Пари у іншої підгрупи:</i>"))
        lines.extend(f"<i>{format_couple(couple, show_time)}</i>" for couple in other)

    return "\n".join(lines) + "\n"


def format_couple(couple: CoupleData, show_time: bool) -> str:
    if couple.couple_index is None:
        prefix = _("⚠️ Нестандартний час:") + f"\n➖ [{quote(couple.time or '')}] "
    else:
        prefix = f"{number_emoji(couple.couple_index + 1)} "
        if show_time and couple.time:
            prefix += f"[{quote(couple.time)}] "

    subject = link(couple.subject, couple.link) if couple.link else quote(couple.subject)
    text = f"{prefix}{subject} ({quote(couple.subject_type)})"

    if couple.cabinet:
        text += " " + _("{cabinet} кб.").format(cabinet=quote(couple.cabinet))

    if couple.additional_information:
        text += f"\nℹ️ {quote(couple.additional_information)}"

    return text
