import os
import json
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "PriceWatch India"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database (defaults to local SQLite if not configured or postgres is unavailable)
    DATABASE_URL: str = "sqlite:///./pricewatch.db"

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "changethisinproduction-supersecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # CORS
    BACKEND_CORS_ORIGINS: str = '["http://localhost:3000","http://localhost:5173"]'

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

    # Twilio (optional)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""

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

