from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets
import warnings
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl


class Settings(BaseSettings):
    API_V1_STR: str = "/v1"
    PROJECT_NAME: str = "mychat"
    ORIGINS: list = ["*", ]
    openai_key: str
    claude_key: str
    gemini_key: str

    oss_access_key: str
    oss_access_key_secret: str
    oss_endpoint: str
    oss_role_arn: str
    oss_role_session_name: str
    oss_duration_seconds: int= 3600

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


    POSTGRES_SERVER: str = '127.0.0.1'
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: str = ''
    POSTGRES_DB: str = ''

    @computed_field  # type: ignore[misc]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

settings = Settings()