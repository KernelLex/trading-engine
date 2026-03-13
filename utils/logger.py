"""
Logging utility for the Market Intelligence Layer.

Provides a ``get_logger`` factory that returns a named logger writing to both
the console and a rotating log file under ``logs/``.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from utils.config import LOG_DIR


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Return a configured logger with console + rotating-file handlers.

    Parameters
    ----------
    name:
        Logger name (typically ``__name__`` of the calling module).
    level:
        Minimum severity to capture.  Defaults to ``INFO``.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers when called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # --- Console handler ---------------------------------------------------
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # --- Rotating file handler ---------------------------------------------
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        LOG_DIR / "market_research.log",
        maxBytes=5 * 1024 * 1024,   # 5 MB per file
        backupCount=5,
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
