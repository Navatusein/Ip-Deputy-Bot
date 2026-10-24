from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel

LEGACY_DATETIME_FORMATS = (
    "%m/%d/%Y %I:%M:%S %p",
    "%m/%d/%Y %H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%m/%d/%Y",
    "%d.%m.%Y",
)


class ApiModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    def to_api(self) -> dict[str, Any]:
        return self.model_dump(mode="json", by_alias=True)


class StudentSettings(ApiModel):
    telegram_id: int
    language: str
    schedule_compact: bool = False


class StudentContact(ApiModel):
    telegram_id: int
    phone: str


class CoupleData(ApiModel):
    subject: str
    subject_type: str
    couple_index: int | None = None
    is_my_subgroup: bool = True
    time: str | None = None
    link: str | None = None
    cabinet: str | None = None
    additional_information: str | None = None


class ScheduleDay(ApiModel):
    date: str
    couples: list[CoupleData] = Field(default_factory=list)


class ScheduleWeek(ApiModel):
    couple_times: list[str] = Field(default_factory=list)
    schedule_days: list[ScheduleDay] = Field(default_factory=list)


class StudentInformation(ApiModel):
    name: str
    surname: str
    patronymic: str | None = None
    subgroup: str | None = None
    contact_phone: str | None = None
    telegram_phone: str | None = None
    email: str | None = None
    fit_email: str | None = None
    telegram_nickname: str | None = None
    birthday: str | None = None

    @property
    def full_name(self) -> str:
        return f"{self.surname} {self.name}"


class TeacherInformation(ApiModel):
    name: str
    surname: str
    patronymic: str | None = None
    contact_phone: str | None = None
    email: str | None = None
    fit_email: str | None = None
    telegram_nickname: str | None = None

    @property
    def full_name(self) -> str:
        return " ".join(part for part in (self.surname, self.name, self.patronymic) if part)


class SubjectInformation(ApiModel):
    name: str
    short_name: str | None = None
    laboratory_days_count: int = 0
    practical_days_count: int = 0
    lectures_days_count: int = 0
    laboratory_count: int = 0
    practical_count: int = 0


class LinkInformation(ApiModel):
    name: str
    description: str | None = None
    url: str


class Submission(ApiModel):
    name: str
    student: str


class SubmissionsConfig(ApiModel):
    id: int
    name: str
    type: str
    subgroup: str | None = None
    cleared_at: datetime | None = None
    submissions: list[Submission] = Field(default_factory=list)

    @field_validator("cleared_at", mode="before")
    @classmethod
    def parse_cleared_at(cls, value: Any) -> Any:
        if value is None or isinstance(value, datetime):
            return value

        if not isinstance(value, str) or not value.strip():
            return None

        text = value.strip()

        try:
            return datetime.fromisoformat(text)
        except ValueError:
            pass

        for date_format in LEGACY_DATETIME_FORMATS:
            try:
                return datetime.strptime(text, date_format)
            except ValueError:
                continue

        return None

    @field_validator("cleared_at")
    @classmethod
    def ensure_timezone(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value
