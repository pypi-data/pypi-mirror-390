import sys
from unittest.mock import patch

import pytest

# Import the appropriate TOML library for testing
if sys.version_info >= (3, 11):
    import tomllib  # noqa: F401
else:
    try:
        import tomli as tomllib  # noqa: F401
    except ImportError:
        pytest.skip('tomli not available', allow_module_level=True)

from src.pyproject import (
    PackageConfig,
    find_pyproject_toml,
    get_package_setting,
    read_package_config,
)


class TestFindPyprojectToml:
    """Test find_pyproject_toml function."""

    def test_find_pyproject_toml_in_current_directory(self, tmp_path):
        """Test finding pyproject.toml in current directory."""
        pyproject_file = tmp_path / 'pyproject.toml'
        pyproject_file.write_text('[tool.foo]\ntimeout = 30')

        result = find_pyproject_toml(tmp_path)
        assert result == pyproject_file

    def test_find_pyproject_toml_in_parent_directory(self, tmp_path):
        """Test finding pyproject.toml in parent directory."""
        pyproject_file = tmp_path / 'pyproject.toml'
        pyproject_file.write_text('[tool.foo]\ntimeout = 30')

        subdir = tmp_path / 'subdir'
        subdir.mkdir()

        result = find_pyproject_toml(subdir)
        assert result == pyproject_file

    def test_find_pyproject_toml_multiple_levels(self, tmp_path):
        """Test finding pyproject.toml multiple levels up."""
        pyproject_file = tmp_path / 'pyproject.toml'
        pyproject_file.write_text('[tool.foo]\ntimeout = 30')

        deep_subdir = tmp_path / 'level1' / 'level2' / 'level3'
        deep_subdir.mkdir(parents=True)

        result = find_pyproject_toml(deep_subdir)
        assert result == pyproject_file

    def test_find_pyproject_toml_not_found(self, tmp_path):
        """Test FileNotFoundError when pyproject.toml is not found."""
        subdir = tmp_path / 'subdir'
        subdir.mkdir()

        with pytest.raises(FileNotFoundError, match='pyproject.toml not found'):
            find_pyproject_toml(subdir)

    @patch('src.pyproject.Path.cwd')
    def test_find_pyproject_toml_default_start_path(self, mock_cwd, tmp_path):
        """Test default start_path uses current working directory."""
        mock_cwd.return_value = tmp_path

        pyproject_file = tmp_path / 'pyproject.toml'
        pyproject_file.write_text('[tool.invoke]\ntimeout = 30')

        result = find_pyproject_toml()
        assert result == pyproject_file

    def test_find_pyproject_toml_resolves_path(self, tmp_path):
        """Test that paths are properly resolved."""
        pyproject_file = tmp_path / 'pyproject.toml'
        pyproject_file.write_text('[tool.invoke]\ntimeout = 30')

        # Use a path with .. to test resolution
        subdir = tmp_path / 'subdir'
        subdir.mkdir()
        path_with_dots = subdir / '..' / 'subdir'

        result = find_pyproject_toml(path_with_dots)
        assert result == pyproject_file


class TestReadInvokeConfig:
    """Test read_package_config function."""

    def test_read_package_config_with_path(self, tmp_path):
        """Test reading package config with explicit path."""
        pyproject_file = tmp_path / 'pyproject.toml'
        content = """[tool.invoke]
timeout = 30
debug = true
tasks_dir = "custom_tasks"
"""
        pyproject_file.write_text(content)

        result = read_package_config('invoke', pyproject_file)
        expected = {'timeout': 30, 'debug': True, 'tasks_dir': 'custom_tasks'}
        assert result == expected

    def test_read_package_config_without_path(self, tmp_path):
        """Test reading package config without explicit path (auto-discovery)."""
        pyproject_file = tmp_path / 'pyproject.toml'
        content = """[tool.invoke]
timeout = 60
"""
        pyproject_file.write_text(content)

        with patch('src.pyproject.find_pyproject_toml', return_value=pyproject_file):
            result = read_package_config('invoke')
            assert result == {'timeout': 60}

    def test_read_package_config_no_tool_section(self, tmp_path):
        """Test reading config with no [tool] section."""
        pyproject_file = tmp_path / 'pyproject.toml'
        content = """[project]
name = "test"
"""
        pyproject_file.write_text(content)

        result = read_package_config('invoke', pyproject_file)
        assert result == {}

    def test_read_package_config_no_invoke_section(self, tmp_path):
        """Test reading config with [tool] but no [tool.invoke] section."""
        pyproject_file = tmp_path / 'pyproject.toml'
        content = """[tool.other]
config = "value"
"""
        pyproject_file.write_text(content)

        result = read_package_config('invoke', pyproject_file)
        assert result == {}

    def test_read_package_config_empty_invoke_section(self, tmp_path):
        """Test reading config with empty [tool.invoke] section."""
        pyproject_file = tmp_path / 'pyproject.toml'
        content = """[tool.invoke]
"""
        pyproject_file.write_text(content)

        result = read_package_config('invoke', pyproject_file)
        assert result == {}

    def test_read_package_config_file_not_found_auto_discovery(self):
        """Test FileNotFoundError when auto-discovery fails."""
        with patch('src.pyproject.find_pyproject_toml', side_effect=FileNotFoundError()):
            with pytest.raises(FileNotFoundError):
                read_package_config('invoke')

    def test_read_package_config_malformed_toml(self, tmp_path):
        """Test handling malformed TOML."""
        pyproject_file = tmp_path / 'pyproject.toml'
        pyproject_file.write_text('[tool.invoke\nmalformed toml')

        with pytest.raises(Exception, match='Error reading .*'):
            read_package_config('invoke', pyproject_file)

    def test_read_package_config_file_permission_error(self, tmp_path):
        """Test handling file permission errors."""
        pyproject_file = tmp_path / 'pyproject.toml'
        pyproject_file.write_text('[tool.invoke]\ntimeout = 30')

        with patch('builtins.open', side_effect=PermissionError('Access denied')):
            with pytest.raises(Exception, match='Error reading .*'):
                read_package_config('invoke', pyproject_file)


class TestGetPackageSetting:
    """Test get_package_setting function."""

    def test_get_package_setting_existing_key(self, tmp_path):
        """Test getting existing setting."""
        pyproject_file = tmp_path / 'pyproject.toml'
        content = """[tool.invoke]
timeout = 45
debug = false
"""
        pyproject_file.write_text(content)

        result = get_package_setting('invoke', 'timeout', pyproject_path=pyproject_file)
        assert result == 45

    def test_get_package_setting_missing_key_with_default(self, tmp_path):
        """Test getting missing setting with default value."""
        pyproject_file = tmp_path / 'pyproject.toml'
        content = """[tool.invoke]
timeout = 45
"""
        pyproject_file.write_text(content)

        result = get_package_setting(
            'invoke', 'missing_key', default='default_value', pyproject_path=pyproject_file
        )
        assert result == 'default_value'

    def test_get_package_setting_missing_key_no_default(self, tmp_path):
        """Test getting missing setting without default value."""
        pyproject_file = tmp_path / 'pyproject.toml'
        content = """[tool.invoke]
timeout = 45
"""
        pyproject_file.write_text(content)

        result = get_package_setting('invoke', 'missing_key', pyproject_path=pyproject_file)
        assert result is None

    def test_get_package_setting_file_not_found_returns_default(self):
        """Test returning default when file is not found."""
        with patch('src.pyproject.read_package_config', side_effect=FileNotFoundError()):
            result = get_package_setting('invoke', 'timeout', default=300)
            assert result == 300

    def test_get_package_setting_exception_returns_default(self, tmp_path):
        """Test returning default when exception occurs."""
        with patch('src.pyproject.read_package_config', side_effect=Exception('Some error')):
            result = get_package_setting('invoke', 'timeout', default=120)
            assert result == 120

    def test_get_package_setting_none_default(self, tmp_path):
        """Test that None default is returned properly."""
        with patch('src.pyproject.read_package_config', side_effect=FileNotFoundError()):
            result = get_package_setting('invoke', 'timeout')
            assert result is None


class TestPackageConfig:
    """Test PackageConfig class."""

    def test_package_config_initialization(self):
        """Test PackageConfig initialization."""
        config = PackageConfig('invoke')
        assert config.pyproject_path is None
        assert config._config is None

    def test_package_config_initialization_with_path(self, tmp_path):
        """Test PackageConfig initialization with path."""
        pyproject_file = tmp_path / 'pyproject.toml'
        config = PackageConfig('invoke', pyproject_file)
        assert config.pyproject_path == pyproject_file
        assert config._config is None

    def test_package_config_lazy_loading(self, tmp_path):
        """Test lazy loading of configuration."""
        pyproject_file = tmp_path / 'pyproject.toml'
        content = """[tool.invoke]
timeout = 30
debug = true
"""
        pyproject_file.write_text(content)

        config = PackageConfig('invoke', pyproject_file)

        # Config should be None initially
        assert config._config is None

        # First access should load the config
        result = config.config
        expected = {'timeout': 30, 'debug': True}
        assert result == expected
        assert config._config == expected

        # Second access should return cached config
        result2 = config.config
        assert result2 is result

    def test_package_config_get_existing_key(self, tmp_path):
        """Test getting existing configuration key."""
        pyproject_file = tmp_path / 'pyproject.toml'
        content = """[tool.invoke]
timeout = 60
tasks_dir = "custom"
"""
        pyproject_file.write_text(content)

        config = PackageConfig('invoke', pyproject_file)
        assert config.get('timeout') == 60
        assert config.get('tasks_dir') == 'custom'

    def test_package_config_get_missing_key(self, tmp_path):
        """Test getting missing configuration key."""
        pyproject_file = tmp_path / 'pyproject.toml'
        content = """[tool.invoke]
timeout = 60
"""
        pyproject_file.write_text(content)

        config = PackageConfig('invoke', pyproject_file)
        assert config.get('missing_key') is None
        assert config.get('missing_key', 'default') == 'default'

    def test_package_config_file_not_found(self):
        """Test behavior when pyproject.toml is not found."""
        with patch('src.pyproject.read_package_config', side_effect=FileNotFoundError()):
            config = PackageConfig('invoke')

            # Should return empty dict when file not found
            assert config.config == {}
            assert config.get('timeout', 300) == 300

    def test_package_config_exception_handling(self):
        """Test behavior when exception occurs during config loading."""
        with patch('src.pyproject.read_package_config', side_effect=Exception('Some error')):
            config = PackageConfig('invoke')

            # Should return empty dict when exception occurs
            assert config.config == {}
            assert config.get('timeout', 300) == 300

    def test_package_config_reload(self, tmp_path):
        """Test reloading configuration."""
        pyproject_file = tmp_path / 'pyproject.toml'
        content1 = """[tool.invoke]
timeout = 30
"""
        pyproject_file.write_text(content1)

        config = PackageConfig('invoke', pyproject_file)

        # Load initial config
        assert config.get('timeout') == 30

        # Modify file
        content2 = """[tool.invoke]
timeout = 60
"""
        pyproject_file.write_text(content2)

        # Config should still be old value (cached)
        assert config.get('timeout') == 30

        # After reload, should get new value
        config.reload()
        assert config.get('timeout') == 60

    def test_package_config_reload_resets_cache(self, tmp_path):
        """Test that reload properly resets the cache."""
        pyproject_file = tmp_path / 'pyproject.toml'
        content = """[tool.invoke]
timeout = 30
"""
        pyproject_file.write_text(content)

        config = PackageConfig('invoke', pyproject_file)

        # Load config
        _ = config.config
        assert config._config is not None

        # Reload should reset cache
        config.reload()
        assert config._config is None
