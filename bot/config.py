import os
from functools import lru_cache
from zoneinfo import ZoneInfo

from pydantic import SecretStr, field_validator
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

CONFIG_FILE = os.getenv("CONFIG_FILE", "config/config.json")


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        json_file=CONFIG_FILE,
        json_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: SecretStr
    api_token: SecretStr
    api_url: str
    api_timeout: float = 10.0
    frontend_url: str
    webhook_url: str
    webhook_path: str = "/bot-webhook"
    webhook_secret: SecretStr
    webserver: str = "0.0.0.0"
    port: int = 7540
    time_zone: str = "Europe/Kyiv"
    log_level: str = "INFO"
    log_file: str | None = None

    @field_validator("api_url", "frontend_url", "webhook_url")
    @classmethod
    def strip_trailing_slash(cls, value: str) -> str:
        return value.rstrip("/")

    @field_validator("webhook_path")
    @classmethod
    def ensure_leading_slash(cls, value: str) -> str:
        return value if value.startswith("/") else f"/{value}"

    @field_validator("time_zone")
    @classmethod
    def validate_time_zone(cls, value: str) -> str:
        ZoneInfo(value)
        return value

    @field_validator("log_file")
    @classmethod
    def empty_log_file_to_none(cls, value: str | None) -> str | None:
        return value or None

    @property
    def tz(self) -> ZoneInfo:
        return ZoneInfo(self.time_zone)

    @property
    def webhook_full_url(self) -> str:
        return f"{self.webhook_url}{self.webhook_path}"

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            JsonConfigSettingsSource(settings_cls),
            file_secret_settings,
        )


@lru_cache
def load_config() -> Config:
    return Config()
