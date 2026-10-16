import os

from dotenv import load_dotenv

load_dotenv(override=False)

RATE_LIMIT = os.getenv("SECUREAPP_RATE_LIMIT", "5/minute")


ITEM_RATE_LIMIT = os.getenv(
    "SECUREAPP_ITEM_RATE_LIMIT",
    RATE_LIMIT,
)

REGISTER_RATE_LIMIT = os.getenv(
    "SECUREAPP_REGISTER_RATE_LIMIT",
    RATE_LIMIT,
)

LOGIN_RATE_LIMIT = os.getenv(
    "SECUREAPP_LOGIN_RATE_LIMIT",
    RATE_LIMIT,
)

SECRET_KEY = os.getenv("SECUREAPP_SECRET_KEY", "")

try:
    ACCESS_TOKEN_MINUTES = int(
        os.getenv("SECUREAPP_ACCESS_TOKEN_MINUTES", "30")
    )
except ValueError as exc:
    raise RuntimeError(
        "SECUREAPP_ACCESS_TOKEN_MINUTES must be a valid integer."
    ) from exc


if len(SECRET_KEY) < 32:
    raise RuntimeError(
        "SECUREAPP_SECRET_KEY must contain at least 32 characters. "
        "Set it in your environment or local .env file."
    )

if ACCESS_TOKEN_MINUTES <= 0:
    raise RuntimeError(
        "SECUREAPP_ACCESS_TOKEN_MINUTES must be greater than zero."
    )
