import json
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict
from typing_extensions import Annotated


class Settings(BaseSettings):
    app_name: str = "Канцелярия №1"
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

    # --- Admin auth (JWT) ---
    admin_username: str = "admin"
    # bcrypt hash of the admin password. Default is the hash of "admin" — for
    # local dev only; override ADMIN_PASSWORD_HASH in production.
    admin_password_hash: str = (
        "$2b$12$pUIrXrlsNgvNKu11CZH1l.tDUOv3FIpzfVMnS6q769d5k4ZobXI1u"
    )
    jwt_secret: str = "change-me-in-production-with-a-long-random-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

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
