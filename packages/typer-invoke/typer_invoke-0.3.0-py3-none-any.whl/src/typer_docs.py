from dataclasses import dataclass, field
from typing import Optional

import typer
from rich.console import Group
from rich.padding import Padding
from rich.text import Text
from typer.models import CommandInfo, TyperInfo


@dataclass
class _Info:
    name: str
    help: str


@dataclass
class _Node:
    """
    Node in a tree.

    A node represents a typer group, which contains commands and subgroups.
    """

    parent: Optional['_Node']  # `None` for root.
    info: _Info
    commands_infos: list[_Info] = field(default_factory=list)
    children: list['_Node'] = field(default_factory=list)


def _extract_info(info: CommandInfo | TyperInfo) -> _Info:
    # Help
    if info.short_help:
        help_ = info.short_help.strip()
    elif info.help:
        lines = info.help.strip().splitlines()
        help_ = lines[0] if lines else ''
    elif info.callback and info.callback.__doc__:
        lines = info.callback.__doc__.strip().splitlines()
        help_ = lines[0] if lines else ''
    else:
        help_ = ''

    # Name
    if info.name:
        name = info.name
    elif getattr(info, 'callback', None):
        name = str(info.callback.__name__).replace('_', '-')  # type: ignore
    else:
        name = ''

    return _Info(name=name, help=help_)


def _extract_command_info(command: CommandInfo) -> _Info:
    return _extract_info(command)


def _extract_group_info(group: TyperInfo) -> _Info:
    group_info = _extract_info(group)
    if not group_info.help and getattr(group, 'typer_instance', None):
        group_info.help = _extract_info(group.typer_instance.info).help  # type: ignore

    return group_info


def extract_typer_info(
    typer_obj: typer.Typer, parent: _Node | None = None, info: _Info | None = None
) -> _Node:
    """
    Extract information from a Typer app and its sub-apps recursively.

    This function traverses a Typer application and extracts all commands and
    subgroups (nested Typer instances) into a tree structure. It processes both
    registered commands and registered groups, filtering out hidden items.

    :param typer_obj: The Typer application instance to extract information from.
    :param parent: The parent node in the tree structure, or ``None`` for the root node.
    :param info: Pre-extracted information for this node, or ``None`` to extract from ``typer_obj``.

    :returns: A node representing this Typer app with all its commands and sub-apps.
    """
    node = _Node(parent=parent, info=info or _extract_info(typer_obj.info))

    for command in typer_obj.registered_commands:
        if not command.hidden:
            node.commands_infos.append(_extract_command_info(command))
    for group in typer_obj.registered_groups:
        if not group.hidden:
            # Can extract more info from the Group at this level
            # so extracting here and passing that info to the recursive function
            extracted_group_info = _extract_group_info(group)
            new_node = extract_typer_info(group.typer_instance, node, extracted_group_info)  # type: ignore
            node.children.append(new_node)

    return node


def _padding_level(level: int) -> int:
    return level * 2


def clean_text(text: str) -> str:
    return text.replace('``', '`')


def build_typer_help(node: _Node, level: int = 0) -> Group:
    """
    Build a rich text representation of a Typer app's help information.

    This function recursively builds a formatted help display for a Typer application tree.
    It creates a hierarchical view showing the app/group name, its help text, all commands
    within it, and all nested subgroups.
    The display uses indentation and color coding to distinguish between different levels
    and types of elements.

    :param node: The tree node representing a Typer app or group to format.
    :param level: The depth level in the tree hierarchy (0 for root app, increments for
        each nested group). Defaults to 0.

    :returns: A Rich Group object containing the formatted help text with proper indentation
        and styling for the node, its commands, and all children.
    """
    # Section
    if level == 0:  # App info
        style_name = 'bold yellow'
        style_info = 'bold yellow'
    else:  # Typer group info
        style_name = 'bold cyan'
        style_info = 'not bold cyan'
    node_text = Text((node.info.name or '').ljust(20), style=style_name) + Text(
        clean_text(node.info.help), style=style_info
    )
    node_padding = Padding(node_text, (0, 0, 0, _padding_level(level)))

    # Commands
    command_paddings = []
    for command_info in node.commands_infos:
        command_text = Text.from_markup(
            f'[b]{command_info.name.ljust(20)}[/b]{clean_text(command_info.help)}'
        )
        command_padding = Padding(command_text, (0, 0, 0, _padding_level(level + 1)))
        command_paddings.append(command_padding)

    # Subsections
    children_paddings = []
    for child in node.children:
        children_paddings.append(build_typer_help(child, level + 1))

    return Group(node_padding, *command_paddings, *children_paddings)
