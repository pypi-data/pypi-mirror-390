"""
Comprehensive example of Python logging with Rich package for enhanced console output.
This example demonstrates custom formatting, different log levels, and Rich markup usage.
"""

import logging

from rich.console import Console
from rich.logging import RichHandler

# Install rich traceback handler for better error display
# from rich.traceback import install
# install(show_locals=True)

# Create a custom console instance for more control
console = Console(stderr=True, force_terminal=True)


class CustomRichHandler(RichHandler):
    """
    Custom Rich handler that provides different formatting for each log level.

    This extends ``RichHandler`` to customize the appearance of different log levels.
    """

    def __init__(self, **kwargs):
        kwargs.setdefault('console', console)
        super().__init__(**kwargs)

    def emit(self, record):
        """
        Custom emit method to handle different log level formatting.
        """
        # Store original message
        msg = record.getMessage()

        # Apply custom formatting based on log level
        if record.levelno >= logging.ERROR:
            record.msg = f'[red]{msg}[/red]'
        elif record.levelno >= logging.WARNING:
            record.msg = f'[yellow]{msg}[/yellow]'
        elif record.levelno >= logging.INFO:
            record.msg = msg
        elif record.levelno >= logging.DEBUG:
            record.msg = f'[dim]{msg}[/dim]'
        else:
            record.msg = f'[dim]{msg}[/dim]'

        # Clear args to prevent string interpolation from breaking Rich markup
        record.args = ()

        super().emit(record)


def get_logger(level=logging.DEBUG) -> logging.Logger:
    """
    Set up logging configuration with Rich handler and custom formatting.

    :param level: The minimum log level to display (default: DEBUG)
    :returns: Configured logger instance.
    """

    # Create logger
    _logger = logging.getLogger('typer-invoke')
    _logger.setLevel(level)
    _logger.handlers.clear()
    handler = CustomRichHandler(
        level=level,
        show_time=False,
        show_level=True,
        markup=True,
        rich_tracebacks=False,
    )

    # Set custom format string and add handler
    formatter = logging.Formatter(fmt='%(message)s', datefmt='[%X]')  # Time format: [HH:MM:SS]
    handler.setFormatter(formatter)
    _logger.addHandler(handler)

    # Prevent logs from being handled by root logger (avoid duplicate output)
    _logger.propagate = False

    return _logger


logger = get_logger()
