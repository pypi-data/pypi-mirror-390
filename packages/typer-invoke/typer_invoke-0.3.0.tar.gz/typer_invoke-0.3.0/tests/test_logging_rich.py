import logging

import pytest
from rich.console import Console

from src.logging_rich import get_logger


@pytest.fixture(scope='module')
def console():
    return Console(stderr=True, force_terminal=True)


@pytest.fixture(scope='module')
def logger():
    return get_logger(level=logging.DEBUG)


def test_demonstrate_log_levels(console, logger):
    """
    Demonstrate different log levels with various message types.
    """

    console.print('\n[bold blue]🚀 Demonstrating Different Log Levels[/bold blue]')
    console.print('=' * 60)

    # DEBUG level messages
    logger.debug('This is a debug message for troubleshooting')
    logger.debug('Debug info: Processing user ID 12345')
    logger.debug('Variable values: x=10, y=20, result=30')

    # INFO level messages
    logger.info('Application started successfully')
    logger.info('Processing 150 records from database')
    logger.info('User authentication completed for: john.doe@example.com')

    # WARNING level messages
    logger.warning('Configuration file not found, using defaults')
    logger.warning('API rate limit approaching: 90% of quota used')
    logger.warning('Deprecated function called: use new_function() instead')

    # ERROR level messages
    logger.error('Failed to connect to database server')
    logger.error('Invalid user credentials provided')
    logger.error('File not found: /path/to/missing/file.txt')


def test_demonstrate_rich_markup(console, logger):
    """
    Demonstrate Rich markup syntax in log messages.
    """

    console.print('\n[bold blue]🎨 Demonstrating Rich Markup in Log Messages[/bold blue]')
    console.print('=' * 60)

    # Rich markup examples in different log levels
    logger.info(
        'Processing user [bold cyan]Alice Johnson[/bold cyan] with ID [yellow]#12345[/yellow]'
    )

    logger.info(
        'Status: '
        '[green]✓ Connected[/green] | Records: [blue]1,234[/blue] | Time: [magenta]1.5s[/magenta]'
    )

    logger.warning(
        'Performance issue detected: '
        'Response time [red]2.5s[/red] exceeds threshold [yellow]2.0s[/yellow]'
    )

    logger.info(
        'Available commands: [italic]start[/italic], [italic]stop[/italic], '
        '[italic]restart[/italic], [italic]status[/italic]'
    )

    logger.debug('Memory usage: [dim]RAM: 4.2GB/8GB | CPU: 45%[/dim]')

    # Demonstrate code highlighting
    logger.info('Executing function: [bold green]process_data()[/bold green]')

    # Demonstrate nested markup
    logger.info(
        '[bold]Operation completed:[/bold] '
        '[green]✓ Success[/green] ([italic]took 0.25 seconds[/italic])'
    )


def test_demonstrate_error_handling(console, logger):
    """
    Demonstrate error logging with stack traces.
    """

    console.print('\n[bold blue]🐛 Demonstrating Error Handling with Stack Traces[/bold blue]')
    console.print('=' * 60)

    try:
        # Intentionally cause an error for demonstration
        10 / 0
    except ZeroDivisionError as e:
        logger.error(f'Mathematical error occurred: {e}', exc_info=True)

    try:
        # Another example with file operations
        with open('nonexistent_file.txt') as f:
            f.read()
    except FileNotFoundError as e:
        logger.error(f'File operation failed: {e}')
        logger.debug('Attempted to read from nonexistent_file.txt', exc_info=True)


def test_demonstrate_structured_logging(console, logger):
    """
    Demonstrate structured logging with extra context.
    """

    console.print('\n[bold blue]📊 Demonstrating Structured Logging[/bold blue]')
    console.print('=' * 60)

    # Add extra context to log messages
    extra_context = {'user_id': 12345, 'session_id': 'abc123def456', 'ip_address': '192.168.1.100'}

    logger.info('User login successful', extra=extra_context)

    # Simulate processing with progress updates
    total_items = 100
    for i in range(0, total_items + 1, 25):
        progress = (i / total_items) * 100
        if progress == 100:
            logger.info(
                f'[green]✓[/green] Processing complete: {i}/{total_items} items '
                f'([bold green]{progress:.0f}%[/bold green])'
            )
        elif progress >= 75:
            logger.info(f'Processing: {i}/{total_items} items ([cyan]{progress:.0f}%[/cyan])')
        else:
            logger.debug(f'Processing: {i}/{total_items} items ({progress:.0f}%)')
