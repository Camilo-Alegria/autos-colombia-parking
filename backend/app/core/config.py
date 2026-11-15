from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Autos Colombia API"
    database_url: str = "postgresql+psycopg2://postgres:Ca1891000*@localhost:5432/autos_colombia_db"
    jwt_secret: str = "autos_colombia_super_secret_jwt_key_2026"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    cors_origins: list[str] = [
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "http://localhost:59178",
        "*",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
