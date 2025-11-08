"""Set up logging using the Loguru library."""

from __future__ import annotations

import inspect
import logging
import os
import sys
from pathlib import Path
from typing import Final

import logfire
from loguru import logger

# ----- Constants -----

# Log formats
STANDARD: Final = "[{time:HH:mm:ss}] {level} - {message}"
DETAIL: Final = "{time} {file:>25}:{line:<4} {level:<8} {message}"
ROTATION: Final = "1 hour"
RETENTION: Final = "2 days"

LOGFIRE_TOKEN: Final = os.getenv("LOGFIRE_TOKEN")


def configure_logging(
    log_filename: str | Path,
    *,
    standard_format: str = STANDARD,
    detail_format: str = DETAIL,
    log_rotation: str = ROTATION,
    log_retention: str = RETENTION,
) -> None:
    """Setup Loguru logging for the application."""
    # Capture things like Hishel logging
    intercept_logging()
    # Replace the default StdErr handler.
    logger.remove()
    logger.add(sys.stderr, level="WARNING", format=standard_format)

    log_filename = Path(log_filename).with_suffix(".log")

    # Add a rotating file handler.
    logger.add(
        log_filename,
        level="DEBUG",
        format=detail_format,
        rotation=log_rotation,
        retention=log_retention,
    )

    # Set up Logfire
    if LOGFIRE_TOKEN:
        logfire.configure(token=LOGFIRE_TOKEN)
        logger.add(logfire.loguru_handler()["sink"], level="DEBUG", format=detail_format)


# ----- Interface to the standard logging module -----


class InterceptHandler(logging.Handler):
    """Send logs to Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record."""
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:  # pragma: no cover
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def intercept_logging() -> None:
    """Intercept standard logging and send it to Loguru."""
    # Configure the root logger
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
