from zoneinfo import ZoneInfo

from aiogram.utils.i18n import gettext as _

from bot.models import SubmissionsConfig
from bot.utilities.text import quote, unique


def format_submission_list(config: SubmissionsConfig, tz: ZoneInfo) -> str:
    title = _("Список: <b>{name} ({type})</b>").format(name=quote(config.name), type=quote(config.type))
    students = unique([submission.student for submission in config.submissions])

    if not students:
        return f"{title}\n\n" + _("На захист ніхто не записався")

    lines = [title]

    if config.cleared_at is not None:
        cleared_at = config.cleared_at.astimezone(tz).strftime("%d.%m.%Y")
        lines.append(_("Остання чистка списку: <b>{date}</b>").format(date=cleared_at))

    rows = []
    for index, student in enumerate(students, start=1):
        works = ", ".join(quote(item.name) for item in config.submissions if item.student == student)
        rows.append(f"{index}) {quote(student)} ({quote(config.type)}): {works};")

    lines.append("")
    lines.append("<pre>" + "\n".join(rows) + "</pre>")
    return "\n".join(lines)
