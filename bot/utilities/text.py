from html import escape

NUMBER_EMOJI = ("0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟")


def quote(value: object) -> str:
    return escape(str(value), quote=False)


def link(title: str, url: str) -> str:
    return f'<a href="{escape(url, quote=True)}">{quote(title)}</a>'


def number_emoji(number: int) -> str:
    if 0 <= number < len(NUMBER_EMOJI):
        return NUMBER_EMOJI[number]
    return f"{number}."


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def optional_line(template: str, value: object | None, **extra: object) -> str | None:
    if value is None or value == "":
        return None
    return template.format(value=quote(value), **extra)
