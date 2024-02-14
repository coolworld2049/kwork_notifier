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
    BOT_ACL_USER_IDS: list[int] = []
    BOT_ACL_ENABLED: bool = True


class KworkSettings(BaseSettings):
    KWORK_LOGIN: str
    KWORK_PASSWORD: str
    KWORK_PHONE_LAST: int
    KWORK_CATEGORIES: list[int] = [41, 255]


class Settings(RedisSettings, BotSettings, KworkSettings):
    LOG_LEVEL: str = "INFO"


settings = Settings()
