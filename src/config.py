from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    BOT_TOKEN: SecretStr
    GITHUB_TOKEN: SecretStr

    DB_USER: str = "postgres"
    DB_PASSWORD: SecretStr
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def DB_URL(self) -> SecretStr:
        url = (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD.get_secret_value()}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
        return SecretStr(url)


config = Config(**{})
