import importlib
import sys

import typer

from .logging_rich import logger


def get_config() -> dict:
    """Retrieve config from ``pyproject.toml``."""
    from .pyproject import read_package_config

    section_name = 'typer-invoke'
    key = 'modules'

    try:
        config = read_package_config(section_name)
    except Exception as e:
        raise ValueError(
            f'Could not read invoke configuration from [b]pyproject.toml[/b]. '
            f'{type(e).__name__}: {e}'
        )

    if not config:
        raise ValueError(
            f'Could not read invoke configuration from [b]pyproject.toml[/b], '
            f'in section [b]{section_name}[/b].',
        )

    if key not in config:
        raise ValueError(
            f'Could not find [b]{key}[/b] key in invoke configuration from [b]pyproject.toml[/b], '
            f'in section [b]{section_name}[/b].',
        )

    return config


def load_module_app(module_path: str, base_path: str) -> typer.Typer | None:
    """Load a Typer app from a module path like 'sample.hello'."""
    import sys

    try:
        # Add base_path to sys.path if not already present
        if base_path not in sys.path:
            sys.path.insert(0, base_path)

        module = importlib.import_module(module_path)
        if hasattr(module, 'app') and isinstance(module.app, typer.Typer):
            return module.app
        else:
            typer.echo(
                f'Warning: Module `{module_path}` does not have a Typer app instance named `app`',
                err=True,
            )
            return None
    except ImportError as e:
        typer.echo(f'Could not import module `{module_path}`: {e}', err=True)
        return None


def create_app(module_paths: list[str], **typer_kwargs) -> typer.Typer:
    """Create a main Typer app with subcommands from specified modules."""
    from .pyproject import find_pyproject_toml

    app = typer.Typer(**typer_kwargs)

    @app.command(name='help-full', hidden=True, help='Show full help.')
    def show_full_help():
        from rich.console import Console

        from .typer_docs import build_typer_help, extract_typer_info

        typer_info = extract_typer_info(app)
        help_text = build_typer_help(typer_info)
        console = Console()
        console.print(help_text)

    base_path = str(find_pyproject_toml().parent)
    for module_path in module_paths:
        # Extract the module name (last part of the path) to use as subcommand name.
        module_name = module_path.split('.')[-1]

        # Load the module's Typer app
        module_app = load_module_app(module_path, base_path)

        if module_app:
            # Add the module's app as a subcommand group
            app.add_typer(module_app, name=module_name)

    return app


def main():
    """
    Entry point for the invoke CLI.

    Retrieves modules to import from ``pyproject.toml`` and creates a main Typer app.
    """
    try:
        config = get_config()
    except ValueError as e:
        logger.error(e)
        sys.exit(1)
    else:
        app = create_app(module_paths=config['modules'])
        app()


if __name__ == '__main__':
    main()
