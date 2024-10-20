from . import client

from bot.models.student_contact import StudentContact


class AuthenticationService:
    @staticmethod
    def authorize(contact: StudentContact) -> [bool, str | None]:
        response = client.post("/authentication/authorize", json=contact.to_dict())

        if response.status_code == 404:
            return False, response.text

        response.raise_for_status()

        return True, ""
