from . import client

from bot.models.student_settings import StudentSettings


class StudentService:
    @staticmethod
    def get_settings(telegram_id: int) -> StudentSettings | None:
        response = client.get(f"/student/settings/{telegram_id}")

        if response.status_code == 404:
            return None

        response.raise_for_status()

        return StudentSettings.from_dict(response.json())

    @staticmethod
    def update_settings(settings: StudentSettings) -> StudentSettings:
        response = client.put("/student/settings", json=settings.to_dict())
        response.raise_for_status()
        return StudentSettings.from_dict(response.json())

    @staticmethod
    def update_last_activity(telegram_id: int) -> None:
        response = client.put(f"/student/last-activity/{telegram_id}")
        response.raise_for_status()
