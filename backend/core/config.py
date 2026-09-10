import os
import json
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"


BACKEND_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_FILE = (BACKEND_DIR / "pricewatch.db").as_posix()


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "PriceWatch India"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database (defaults to local SQLite if not configured or postgres is unavailable)
    DATABASE_URL: str = f"sqlite:///{DEFAULT_DB_FILE}"

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "changethisinproduction-supersecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # CORS
    BACKEND_CORS_ORIGINS: str = '["http://localhost:3000","http://localhost:5173","https://priceping.store","https://www.priceping.store","http://priceping.store","https://pingprice.store","https://www.pingprice.store"]'

    @property
    def cors_origins(self) -> List[str]:
        return json.loads(self.BACKEND_CORS_ORIGINS)

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = "noreply@pricewatch.in"
    EMAILS_FROM_NAME: str = "PriceWatch India"

    # Twilio (optional for SMS & WhatsApp)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    TWILIO_WHATSAPP_FROM: str = "whatsapp:+14155238886"  # Twilio Sandbox or verified WhatsApp number
    ADMIN_WHATSAPP_NUMBER: str = ""                       # e.g. "whatsapp:+919876543210"

    # Telegram Bot Alerts (100% Free instant admin notifications)
    TELEGRAM_BOT_TOKEN: str = ""                          # e.g. "123456789:ABCdefGHIjklMNOpqrSTUvwxYZ"
    TELEGRAM_ADMIN_CHAT_ID: str = ""                      # e.g. "987654321"

    # Price Tracking
    PRICE_CHECK_INTERVAL_MINUTES: int = 30
    PRICE_CHECK_INTERVAL_HOURS: int = 6
    MAX_RETRIES: int = 3
    REQUEST_TIMEOUT_SECONDS: int = 30
    CROSS_STORE_SEARCH_ENABLED: bool = True

    # Historical Providers
    # Keepa API key for Amazon price history (optional, free/paid key from keepa.com)
    KEEPA_API_KEY: str = ""

    # ScraperAPI (optional) - bypass Amazon/Flipkart bot protection
    # Get a free key at https://www.scraperapi.com (1000 free requests/month)
    SCRAPER_API_KEY: str = ""

    # Admin
    FIRST_SUPERUSER_EMAIL: str = "admin@pricewatch.in"
    FIRST_SUPERUSER_PASSWORD: str = "adminpassword123"

    model_config = {
        "env_file": (str(ENV_PATH), ".env"),
        "case_sensitive": False,
        "extra": "ignore",
    }


settings = Settings()

# BUG-017 / BUG-018 FIX: Refuse to start in production with default secrets.
# A missing .env or unconfigured deployment would silently use weak defaults,
# making all JWT tokens forgeable and leaving admin with a known password.
_WEAK_SECRET = "changethisinproduction-supersecretkey"
_WEAK_ADMIN_PASS = "adminpassword123"

if not settings.DEBUG:
    if settings.SECRET_KEY == _WEAK_SECRET:
        raise RuntimeError(
            "FATAL: SECRET_KEY is set to the insecure default value. "
            "Set a strong random SECRET_KEY in your environment before running in production."
        )
    if settings.FIRST_SUPERUSER_PASSWORD == _WEAK_ADMIN_PASS:
        import warnings
        warnings.warn(
            "WARNING: FIRST_SUPERUSER_PASSWORD is set to the insecure default 'adminpassword123'. "
            "Set a strong password in your environment.",
            RuntimeWarning,
            stacklevel=2,
        )

