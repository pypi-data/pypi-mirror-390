class ParsegumentError(Exception):
    def __init__(self, message="Unimplemented") -> None:
        self.message = message

class NodeDoesNotExist(ParsegumentError):
    def __init__(self) -> None:
        super().__init__("Argument does not exist")

class ArgumentGroupNotFound(ParsegumentError):
    def __init__(self) -> None:
        super().__init__("Argument group does not exist")

class MultipleChildrenFound(ParsegumentError):
    def __init__(self) -> None:
        super().__init__("Multiple children found")

class ConversionTypeNotFound(ParsegumentError):
    def __init__(self, param_type) -> None:
        super().__init__(f"Attempted to convert string to {param_type}, but was not able to")

class ParameterNotFound(ParsegumentError):
    def __init__(self, name:str) -> None:
        super().__init__(f"Parameter with name: {name} does not exist")

class CommandNotFound(ParsegumentError):
    def __init__(self, name:str) -> None:
        super().__init__(f"Command with name: {name} does not exist")