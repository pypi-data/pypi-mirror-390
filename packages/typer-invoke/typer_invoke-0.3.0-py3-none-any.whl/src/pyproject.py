import sys
from pathlib import Path
from typing import Any, cast

# Import the appropriate TOML library
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        raise ImportError('tomli is required for Python < 3.11. Install with: pip install tomli')


def find_pyproject_toml(start_path: str | Path | None = None) -> Path:
    """
    Find ``pyproject.toml`` by walking up the directory tree from start_path.

    :param start_path: Directory to start searching from. Defaults to current working directory.
    :returns: Path to ``pyproject.toml``.
    :raises FileNotFoundError: If ``pyproject.toml`` is not found.
    """
    if start_path is None:
        start_path = Path.cwd()

    current = Path(start_path).resolve()

    # Walk up the directory tree.
    for parent in [current] + list(current.parents):
        pyproject_path = parent / 'pyproject.toml'
        if pyproject_path.exists():
            return pyproject_path

    raise FileNotFoundError('pyproject.toml not found.')


def read_package_config(
    package_name: str, pyproject_path: str | Path | None = None
) -> dict[str, Any]:
    """
    Read package configuration from pyproject.toml.

    :param package_name: Name of the package to read configuration for.
    :param pyproject_path: Path to pyproject.toml. If None, searches for it automatically.
    :returns: Dictionary containing package configuration, empty dict if not found.

    :raises FileNotFoundError: If ``pyproject.toml`` is not found.
    :raises tomllib.TOMLDecodeError: If ``pyproject.toml`` is malformed.
    """
    if pyproject_path is None:
        pyproject_path = find_pyproject_toml()

    if pyproject_path is None:
        raise FileNotFoundError(
            'pyproject.toml not found in current directory or any parent directory'
        )

    try:
        with open(pyproject_path, 'rb') as f:
            data = tomllib.load(f)

        # Extract package-specific configuration.
        return cast(dict[str, Any], data.get('tool', {}).get(package_name, {}))

    except Exception as e:
        raise Exception(f'Error reading {pyproject_path}: {e}')


def get_package_setting(
    package_name: str,
    key: str,
    default: Any = None,
    pyproject_path: str | Path | None = None,
) -> Any:
    """
    Get a specific package setting from pyproject.toml.

    :param package_name: Name of the package whose section under ``[tool]`` to read.
    :param key: Configuration key to retrieve.
    :param default: Default value if key is not found.
    :param pyproject_path: Path to ``pyproject.toml``.
    :returns: The configuration value or default.
    """
    try:
        config = read_package_config(package_name, pyproject_path)
        return config.get(key, default)
    except (FileNotFoundError, Exception):
        return default


# Utility class, alternative to calling ``read_package_config`` directly.
class PackageConfig:
    """
    Configuration manager for package settings from ``pyproject.toml``.
    """

    def __init__(self, package: str, pyproject_path: str | Path | None = None):
        """
        Initialize ``PackageConfig``.

        :param package: Name of the package. Will be used to find the section in ``pyproject.toml``.
        :param pyproject_path: Path to ``pyproject.toml``.
        """
        self.package = package
        self.pyproject_path = pyproject_path
        self._config: dict[str, Any] | None = None

    @property
    def config(self) -> dict[str, Any]:
        """
        Lazy-load configuration.

        :returns: Dictionary containing package configuration.
        """
        if self._config is None:
            try:
                self._config = read_package_config(self.package, self.pyproject_path)
            except (FileNotFoundError, Exception):
                self._config = {}
        return self._config

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        :param key: Configuration key to retrieve.
        :param default: Default value if key is not found.
        :returns: The configuration value or default.
        """
        return self.config.get(key, default)

    def reload(self) -> None:
        """
        Reload configuration from file.
        """
        self._config = None
