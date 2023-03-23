"""
Этот модуль отвечает за загрузку переменных
окружения из файла .env с использованием
кэширования для повторного использования
данных для авторизации.

Переменная settings хранит данные для авторизации.
"""
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, Field, PostgresDsn, validator


class Settings(BaseSettings):
    """
    Модель данных в env.
    """

    USERS_PATH: str = Field(default="users.txt")

    CLIENT_ID: str
    CLIENT_SECRET: str

    POSTGRES: str = Field(default="postgresql")
    POSTGRES_DRIVER: str = Field(default="psycopg2")
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: str = Field(default="5432")
    POSTGRES_DB: str
    DATABASE_URI: Optional[PostgresDsn]

    @validator("DATABASE_URI")
    def generate_dsn(cls, value, values) -> str:
        if isinstance(value, str):
            return value
        dsn = PostgresDsn.build(
            scheme=f'{values.get("POSTGRES")}+{values.get("POSTGRES_DRIVER")}',
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),
            port=values.get("POSTGRES_PORT"),
            path=f'/{values.get("POSTGRES_DB") or ""}',
        )
        return dsn

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    """
    :return: Переменные окружения.

    Загружает переменные окружения из файла .env.
    """

    return Settings()


settings = get_settings()
