from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str
    app_name: str
    app_host: str
    app_port: int
    log_level: str

    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_expire_minutes: int

    s3_endpoint_url: str
    s3_region: str
    s3_bucket: str
    s3_access_key: str
    s3_secret_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


def load_settings() -> Settings:
    """
    Load settings from environment variables.
    Raises a RuntimeError with explicit missing/invalid fields to make startup
    failures easy to understand for developers.
    """
    try:
        return Settings()
    except ValidationError as exc:
        missing_or_invalid = ", ".join(
            ".".join(str(part) for part in err["loc"]) for err in exc.errors()
        )
        raise RuntimeError(
            "Configuration error: missing or invalid required settings -> "
            f"{missing_or_invalid}. Create backend/.env from backend/.env.example."
        ) from exc
