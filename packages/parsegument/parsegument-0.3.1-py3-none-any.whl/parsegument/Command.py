from typing import Callable, Union, Any
from .Parameters import Argument, Operand, Flag
import inspect
from .types.ArgDict import ArgDict
from .utils.parser import node_type, parse_operand, convert_string_to_result
from .Node import Node, CommandNode
from .formatting import HelpFormatter

class Command(CommandNode):
    """
    Linked to a function via executable
    Call flags using -flag
    call operands using --operand=value
    """
    parameters: ArgDict

    def __init__(self, name: str, executable: Callable, help: str="") -> None:
        super().__init__(name, help)
        self.parameters = {"args": {}, "kwargs": {}}
        self.executable = executable

    def __len__(self):
        return len(self.parameters["args"]) + len(self.parameters["kwargs"])

    @property
    def length(self):
        return self.__len__()

    @property
    def flatten_params(self):
        return list(self.parameters["args"].values()) + list(self.parameters["kwargs"].values())

    @property
    def _get_help_messages(self) -> str:
        items = list(self.parameters["args"].items()) + list(self.parameters["kwargs"].items())
        max_len = max(len(key) for key, _ in items)
        return "\n".join(f"{key.ljust(max_len*2 + 2)}{value.help}" for key, value in items)

    def add_parameter(self, param: Union[Argument, Operand, Flag]) -> None:
        """defines an argument, operand, or flag to the command"""
        if type(param) == Argument:
            self.parameters["args"][param.name] = param
        else:
            self.parameters["kwargs"][param.name] = param

    def forward(self, nodes:dict[str, list[str]]) -> Any:
        """Converts all arguments in nodes into its defined types, and executes the linked executable"""
        path = nodes["path"]
        exec_path = nodes["exec_path"]
        if HelpFormatter.is_help_message(exec_path):
            return HelpFormatter.format(path, self.help, "Command", self.flatten_params)
        args_length = len(self.parameters["args"])
        args = exec_path[:args_length]
        args = {name:args[idx] for idx, name in enumerate(self.parameters["args"].keys())}
        args = [convert_string_to_result(value, self.parameters["args"][key].param_type) for key, value in args.items()]
        kwargs_strings = exec_path[args_length:]
        kwargs = {}
        for kwarg_string in kwargs_strings:
            type_of_node = node_type(kwarg_string)
            if type_of_node == "Flag":
                kwargs[kwarg_string[1:]] = True
                continue
            elif type_of_node == "Operand":
                name, value = parse_operand(kwarg_string)
                node_arguments = self.parameters["kwargs"][name]
                value = convert_string_to_result(value, node_arguments.param_type)
                kwargs[name] = value
                continue
        return self.executable(*args, **kwargs)
