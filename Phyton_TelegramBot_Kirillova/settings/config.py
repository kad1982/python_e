import os
from pydantic import SecretStr, PostgresDsn, Secret, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), ".envs/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # из .env
    TELEGRAM_API_KEY: SecretStr
    LOG_LEVEL: str = "INFO"

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: SecretStr

    @computed_field
    @property
    def POSTGRES_DSN(self) -> SecretStr:
        return SecretStr(
            f"postgresql+asyncpg://{self.DB_USER}:"
            f"{self.DB_PASSWORD.get_secret_value()}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
    def POSTGRES_DSN_SYNC(self) -> SecretStr:
        return SecretStr(
            f"postgresql+psycopg2://{self.DB_USER}:"
            f"{self.DB_PASSWORD.get_secret_value()}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


    ADMIN_INTERFACE_PORT: int = 8001
    ADMIN_SECRET_KEY: SecretStr = SecretStr("secretkey")
    ADMIN_LOGIN: SecretStr = SecretStr("admin")
    ADMIN_PASSWORD: SecretStr = SecretStr("admin")

    def PERSISTANCE_POSTGRES_DSN(self) -> SecretStr:
        return SecretStr(
            f"postgresql://{self.DB_USER}:"
            f"{self.DB_PASSWORD.get_secret_value()}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

settings = AppSettings()
