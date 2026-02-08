from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    environment: str = Field(default='local', alias='ENVIRONMENT')
    log_level: str = Field(default='INFO', alias='LOG_LEVEL')

    api_host: str = Field(default='0.0.0.0', alias='API_HOST')
    api_port: int = Field(default=8000, alias='API_PORT')
    cors_origins: str = Field(default='http://localhost:3000', alias='CORS_ORIGINS')

    database_url: str = Field(
        default='postgresql+asyncpg://finops:change_me@postgres:5432/finops',
        alias='DATABASE_URL',
    )
    redis_url: str = Field(default='redis://redis:6379/0', alias='REDIS_URL')
    tavily_api_key: str = Field(default='', alias='TAVILY_API_KEY')

    worker_max_jobs: int = Field(default=20, alias='WORKER_MAX_JOBS')


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
