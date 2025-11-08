from unittest.mock import Mock

import pytest
import typer
from rich.console import Group

from src.typer_docs import (
    _extract_command_info,
    _extract_group_info,
    _extract_info,
    _Info,
    _Node,
    _padding_level,
    build_typer_help,
    clean_text,
    extract_typer_info,
)


@pytest.fixture
def sample_info():
    """Fixture providing a sample _Info object."""
    return _Info(name='test-command', help='Test command description')


@pytest.fixture
def sample_node(sample_info):
    """Fixture providing a sample _Node object."""
    return _Node(parent=None, info=sample_info)


@pytest.fixture
def command_info_with_short_help():
    """Fixture providing a CommandInfo with short_help."""
    command = Mock(spec=['short_help', 'help', 'callback', 'name', 'hidden'])
    command.short_help = '  Short help text  '
    command.help = 'Long help text\nWith multiple lines'
    command.name = 'my-command'
    command.callback = None
    command.hidden = False
    return command


@pytest.fixture
def command_info_with_help():
    """Fixture providing a CommandInfo with help but no short_help."""
    command = Mock(spec=['short_help', 'help', 'callback', 'name', 'hidden'])
    command.short_help = None
    command.help = '  First line of help\nSecond line  '
    command.name = 'test-cmd'
    command.callback = None
    command.hidden = False
    return command


@pytest.fixture
def command_info_with_callback_doc():
    """Fixture providing a CommandInfo with callback docstring only."""

    def callback_func():
        """Callback docstring\nWith multiple lines"""
        pass

    command = Mock(spec=['short_help', 'help', 'callback', 'name', 'hidden'])
    command.short_help = None
    command.help = None
    command.callback = callback_func
    command.name = 'callback-cmd'
    command.hidden = False
    return command


@pytest.fixture
def command_info_no_help():
    """Fixture providing a CommandInfo with no help text."""
    command = Mock(spec=['short_help', 'help', 'callback', 'name', 'hidden'])
    command.short_help = None
    command.help = None
    command.callback = None
    command.name = 'no-help'
    command.hidden = False
    return command


@pytest.fixture
def command_info_no_name():
    """Fixture providing a CommandInfo with no name but has callback."""

    def my_callback_function():
        """Callback doc"""
        pass

    command = Mock(spec=['short_help', 'help', 'callback', 'name', 'hidden'])
    command.short_help = 'Command help'
    command.help = None
    command.callback = my_callback_function
    command.name = None
    command.hidden = False
    return command


@pytest.fixture
def typer_info_with_typer_instance():
    """Fixture providing a TyperInfo with typer_instance."""
    typer_instance = typer.Typer(help='Typer instance help')

    group = Mock(spec=['short_help', 'help', 'callback', 'name', 'hidden', 'typer_instance'])
    group.short_help = None
    group.help = None
    group.callback = None
    group.name = 'group-name'
    group.typer_instance = typer_instance
    group.hidden = False
    return group


@pytest.fixture
def simple_typer_app():
    """Fixture providing a simple Typer app with commands."""
    app = typer.Typer(help='Main app')

    @app.command()
    def command1():
        """First command help"""
        pass

    @app.command()
    def command2(name: str):
        """Second command help"""
        pass

    return app


@pytest.fixture
def nested_typer_app():
    """Fixture providing a Typer app with nested groups."""
    app = typer.Typer(help='Main app')

    @app.command()
    def root_command():
        """Root level command"""
        pass

    sub_app = typer.Typer(help='Sub app help')

    @sub_app.command()
    def sub_command():
        """Sub command help"""
        pass

    app.add_typer(sub_app, name='sub', help='Subgroup')

    return app


@pytest.fixture
def typer_app_with_hidden():
    """Fixture providing a Typer app with hidden commands and groups."""
    app = typer.Typer(help='Main app')

    @app.command()
    def visible_command():
        """Visible command"""
        pass

    @app.command(hidden=True)
    def hidden_command():
        """Hidden command"""
        pass

    sub_app = typer.Typer(help='Visible sub app')

    @sub_app.command()
    def sub_cmd():
        """Sub command"""
        pass

    app.add_typer(sub_app, name='visible-sub')

    hidden_sub_app = typer.Typer(help='Hidden sub app')

    @hidden_sub_app.command()
    def hidden_sub_cmd():
        """Hidden sub command"""
        pass

    app.add_typer(hidden_sub_app, name='hidden-sub', hidden=True)

    return app


class TestInfo:
    """Test _Info dataclass."""

    def test_info_creation(self):
        """Test creating an _Info object."""
        info = _Info(name='test', help='Test help')

        assert info.name == 'test'
        assert info.help == 'Test help'

    def test_info_empty_values(self):
        """Test creating an _Info object with empty values."""
        info = _Info(name='', help='')

        assert info.name == ''
        assert info.help == ''


class TestNode:
    """Test _Node dataclass."""

    def test_node_creation(self, sample_info):
        """Test creating a _Node object."""
        node = _Node(parent=None, info=sample_info)

        assert node.parent is None
        assert node.info == sample_info
        assert node.commands_infos == []
        assert node.children == []

    def test_node_with_parent(self, sample_info):
        """Test creating a child node with a parent."""
        parent_node = _Node(parent=None, info=sample_info)
        child_info = _Info(name='child', help='Child help')
        child_node = _Node(parent=parent_node, info=child_info)

        assert child_node.parent == parent_node
        assert child_node.info.name == 'child'

    def test_node_with_commands(self, sample_info):
        """Test adding commands to a node."""
        node = _Node(parent=None, info=sample_info)
        cmd_info = _Info(name='cmd1', help='Command 1')
        node.commands_infos.append(cmd_info)

        assert len(node.commands_infos) == 1
        assert node.commands_infos[0].name == 'cmd1'

    def test_node_with_children(self, sample_info):
        """Test adding children to a node."""
        parent_node = _Node(parent=None, info=sample_info)
        child_info = _Info(name='child', help='Child help')
        child_node = _Node(parent=parent_node, info=child_info)
        parent_node.children.append(child_node)

        assert len(parent_node.children) == 1
        assert parent_node.children[0] == child_node


class TestExtractInfo:
    """Test _extract_info function."""

    def test_extract_info_with_short_help(self, command_info_with_short_help):
        """Test extracting info when short_help is present."""
        info = _extract_info(command_info_with_short_help)

        assert info.name == 'my-command'
        assert info.help == 'Short help text'

    def test_extract_info_with_help(self, command_info_with_help):
        """Test extracting info when help is present but not short_help."""
        info = _extract_info(command_info_with_help)

        assert info.name == 'test-cmd'
        assert info.help == 'First line of help'

    def test_extract_info_with_callback_doc(self, command_info_with_callback_doc):
        """Test extracting info from callback docstring."""
        info = _extract_info(command_info_with_callback_doc)

        assert info.name == 'callback-cmd'
        assert info.help == 'Callback docstring'

    def test_extract_info_no_help(self, command_info_no_help):
        """Test extracting info when no help is available."""
        info = _extract_info(command_info_no_help)

        assert info.name == 'no-help'
        assert info.help == ''

    def test_extract_info_no_name(self, command_info_no_name):
        """Test extracting info when name is None but callback exists."""
        info = _extract_info(command_info_no_name)

        assert info.name == 'my-callback-function'
        assert info.help == 'Command help'

    def test_extract_info_no_name_no_callback(self):
        """Test extracting info when both name and callback are missing."""
        command = Mock(spec=['short_help', 'help', 'callback', 'name'])
        command.short_help = 'Help text'
        command.help = None
        command.callback = None
        command.name = None

        info = _extract_info(command)

        assert info.name == ''
        assert info.help == 'Help text'

    def test_extract_info_empty_help_string(self):
        """Test extracting info when help is an empty string."""
        command = Mock(spec=['short_help', 'help', 'callback', 'name'])
        command.short_help = None
        command.help = '   '
        command.callback = None
        command.name = 'test'

        info = _extract_info(command)

        assert info.name == 'test'
        assert info.help == ''

    def test_extract_info_callback_with_empty_doc(self):
        """Test extracting info when callback has empty docstring."""

        def callback_func():
            """ """
            pass

        command = Mock(spec=['short_help', 'help', 'callback', 'name'])
        command.short_help = None
        command.help = None
        command.callback = callback_func
        command.name = 'test'

        info = _extract_info(command)

        assert info.name == 'test'
        assert info.help == ''


class TestExtractCommandInfo:
    """Test _extract_command_info function."""

    def test_extract_command_info(self, command_info_with_short_help):
        """Test extracting command info."""
        info = _extract_command_info(command_info_with_short_help)

        assert isinstance(info, _Info)
        assert info.name == 'my-command'
        assert info.help == 'Short help text'


class TestExtractGroupInfo:
    """Test _extract_group_info function."""

    def test_extract_group_info_with_help(self, command_info_with_short_help):
        """Test extracting group info when help is present."""
        info = _extract_group_info(command_info_with_short_help)

        assert isinstance(info, _Info)
        assert info.name == 'my-command'
        assert info.help == 'Short help text'

    def test_extract_group_info_with_typer_instance(self, typer_info_with_typer_instance):
        """Test extracting group info with typer_instance fallback."""
        info = _extract_group_info(typer_info_with_typer_instance)

        assert isinstance(info, _Info)
        assert info.name == 'group-name'
        assert info.help == 'Typer instance help'

    def test_extract_group_info_no_typer_instance(self, command_info_no_help):
        """Test extracting group info without typer_instance."""
        info = _extract_group_info(command_info_no_help)

        assert isinstance(info, _Info)
        assert info.name == 'no-help'
        assert info.help == ''


class TestExtractTyperInfo:
    """Test extract_typer_info function."""

    def test_extract_simple_app(self, simple_typer_app):
        """Test extracting info from a simple app with commands."""
        node = extract_typer_info(simple_typer_app)

        assert isinstance(node, _Node)
        assert node.parent is None
        assert node.info.help == 'Main app'
        assert len(node.commands_infos) == 2
        assert len(node.children) == 0

        # Check command names
        command_names = {cmd.name for cmd in node.commands_infos}
        assert 'command1' in command_names
        assert 'command2' in command_names

    def test_extract_nested_app(self, nested_typer_app):
        """Test extracting info from a nested app."""
        node = extract_typer_info(nested_typer_app)

        assert isinstance(node, _Node)
        assert len(node.commands_infos) == 1
        assert node.commands_infos[0].name == 'root-command'
        assert len(node.children) == 1

        # Check child node
        child = node.children[0]
        assert child.parent == node
        assert child.info.name == 'sub'
        assert len(child.commands_infos) == 1
        assert child.commands_infos[0].name == 'sub-command'

    def test_extract_with_hidden_items(self, typer_app_with_hidden):
        """Test that hidden commands and groups are excluded."""
        node = extract_typer_info(typer_app_with_hidden)

        # Only visible command should be included
        assert len(node.commands_infos) == 1
        assert node.commands_infos[0].name == 'visible-command'

        # Only visible subgroup should be included
        assert len(node.children) == 1
        assert node.children[0].info.name == 'visible-sub'

    def test_extract_with_provided_info(self, simple_typer_app, sample_info):
        """Test extracting with provided info parameter."""
        node = extract_typer_info(simple_typer_app, info=sample_info)

        assert node.info == sample_info
        assert node.info.name == 'test-command'
        assert node.info.help == 'Test command description'

    def test_extract_with_parent(self, simple_typer_app, sample_node):
        """Test extracting with parent node."""
        node = extract_typer_info(simple_typer_app, parent=sample_node)

        assert node.parent == sample_node

    def test_extract_empty_app(self):
        """Test extracting info from an empty app."""
        app = typer.Typer(help='Empty app')
        node = extract_typer_info(app)

        assert len(node.commands_infos) == 0
        assert len(node.children) == 0


class TestPaddingLevel:
    """Test _padding_level function."""

    def test_padding_level_zero(self):
        """Test padding for level 0."""
        assert _padding_level(0) == 0

    def test_padding_level_one(self):
        """Test padding for level 1."""
        assert _padding_level(1) == 2

    def test_padding_level_multiple(self):
        """Test padding for various levels."""
        assert _padding_level(2) == 4
        assert _padding_level(3) == 6
        assert _padding_level(5) == 10


class TestCleanText:
    """Test clean_text function."""

    def test_clean_text_with_double_backticks(self):
        """Test cleaning text with double backticks."""
        result = clean_text('This is ``code`` example')
        assert result == 'This is `code` example'

    def test_clean_text_multiple_occurrences(self):
        """Test cleaning text with multiple double backticks."""
        result = clean_text('``foo`` and ``bar``')
        assert result == '`foo` and `bar`'

    def test_clean_text_no_backticks(self):
        """Test cleaning text without double backticks."""
        result = clean_text('Normal text')
        assert result == 'Normal text'

    def test_clean_text_single_backticks(self):
        """Test that single backticks are preserved."""
        result = clean_text('This is `code` example')
        assert result == 'This is `code` example'

    def test_clean_text_empty_string(self):
        """Test cleaning empty string."""
        result = clean_text('')
        assert result == ''


class TestBuildTyperHelp:
    """Test build_typer_help function."""

    def test_build_help_root_level(self, sample_node):
        """Test building help for root level node."""
        group = build_typer_help(sample_node, level=0)

        assert isinstance(group, Group)
        assert len(group.renderables) > 0

    def test_build_help_with_commands(self, simple_typer_app):
        """Test building help with commands."""
        node = extract_typer_info(simple_typer_app)
        group = build_typer_help(node)

        assert isinstance(group, Group)
        # Should have node text + 2 commands
        assert len(group.renderables) == 3

    def test_build_help_nested(self, nested_typer_app):
        """Test building help with nested groups."""
        node = extract_typer_info(nested_typer_app)
        group = build_typer_help(node)

        assert isinstance(group, Group)
        # Should have: root node text, root command, and nested group (which itself is a Group)
        assert len(group.renderables) == 3

    def test_build_help_level_one(self):
        """Test building help for level 1 node (group)."""
        info = _Info(name='subgroup', help='Subgroup help')
        node = _Node(parent=None, info=info)
        group = build_typer_help(node, level=1)

        assert isinstance(group, Group)

    def test_build_help_with_double_backticks(self):
        """Test that double backticks are cleaned in help text."""
        info = _Info(name='test', help='Help with ``code``')
        cmd_info = _Info(name='cmd', help='Command with ``more code``')
        node = _Node(parent=None, info=info, commands_infos=[cmd_info])

        group = build_typer_help(node)

        assert isinstance(group, Group)
        # Verify the group is created (actual text cleaning is tested in TestCleanText)
        assert len(group.renderables) == 2

    def test_build_help_empty_node(self):
        """Test building help for node without commands or children."""
        info = _Info(name='empty', help='Empty node')
        node = _Node(parent=None, info=info)

        group = build_typer_help(node)

        assert isinstance(group, Group)
        # Should only have the node text
        assert len(group.renderables) == 1

    def test_build_help_preserves_structure(self, nested_typer_app):
        """Test that nested structure is preserved in output."""
        node = extract_typer_info(nested_typer_app)
        group = build_typer_help(node)

        # Verify root has child groups
        assert any(isinstance(r, Group) for r in group.renderables)

    @pytest.mark.parametrize('level', [0, 1, 2, 3])
    def test_build_help_different_levels(self, level):
        """Test building help at different nesting levels."""
        info = _Info(name=f'level-{level}', help='Help text')
        node = _Node(parent=None, info=info)

        group = build_typer_help(node, level=level)

        assert isinstance(group, Group)


class TestIntegration:
    """Integration tests combining multiple functions."""

    def test_full_extraction_and_build(self, nested_typer_app):
        """Test complete flow from extraction to building help."""
        node = extract_typer_info(nested_typer_app)
        group = build_typer_help(node)

        assert isinstance(node, _Node)
        assert isinstance(group, Group)
        assert len(group.renderables) > 0

    def test_complex_nested_structure(self):
        """Test with deeply nested structure."""
        app = typer.Typer(help='Root app')

        @app.command()
        def root_cmd():
            """Root command"""
            pass

        level1 = typer.Typer(help='Level 1')

        @level1.command()
        def level1_cmd():
            """Level 1 command"""
            pass

        level2 = typer.Typer(help='Level 2')

        @level2.command()
        def level2_cmd():
            """Level 2 command"""
            pass

        level1.add_typer(level2, name='level2')
        app.add_typer(level1, name='level1')

        node = extract_typer_info(app)
        group = build_typer_help(node)

        # Verify structure
        assert len(node.commands_infos) == 1
        assert len(node.children) == 1
        assert len(node.children[0].children) == 1
        assert isinstance(group, Group)
