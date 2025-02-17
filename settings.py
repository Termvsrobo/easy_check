from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    class Config(SettingsConfigDict):
        env_file = '.env'
    DB_URL: str = "sqlite:///db.sqlite3"


settings = Settings()
