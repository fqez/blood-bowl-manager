"""Centralized logging configuration for Blood Bowl Manager API."""

import logging
import sys


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Create and configure a logger instance.

    Args:
        name: Logger name (typically __name__ of the module)
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


# Pre-configured loggers for common modules
def get_api_logger() -> logging.Logger:
    """Get logger for API routes."""
    return setup_logger("api")


def get_db_logger() -> logging.Logger:
    """Get logger for database operations."""
    return setup_logger("database")


def get_service_logger() -> logging.Logger:
    """Get logger for service layer."""
    return setup_logger("services")
