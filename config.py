
from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from enums import Language, City


class Telegram(BaseModel):
    bot_token: str
    languages: list[str] = [i.value for i in Language]
    cities: list[str] = [i.value for i in City]
    commands: list[str] = ["/start"]


class Database(BaseModel):
    uri: str
    name: str


class Logger(BaseModel):
    path: str = "resources/logs"
    level: str = "DEBUG"


class Resources(BaseModel):
    locales_path: str = "resources/locales"


class Settings(BaseSettings):
    telegram: Telegram
    database: Database
    logger: Logger
    resources: Resources

    model_config = SettingsConfigDict(
        env_file=f".env",
        case_sensitive=False,
        env_nested_delimiter="__",
    )


@lru_cache(maxsize=1)
def get_config() -> Settings:
    return Settings()
