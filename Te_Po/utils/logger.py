import logging
from typing import Optional

_LOGGER_NAME = "tiwhanawhana"


def get_logger(name: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(name or _LOGGER_NAME)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
