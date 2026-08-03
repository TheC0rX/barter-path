from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    BOT_TOKEN: SecretStr
    PAT_TOKEN: SecretStr

    POSTGRES_USER: SecretStr
    POSTGRES_PASS: SecretStr
    POSTGRES_HOST: SecretStr
    POSTGRES_PORT: SecretStr
    POSTGRES_DB: SecretStr

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def db_url(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.POSTGRES_USER.get_secret_value()}:{self.POSTGRES_PASS.get_secret_value()}"
            f"@{self.POSTGRES_HOST.get_secret_value()}:{self.POSTGRES_PORT.get_secret_value()}"
            f"/{self.POSTGRES_DB.get_secret_value()}"
        )


config = Config(**{})
