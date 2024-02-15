from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class RedisSettings(BaseSettings):
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @property
    def redis_url(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


class BotSettings(BaseSettings):
    BOT_TOKEN: str
    BOT_NOTIFY_USER_ID: int


class KworkSettings(BaseSettings):
    KWORK_LOGIN: str
    KWORK_PASSWORD: str
    KWORK_PHONE_LAST: str
    KWORK_CATEGORIES: list[int]

    KWORK_PRICE_FROM: int | None = None
    KWORK_PRICE_TO: int | None = None
    KWORK_HIRING_FROM: int | None = None
    KWORK_KWORKS_FILTER_FROM: int | None = None
    KWORK_KWORKS_FILTER_TO: int | None = None


class ScheduleSettings(BaseSettings):
    SCHEDULE_PARSE_KWORK_MINUTES: int = 10


class Settings(RedisSettings, BotSettings, KworkSettings, ScheduleSettings):
    LOG_LEVEL: str = "INFO"


settings = Settings()
