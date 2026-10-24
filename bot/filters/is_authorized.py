from typing import Any

from aiogram.filters import Filter
from aiogram.types import Message


class IsAuthorized(Filter):
    async def __call__(self, message: Message, **data: Any) -> bool:
        return data.get("student_settings") is not None
