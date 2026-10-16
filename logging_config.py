
import logging
import os


def configure_logging() -> None:
    log_level = os.getenv("SECUREAPP_LOG_LEVEL", "INFO").upper()

    numeric_level = getattr(logging, log_level, None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid SECUREAPP_LOG_LEVEL: {log_level}")

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[logging.StreamHandler()],
    )
