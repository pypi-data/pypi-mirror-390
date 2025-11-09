"""
Logging Configuration Module (Loguru Version)

Provides unified logging configuration and output.
"""

import logging
import sys
from loguru import logger


class InterceptHandler(logging.Handler):
    """Redirects Python standard logging to Loguru"""

    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        # Locate original call position
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(log_level: str = "DEBUG", log_file: str = "logs/app.log") -> None:
    """
    Configure Loguru logging system

    Args:
        log_file: Log file path, defaults to 'app.log'
        log_level: Log level
    """
    # Remove Loguru default handler
    logger.remove()

    # Define log output format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{module}</cyan>.<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # Output to console
    logger.add(sys.stdout, format=log_format, level="DEBUG")

    # Output to log file (daily rotation + compression)
    logger.add(
        log_file,
        format=log_format,
        level=log_level,
        rotation="00:00",  # Daily rotation at midnight
        retention="7 days",  # Keep for 7 days
        compression="zip",  # Compress old logs
        encoding="utf-8",
        enqueue=True,  # Async write to prevent I/O blocking
    )

    # Take over standard library logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Take over Uvicorn / FastAPI internal logging
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        lib_logger = logging.getLogger(name)
        lib_logger.handlers = [InterceptHandler()]
        lib_logger.propagate = False


def get_logger(name: str = None):
    """
    Get Loguru logger

    Args:
        name: Module name or logger name (optional)

    Returns:
        logger: Loguru logger object
    """
    if name:
        return logger.bind(module=name)
    return logger
