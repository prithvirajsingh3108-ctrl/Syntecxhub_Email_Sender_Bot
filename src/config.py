# src/config.py
# Loads and validates environment variables for SMTP configuration

import os
from dotenv import load_dotenv

# Load .env file from the project root
load_dotenv()


class Config:
    """Holds all configuration values loaded from the .env file."""

    EMAIL_ADDRESS: str = os.getenv("EMAIL_ADDRESS", "")
    EMAIL_APP_PASSWORD: str = os.getenv("EMAIL_APP_PASSWORD", "")
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))

    @classmethod
    def validate(cls) -> list[str]:
        """
        Check that all required credentials are present.
        Returns a list of error messages; empty list means all good.
        """
        errors = []
        if not cls.EMAIL_ADDRESS:
            errors.append("EMAIL_ADDRESS is missing from .env file.")
        if not cls.EMAIL_APP_PASSWORD:
            errors.append("EMAIL_APP_PASSWORD is missing from .env file.")
        if not cls.SMTP_SERVER:
            errors.append("SMTP_SERVER is missing from .env file.")
        if not cls.SMTP_PORT:
            errors.append("SMTP_PORT is missing or invalid in .env file.")
        return errors
