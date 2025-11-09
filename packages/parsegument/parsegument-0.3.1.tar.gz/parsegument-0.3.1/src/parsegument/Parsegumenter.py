from __future__ import annotations
from typing import Union, Any, Optional

from .Command import Command
from .BaseGroup import BaseGroup
from .Node import CommandNode
from .Parameters import Parameter
from .formatting import HelpFormatter
from .error import NodeDoesNotExist, ArgumentGroupNotFound, MultipleChildrenFound
import shlex
import sys

class Parsegumenter(BaseGroup):
    """
    Child class of BaseGroup
    Essentially acts as an extension of CommandGroup
    """
    def __init__(self, name: str="", prefix: str="", help: str="") -> None:
        super().__init__(name, help)
        self.children = {}
        self.prefix = prefix

    def _check_valid(self, command: list[str]) -> bool:
        """Checks if the first term of a command is valid based on the name and prefix"""
        first = command[0]
        if self.prefix and not first.startswith(self.prefix): return False
        else: first = first[len(self.prefix):]
        if self.name and first != self.name: return False
        else: return True

    @property
    def schema(self) -> dict:
        def iterate(node: Union[CommandNode]):
            if isinstance(node, BaseGroup):
                return {key: iterate(value) for key, value in node.children.items()}
            elif isinstance(node, Command):
                copy = node.parameters["args"].copy()
                copy.update(node.parameters["kwargs"])
                return {key: value.param_type for key, value in copy.items()}
            return None

        return iterate(self)

    def execute(self, command:Union[str, list[str]]) -> Union[Any, None]:
        """Checks if a child with the name of the first list item exists, then executes the child
        It will also automatically check if it is valid with the prefix and name"""
        parsed = shlex.split(command) if isinstance(command, str) else command
        nodes = {"path": [], "exec_path": parsed}
        if not self._check_valid(parsed): return None
        if self.name:
            nodes["path"].append(parsed[0])
            parsed.pop(0)
        value = self.forward(nodes)
        return value

    def run(self) -> Optional[Any]:
        """Reads arguments from the CLI and executes it"""
        args = sys.argv
        if not len(args) > 1:
            return None
        return self.execute(args[1:])




