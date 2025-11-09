from .Node import Node

class Parameter(Node):
    """Base Parameter class"""
    def __init__(self, name: str, param_type: type, help: str= "") -> None:
        super().__init__(name, help)
        self.param_type = param_type or str

class Argument(Parameter):
    """A Compulsory Argument"""
    def __init__(self, name: str, param_type: type=str, help: str= "") -> None:
        super().__init__(name, param_type, help)

class Flag(Parameter):
    """An optional boolean kwarg"""
    def __init__(self, name:str, help: str="") -> None:
        super().__init__(name, bool, help)

class Operand(Parameter):
    """Any keyword Argument"""
    def __init__(self, name: str, param_type:type=str, help: str= "") -> None:
        super().__init__(name, param_type, help)

