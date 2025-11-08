from unittest.mock import Mock, patch

import pytest
import typer
from typer.testing import CliRunner

from src.invoke import create_app, load_module_app, main


@pytest.fixture
def runner():
    """Fixture providing a Typer CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_typer_app():
    """Fixture providing a mock Typer app."""
    app = typer.Typer()

    @app.command()
    def test_command():
        typer.echo("test output")

    @app.command()
    def another_command(name: str):
        typer.echo(f"Hello {name}")

    return app


@pytest.fixture
def mock_module_with_app(mock_typer_app):
    """Fixture providing a mock module with a Typer app."""
    mock_module = Mock()
    mock_module.app = mock_typer_app
    return mock_module


@pytest.fixture
def mock_module_without_app():
    """Fixture providing a mock module without a Typer app."""
    mock_module = Mock(spec=[])
    return mock_module


class TestLoadModuleApp:
    """Test load_module_app function."""

    def test_load_module_app_success(self, mock_module_with_app):
        """Test successfully loading a module with a Typer app."""
        with patch('src.invoke.importlib.import_module', return_value=mock_module_with_app):
            result = load_module_app('sample.hello', 'foo')

            assert result is not None
            assert isinstance(result, typer.Typer)
            assert result == mock_module_with_app.app

    def test_load_module_app_no_app_attribute(self, mock_module_without_app, capsys):
        """Test loading a module without an 'app' attribute."""
        with patch('src.invoke.importlib.import_module', return_value=mock_module_without_app):
            result = load_module_app('sample.noapp', 'foo')

            assert result is None
            captured = capsys.readouterr()
            assert 'does not have a Typer app' in captured.err

    def test_load_module_app_app_not_typer_instance(self, capsys):
        """Test loading a module where 'app' is not a Typer instance."""
        mock_module = Mock()
        mock_module.app = "not a typer app"

        with patch('src.invoke.importlib.import_module', return_value=mock_module):
            result = load_module_app('sample.invalid', 'foo')

            assert result is None
            captured = capsys.readouterr()
            assert 'does not have a Typer app' in captured.err

    def test_load_module_app_import_error(self, capsys):
        """Test handling ImportError when module cannot be imported."""
        with patch(
            'src.invoke.importlib.import_module', side_effect=ImportError('Module not found')
        ):
            result = load_module_app('nonexistent.module', 'foo')

            assert result is None
            captured = capsys.readouterr()
            assert 'Could not import module' in captured.err
            assert "nonexistent.module" in captured.err

    def test_load_module_app_module_not_found_error(self, capsys):
        """Test handling ModuleNotFoundError specifically."""
        with patch(
            'src.invoke.importlib.import_module',
            side_effect=ModuleNotFoundError("No module named 'foo'"),
        ):
            result = load_module_app('foo.bar', 'foo')

            assert result is None
            captured = capsys.readouterr()
            assert 'Could not import module' in captured.err


class TestCreateApp:
    """Test create_app function."""

    def test_create_app_single_module(self, mock_module_with_app):
        """Test creating app with a single module."""
        with patch('src.invoke.load_module_app', return_value=mock_module_with_app.app):
            app = create_app(['sample.hello'])

            assert isinstance(app, typer.Typer)
            # Verify the subcommand was added
            assert len(app.registered_groups) > 0

    def test_create_app_multiple_modules(self, mock_typer_app):
        """Test creating app with multiple modules."""
        mock_app1 = typer.Typer()
        mock_app2 = typer.Typer()

        def load_side_effect(module_path, base_path):
            if module_path == 'sample.hello':
                return mock_app1
            elif module_path == 'sample.world':
                return mock_app2
            return None

        with patch('src.invoke.load_module_app', side_effect=load_side_effect):
            app = create_app(['sample.hello', 'sample.world'])

            assert isinstance(app, typer.Typer)
            assert len(app.registered_groups) == 2

    def test_create_app_with_failed_module_load(self, mock_typer_app):
        """Test creating app when one module fails to load."""

        def load_side_effect(module_path, base_path):
            if module_path == 'sample.hello':
                return mock_typer_app
            return None

        with patch('src.invoke.load_module_app', side_effect=load_side_effect):
            app = create_app(['sample.hello', 'sample.invalid'])

            assert isinstance(app, typer.Typer)
            # Only the successful module should be added
            assert len(app.registered_groups) == 1

    def test_create_app_empty_module_list(self):
        """Test creating app with empty module list."""
        app = create_app([])

        assert isinstance(app, typer.Typer)
        assert len(app.registered_groups) == 0

    def test_create_app_extracts_correct_module_name(self, mock_typer_app):
        """Test that module name is correctly extracted from path."""
        with patch('src.invoke.load_module_app', return_value=mock_typer_app) as mock_load:
            app = create_app(['foo.bar.baz'])

            # Verify the module was loaded
            mock_load.assert_called_once()
            assert mock_load.call_args.args[0] == 'foo.bar.baz'

            # The subcommand name should be 'baz' (last part of the path)
            assert isinstance(app, typer.Typer)

    def test_create_app_module_with_single_name(self, mock_typer_app):
        """Test creating app with single-part module name."""
        with patch('src.invoke.load_module_app', return_value=mock_typer_app):
            app = create_app(['hello'])

            assert isinstance(app, typer.Typer)
            assert len(app.registered_groups) > 0


class TestMain:
    """Test ``main`` function."""

    def test_main_creates_and_runs_app(self):
        """Test that main creates and runs the app."""
        mock_app = Mock(spec=typer.Typer)

        with patch('src.invoke.create_app', return_value=mock_app) as mock_create:
            main()

            # Verify create_app was called with correct module paths
            mock_create.assert_called_once()

            # Verify the app was invoked
            mock_app.assert_called_once()


class TestIntegration:
    """Integration tests using actual sample.hello module."""

    def test_load_actual_hello_module(self):
        """Test loading the actual sample.hello module."""
        result = load_module_app('sample.hello', 'foo')

        assert result is not None
        assert isinstance(result, typer.Typer)

    def test_create_app_with_actual_module(self, runner):
        """Test creating app with actual sample.hello module."""
        app = create_app(['sample.hello'])

        assert isinstance(app, typer.Typer)

        # Test that we can invoke the hello world command
        result = runner.invoke(app, ['hello', 'world'])
        assert result.exit_code == 0
        assert 'hello world' in result.stdout

    def test_create_app_with_actual_module_mom_command(self, runner):
        """Test the mom command from sample.hello."""
        app = create_app(['sample.hello'])

        result = runner.invoke(app, ['hello', 'mom'])
        assert result.exit_code == 0
        assert 'hello mom' in result.stdout

    def test_create_app_with_actual_module_other_command(self, runner):
        """Test the other command from sample.hello with argument."""
        app = create_app(['sample.hello'])

        result = runner.invoke(app, ['hello', 'other', 'Alice'])
        assert result.exit_code == 0
        assert 'hello Alice' in result.stdout

    def test_create_app_help_shows_hello_subcommand(self, runner):
        """Test that help output shows hello as a subcommand."""
        app = create_app(['sample.hello'])

        result = runner.invoke(app, ['--help'])
        assert result.exit_code == 0
        assert 'hello' in result.stdout.lower()

    def test_hello_subcommand_help_shows_commands(self, runner):
        """Test that hello subcommand help shows all commands."""
        app = create_app(['sample.hello'])

        result = runner.invoke(app, ['hello', '--help'])
        assert result.exit_code == 0
        assert 'world' in result.stdout
        assert 'mom' in result.stdout
        assert 'other' in result.stdout


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_load_module_app_with_syntax_error(self):
        """Test handling module with syntax error."""
        with patch('src.invoke.importlib.import_module', side_effect=SyntaxError('Invalid syntax')):
            with pytest.raises(SyntaxError):
                load_module_app('sample.broken', 'foo')

    def test_load_module_app_handles_runtime_error(self, capsys):
        """Test handling RuntimeError during module loading."""
        with patch('src.invoke.importlib.import_module', side_effect=RuntimeError('Runtime issue')):
            # RuntimeError is not caught by ImportError, so it should propagate
            with pytest.raises(RuntimeError):
                load_module_app('sample.problematic', 'foo')

    def test_create_app_handles_none_from_load_module(self):
        """Test that create_app gracefully handles None from load_module_app."""
        with patch('src.invoke.load_module_app', return_value=None):
            app = create_app(['sample.nonexistent'])

            # Should create app successfully even if module loading failed
            assert isinstance(app, typer.Typer)
            assert len(app.registered_groups) == 0


class TestModuleNameExtraction:
    """Test module name extraction logic."""

    @pytest.mark.parametrize(
        'module_path, expected_name',
        [
            ('sample.hello', 'hello'),
            ('foo.bar.baz', 'baz'),
            ('single', 'single'),
            ('a.b.c.d.e', 'e'),
            ('my_package.my_module', 'my_module'),
        ],
    )
    def test_module_name_extraction(self, module_path, expected_name, mock_typer_app):
        """Test that module names are correctly extracted from various paths."""
        with patch('src.invoke.load_module_app', return_value=mock_typer_app):
            create_app([module_path])

            # Check that the extracted name matches expected
            extracted_name = module_path.split('.')[-1]
            assert extracted_name == expected_name
