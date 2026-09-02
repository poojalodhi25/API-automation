"""Load environment variables with python-dotenv and validate them with Pydantic."""

import os
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parents[2]
APP_DIR = BASE_DIR / "app"
load_dotenv(BASE_DIR / ".env")


class Settings(BaseModel):
    """Application settings. Values come from .env / environment variables."""

    app_name: str = Field(default="HireFlow Full-Time Automation")
    app_env: str = Field(default="development")
    debug: bool = Field(default=True)
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000)

    mysql_host: str = Field(default="localhost")
    mysql_port: int = Field(default=3306)
    mysql_user: str = Field(default="root")
    mysql_password: str = Field(default="")
    mysql_database: str = Field(default="hireflow_fulltime")

    gemini_api_key: str = Field(default="")
    gemini_model: str = Field(default="gemini-2.0-flash")

    gmail_client_id: str = Field(default="")
    gmail_client_secret: str = Field(default="")
    gmail_redirect_uri: str = Field(default="http://127.0.0.1:8000/api/gmail/callback")
    gmail_sender_email: str = Field(default="")
    gmail_cc_email: str = Field(default="")
    gmail_bcc_email: str = Field(default="")

    usajobs_api_key: str = Field(default="")
    usajobs_user_agent: str = Field(default="HireFlow/1.0 (your_email@example.com)")

    adzuna_app_id: str = Field(default="")
    adzuna_app_key: str = Field(default="")

    followup_after_days: int = Field(default=7)
    email_send_delay_seconds: int = Field(default=3)

    @property
    def database_url(self) -> str:
        """SQLAlchemy connection URL for MySQL."""
        password = quote_plus(self.mysql_password)
        return (
            f"mysql+pymysql://{self.mysql_user}:{password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    @property
    def gmail_token_path(self) -> Path:
        return BASE_DIR / "logs" / "gmail_token.json"

    @property
    def gemini_ready(self) -> bool:
        return bool(self.gemini_api_key.strip())

    @property
    def gmail_oauth_ready(self) -> bool:
        return bool(self.gmail_client_id.strip() and self.gmail_client_secret.strip())


def _as_bool(value: str, default: bool = True) -> bool:
    if value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_settings() -> Settings:
    """Build Settings from environment variables."""
    return Settings(
        app_name=os.getenv("APP_NAME", "HireFlow Full-Time Automation"),
        app_env=os.getenv("APP_ENV", "development"),
        debug=_as_bool(os.getenv("DEBUG", "true")),
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        mysql_host=os.getenv("MYSQL_HOST", "localhost"),
        mysql_port=int(os.getenv("MYSQL_PORT", "3306")),
        mysql_user=os.getenv("MYSQL_USER", "root"),
        mysql_password=os.getenv("MYSQL_PASSWORD", ""),
        mysql_database=os.getenv("MYSQL_DATABASE", "hireflow_fulltime"),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        gmail_client_id=os.getenv("GMAIL_CLIENT_ID", ""),
        gmail_client_secret=os.getenv("GMAIL_CLIENT_SECRET", ""),
        gmail_redirect_uri=os.getenv(
            "GMAIL_REDIRECT_URI", "http://127.0.0.1:8000/api/gmail/callback"
        ),
        gmail_sender_email=os.getenv("GMAIL_SENDER_EMAIL", ""),
        gmail_cc_email=os.getenv("GMAIL_CC_EMAIL", ""),
        gmail_bcc_email=os.getenv("GMAIL_BCC_EMAIL", ""),
        usajobs_api_key=os.getenv("USAJOBS_API_KEY", ""),
        usajobs_user_agent=os.getenv(
            "USAJOBS_USER_AGENT", "HireFlow/1.0 (your_email@example.com)"
        ),
        adzuna_app_id=os.getenv("ADZUNA_APP_ID", ""),
        adzuna_app_key=os.getenv("ADZUNA_APP_KEY", ""),
        followup_after_days=int(os.getenv("FOLLOWUP_AFTER_DAYS", "7")),
        email_send_delay_seconds=int(os.getenv("EMAIL_SEND_DELAY_SECONDS", "3")),
    )


@lru_cache
def get_settings() -> Settings:
    return load_settings()


settings = get_settings()
