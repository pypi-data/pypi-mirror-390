"""dive-logger: A colorful and feature-rich logging utility for Python."""

__version__ = "0.1.1" 

from .logger import Logger, ColorFormatter, logger, handle_extraction_error

__all__ = ["Logger", "ColorFormatter", "logger", "handle_extraction_error"]