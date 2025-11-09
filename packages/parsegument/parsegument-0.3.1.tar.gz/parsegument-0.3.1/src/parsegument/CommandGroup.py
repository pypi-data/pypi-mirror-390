from typing import Any
from .BaseGroup import BaseGroup
from .error import NodeDoesNotExist

class CommandGroup(BaseGroup):
    def __init__(self, name: str, help:str="") -> None:
        super().__init__(name, help)
        self.children = {}

    @classmethod
    def _get_commands(cls) -> set[str]:
        return cls._get_methods() - CommandGroup._get_methods()

    def initialise(self) -> None:
        """
        Only use this if you are making a child class of CommandGroup
        This does the same thing as the @BaseGroup.command decorator, but does it for every custom method in the child class
        """
        child_commands = list(self._get_commands())
        methods = [getattr(self, i) for i in child_commands]
        for method in methods:
            self.command()(method)
