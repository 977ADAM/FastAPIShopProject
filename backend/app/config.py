import json

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict
from typing import List
from typing_extensions import Annotated


class Settings(BaseSettings):
    app_name: str = "FastAPI Shop"
    debug: bool = True
    database_url: str = "sqlite:///./shop.db"
    # NoDecode disables pydantic-settings' automatic JSON decoding so the raw
    # env string reaches assemble_cors_origins below.
    cors_origins: Annotated[List[str], NoDecode] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    static_dir: str = "static"
    images_dir: str = "static/images"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, value):
        """Allow CORS_ORIGINS to be a comma-separated string or a JSON list.

        pydantic-settings tries to JSON-decode list fields from env vars, which
        breaks for the plain comma-separated form used in docker-compose
        (e.g. ``CORS_ORIGINS=https://a.com,https://b.com``). This normalizes
        both forms into a list of stripped origins.
        """
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("["):
                return json.loads(stripped)
            return [origin.strip() for origin in stripped.split(",") if origin.strip()]
        return value


settings = Settings()
