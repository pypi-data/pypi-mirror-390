"""Logging configuration for TogoMQ SDK."""

import logging


class LogLevel:
    """Log level constants."""

    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    NONE = "none"


_LEVEL_MAP = {
    LogLevel.DEBUG: logging.DEBUG,
    LogLevel.INFO: logging.INFO,
    LogLevel.WARN: logging.WARNING,
    LogLevel.ERROR: logging.ERROR,
    LogLevel.NONE: logging.CRITICAL + 10,  # Effectively disable logging
}


def setup_logger(name: str, level: str = LogLevel.INFO) -> logging.Logger:
    """Set up a logger for TogoMQ.

    Args:
        name: The name of the logger.
        level: The log level (debug, info, warn, error, none).

    Returns:
        A configured logger instance.
    """
    logger = logging.getLogger(name)

    # Remove any existing handlers
    logger.handlers = []

    # Set the log level
    log_level = _LEVEL_MAP.get(level.lower(), logging.INFO)
    logger.setLevel(log_level)

    # Don't propagate to root logger
    logger.propagate = False

    # Only add handler if not "none"
    if level.lower() != LogLevel.NONE:
        handler = logging.StreamHandler()
        handler.setLevel(log_level)

        # Create formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: The name of the logger.

    Returns:
        A logger instance.
    """
    return logging.getLogger(name)
