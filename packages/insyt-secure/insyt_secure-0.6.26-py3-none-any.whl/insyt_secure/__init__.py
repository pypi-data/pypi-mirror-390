"""Insyt Secure package."""

__version__ = "0.1.6"

from .utils.logging_config import configure_logging, LoggingFormat

__all__ = ['configure_logging', 'LoggingFormat']