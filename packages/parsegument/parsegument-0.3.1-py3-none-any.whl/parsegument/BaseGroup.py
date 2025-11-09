from __future__ import annotations
from typing import Union, Callable, TYPE_CHECKING, Any
from inspect import signature
import functools

from .formatting import HelpFormatter
from .utils.convert_params import convert_param
from .Command import Command
from .Node import CommandNode

if TYPE_CHECKING:
    from .CommandGroup import CommandGroup


class BaseGroup(CommandNode):
    def __init__(self, name:str, help: str=""):
        super().__init__(name, help)
        self.children: dict[str, Union[Command, CommandGroup]] = {}
        self._on_call = []

    def __len__(self):
        return len(self.children)

    @property
    def length(self):
        return self.__len__()

    @classmethod
    def _get_methods(cls) -> set[str]:
        return set([i for i in dir(cls) if i[0] != "_"])

    @property
    def _get_help_messages(self) -> str:
        max_len = max(len(key) for key, _ in self.children.items())
        return "\n".join(f"{key.ljust(max_len*2 + 2)}{value.help}" for key, value in self.children.items())

    def _execute_on_calls(self):
        for command in self._on_call:
            command()

    def add_child(self, child: Union[Command, CommandGroup]) -> bool:
        """Add a Command or CommandGroup as a child"""
        if child.name in [i.name for i in self.children.values()]:
            return False
        self.children[child.name] = child
        return True

    def command(self, name:str=None, help: str=None) -> Callable:
        """A Decorator that automatically creates a command, and adds it as a child"""

        def command_wrapper(func):
            orig = getattr(func, "__wrapped__", func)
            params = signature(func).parameters
            func_name = func.__name__
            command_object = Command(name=func_name, executable=func, help=help)
            for key, param in params.items():
                converted = convert_param(param)
                command_object.add_parameter(converted)
            if name:
                command_object.name = name
            self.add_child(command_object)

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            new_params = getattr(func, "__parameters__", None) or getattr(orig, "__parameters__", None)
            if new_params:
                for arg in new_params["args"].values():
                    command_object.parameters["args"][arg.name] = arg
                for kwarg in new_params["kwargs"].values():
                    command_object.parameters["kwargs"][kwarg.name] = kwarg
            wrapper.command = command_object
            orig.command = command_object

            return wrapper

        return command_wrapper

    def on_call(self, func: Callable) -> Callable:
        """Calls a function when the command is used"""

        if func not in self._on_call:
            self._on_call.append(func)

        def command_wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return command_wrapper

    def forward(self, nodes: dict[str, list[str]]) -> Any:
        path = nodes["path"]
        exec_path = nodes["exec_path"]

        if not exec_path or HelpFormatter.first_node_is_help(exec_path):
            return HelpFormatter.format(path, self.help, self.__class__.__name__, self.children.values())
        if not HelpFormatter.is_help_message(exec_path):
            self._execute_on_calls()
        child = self.children.get(exec_path[0])
        nodes["path"].append(nodes["exec_path"][0])
        nodes["exec_path"].pop(0)
        if not child:
            if type(child) == Command and not child.parameters:
                return None
            elif isinstance(child, BaseGroup) and not child.children:
                return None
        return child.forward(nodes)


