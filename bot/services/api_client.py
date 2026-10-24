import re
import uuid
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum
from typing import Any

import httpx

from bot.models import (
    LinkInformation,
    ScheduleDay,
    ScheduleWeek,
    StudentContact,
    StudentInformation,
    StudentSettings,
    SubjectInformation,
    SubmissionsConfig,
    TeacherInformation,
)

API_DATE_FORMAT = "%Y-%m-%d"
SCHEDULE_DATE_FORMAT = "%d.%m"
ERROR_CODE_PATTERN = re.compile(r"\[([A-Za-z0-9-]+)]")
LONG_NUMBER_PATTERN = re.compile(r"\d{5,}")


class ApiError(Exception):
    def __init__(self, status_code: int, method: str, path: str, message: str | None = None) -> None:
        self.status_code = status_code
        self.method = method
        self.path = path
        self.message = message
        super().__init__(f"API responded {status_code} to {method} {path}")

    @classmethod
    def from_response(cls, response: httpx.Response) -> "ApiError":
        message: str | None = None

        try:
            body = response.json()
        except ValueError:
            body = None

        if isinstance(body, dict):
            message = body.get("message") or body.get("title")
        elif isinstance(body, str):
            message = body
        elif response.text:
            message = response.text

        path = LONG_NUMBER_PATTERN.sub("<id>", response.request.url.path)
        return cls(response.status_code, response.request.method, path, message)


class AuthorizationStatus(Enum):
    SUCCESS = "success"
    NOT_FOUND = "not_found"
    ALREADY_LINKED = "already_linked"


@dataclass(frozen=True)
class AuthorizationResult:
    status: AuthorizationStatus
    error_code: str | None = None


class ApiClient:
    def __init__(self, base_url: str, token: str, timeout: float = 10.0) -> None:
        self._base_url = base_url
        self._token = token
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def open(self) -> None:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                headers={"X-BOT-TOKEN": self._token},
                timeout=httpx.Timeout(self._timeout),
            )

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("ApiClient is not opened")
        return self._client

    async def _request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        response = await self.client.request(method, url, **kwargs)

        if response.is_error:
            raise ApiError.from_response(response)

        return response

    async def authorize(self, contact: StudentContact) -> AuthorizationResult:
        try:
            await self._request("POST", "/authentication/authorize", json=contact.to_api())
        except ApiError as error:
            if error.status_code == 404:
                match = ERROR_CODE_PATTERN.search(error.message or "")
                code = match.group(1) if match else uuid.uuid4().hex[:8]
                return AuthorizationResult(AuthorizationStatus.NOT_FOUND, code)

            if error.status_code == 409:
                return AuthorizationResult(AuthorizationStatus.ALREADY_LINKED)

            raise

        return AuthorizationResult(AuthorizationStatus.SUCCESS)

    async def get_settings(self, telegram_id: int) -> StudentSettings | None:
        try:
            response = await self._request("GET", f"/student/settings/{telegram_id}")
        except ApiError as error:
            if error.status_code == 404:
                return None
            raise

        return StudentSettings.model_validate(response.json())

    async def update_settings(self, settings: StudentSettings) -> StudentSettings:
        response = await self._request("PUT", "/student/settings", json=settings.to_api())
        return StudentSettings.model_validate(response.json())

    async def update_last_activity(self, telegram_id: int) -> None:
        await self._request("PUT", f"/student/last-activity/{telegram_id}")

    async def get_students(self) -> list[StudentInformation]:
        response = await self._request("GET", "/information/students")
        return [StudentInformation.model_validate(item) for item in response.json()]

    async def get_teachers(self) -> list[TeacherInformation]:
        response = await self._request("GET", "/information/teachers")
        return [TeacherInformation.model_validate(item) for item in response.json()]

    async def get_subjects(self) -> list[SubjectInformation]:
        response = await self._request("GET", "/information/subjects")
        return [SubjectInformation.model_validate(item) for item in response.json()]

    async def get_links(self) -> list[LinkInformation]:
        response = await self._request("GET", "/information/links")
        return [LinkInformation.model_validate(item) for item in response.json()]

    async def get_day_schedule(self, telegram_id: int, day: date) -> ScheduleDay:
        response = await self._request(
            "GET",
            "/schedule/day",
            params={"telegramId": telegram_id, "dateString": day.strftime(API_DATE_FORMAT)},
        )

        if response.status_code == 204 or not response.content:
            return ScheduleDay(date=day.strftime(SCHEDULE_DATE_FORMAT))

        return ScheduleDay.model_validate(response.json())

    async def get_week_schedule(self, telegram_id: int, day: date) -> ScheduleWeek:
        response = await self._request(
            "GET",
            "/schedule/week",
            params={"telegramId": telegram_id, "dateString": day.strftime(API_DATE_FORMAT)},
        )

        if response.status_code == 204 or not response.content:
            monday = day - timedelta(days=day.weekday())
            days = [ScheduleDay(date=(monday + timedelta(days=i)).strftime(SCHEDULE_DATE_FORMAT)) for i in range(7)]
            return ScheduleWeek(schedule_days=days)

        return ScheduleWeek.model_validate(response.json())

    async def get_submissions_configs(self) -> list[SubmissionsConfig]:
        response = await self._request("GET", "/submission/submissions-configs")
        return [SubmissionsConfig.model_validate(item) for item in response.json()]
