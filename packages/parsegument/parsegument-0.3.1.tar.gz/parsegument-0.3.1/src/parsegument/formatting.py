from typing import Callable
from string import Template

from parsegument.Node import CommandNode


class HelpFormatter:
    """
    Class used for all Help Message Formatting

    -----
    HelpFormatter.triggers is a list of command parameters that trigger a help message to be returned

    HelpFormatter.schema defines how a help message is formatted:
    {usage} is the path of the command
    {pg_type} is the type of the command parameter (eg Command, CommandGroup, etc)
    {options} returns all valid paths
    """
    triggers = ["-help", "--help", "-h"]
    schema: str = """
-----
Usage: {usage} [OPTIONS]
[TYPE {pg_type}] {description}

[OPTIONS]
{options}
-----
"""

    @classmethod
    def is_help_message(cls, nodes: list[str]):
        return bool([i for i in nodes if i in cls.triggers])

    @classmethod
    def first_node_is_help(cls, nodes: list[str]):
        return nodes[0] in cls.triggers

    @classmethod
    def format_with_schema(cls, usage: str, pg_type: str, description: str, options: str):
        return cls.schema.format(usage=usage, pg_type=pg_type, description=description, options=options)

    @classmethod
    def format(cls, path: list[str], description: str, pg_type: str, options: list[CommandNode]) -> str:
        path = " ".join(path)
        options = "\n".join([f"{i.name}: {i.help}" for i in options])
        return cls.format_with_schema(path, pg_type, description, options)
