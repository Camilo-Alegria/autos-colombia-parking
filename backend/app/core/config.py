from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Autos Colombia API"
    database_url: str = "postgresql+psycopg2://postgres:Ca1891000*@localhost:5432/autos_colombia_db"
    cors_origins: list[str] = [
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "http://localhost:59178",
    ]


settings = Settings()
