from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SQL_DATABASE: str
    BROKER_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_DAYS: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    @property
    def DATABASE_URL_asyncpg(self):
        return f"sqlite+aiosqlite:///{self.SQL_DATABASE}"

    @property
    def DATABASE_URL_psycopg(self):
        return f"sqlite+aiosqlite:///{self.SQL_DATABASE}"

    model_config = SettingsConfigDict(env_file='.env.dev')

settings = Settings()
