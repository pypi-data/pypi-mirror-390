from typing import Any
from abc import ABC, abstractmethod, ABCMeta


class Node:
    def __init__(self, name: str, help: str) -> None:
        self.name = name
        self.help = help

    @property
    def help_message(self) -> str:
        return f"{self.name}: {self.help}"

class CommandNode(Node, metaclass=ABCMeta):
    def __init__(self, name: str, help: str) -> None:
        super().__init__(name, help)

    @abstractmethod
    def forward(self, nodes:list[str]) -> Any:
        raise NotImplementedError