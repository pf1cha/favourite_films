from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    OMDB_API_KEY: str = Field()
    DB_NAME: str = Field()
    DB_USER: str = Field()
    DB_PASSWORD: str = Field()
    DB_HOST: str = Field()
    DB_PORT: str = Field()

    model_config = SettingsConfigDict(env_file="config.env")


settings = Settings()
