from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    key: str = ""
    download_key: str = ""
    update_time: str = "12:00"
    db_path: str = "data"
    port: int = 8000
    ipv4_baseurl: str = ""
    ipv6_baseurl: str = ""


settings = Settings()
